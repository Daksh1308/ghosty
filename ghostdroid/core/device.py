import subprocess
import re
import time
from typing import Optional, Dict, List, Any
from datetime import datetime


class ADBDevice:
    def __init__(self, serial: str):
        self.serial = serial
        self.info: Dict[str, Any] = {}
        self._refresh()

    def _run_adb(self, cmd: str, timeout: int = 10) -> str:
        try:
            serial_cmd = f"-s {self.serial} " if self.serial else ""
            full_cmd = f"adb {serial_cmd}{cmd}"
            result = subprocess.run(
                full_cmd, shell=True, capture_output=True,
                text=True, timeout=timeout
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return ""
        except Exception:
            return ""

    def _refresh(self):
        props = self._run_adb("shell getprop")
        batt = self._run_adb("shell dumpsys battery")
        self.info = {
            "serial": self.serial,
            "model": self._extract_prop(props, "ro.product.model"),
            "manufacturer": self._extract_prop(props, "ro.product.manufacturer"),
            "android_version": self._extract_prop(props, "ro.build.version.release"),
            "api_level": self._extract_prop(props, "ro.build.version.sdk"),
            "build": self._extract_prop(props, "ro.build.display.id"),
            "security_patch": self._extract_prop(props, "ro.build.version.security_patch"),
            "fingerprint": self._extract_prop(props, "ro.build.fingerprint"),
            "battery_level": self._extract_battery(batt),
            "battery_status": self._extract_battery_status(batt),
            "usb_debugging": self._check_usb_debugging(),
            "cpu_abi": self._extract_prop(props, "ro.product.cpu.abi"),
            "total_ram": self._get_ram(),
            "resolution": self._get_resolution(),
            "hostname": self._extract_prop(props, "net.hostname"),
            "last_seen": datetime.now().isoformat(),
        }

    def _extract_prop(self, props: str, key: str) -> str:
        match = re.search(rf"\[{key}\]:\s*\[([^\]]+)\]", props)
        return match.group(1).strip() if match else "Unknown"

    def _extract_battery(self, output: str) -> int:
        match = re.search(r"level:\s*(\d+)", output)
        return int(match.group(1)) if match else 0

    def _extract_battery_status(self, output: str) -> str:
        status_map = {1: "Unknown", 2: "Charging", 3: "Discharging",
                       4: "Not charging", 5: "Full"}
        match = re.search(r"status:\s*(\d+)", output)
        status_code = int(match.group(1)) if match else 1
        return status_map.get(status_code, "Unknown")

    def _check_usb_debugging(self) -> bool:
        result = self._run_adb("shell settings get global adb_enabled")
        return result.strip() == "1"

    def _get_ram(self) -> str:
        result = self._run_adb("shell cat /proc/meminfo | grep MemTotal")
        match = re.search(r"(\d+)", result)
        if match:
            kb = int(match.group(1))
            return f"{kb // 1024} MB"
        return "Unknown"

    def _get_resolution(self) -> str:
        result = self._run_adb("shell wm size")
        match = re.search(r"Physical size:\s*(\d+x\d+)", result)
        return match.group(1) if match else "Unknown"

    def get_property(self, key: str, default: str = "Unknown") -> str:
        return self.info.get(key, default)

    def get_installed_packages(self) -> List[str]:
        result = self._run_adb("shell pm list packages -3")
        return [p.replace("package:", "").strip() for p in result.split("\n") if p]

    def get_dangerous_permissions(self) -> List[Dict]:
        packages = self.get_installed_packages()
        dangerous = []
        dangerous_perms = [
            "CAMERA", "RECORD_AUDIO", "READ_CONTACTS", "ACCESS_FINE_LOCATION",
            "ACCESS_COARSE_LOCATION", "READ_SMS", "RECEIVE_SMS", "SEND_SMS",
            "READ_CALL_LOG", "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE",
            "PROCESS_OUTGOING_CALLS", "BIND_ACCESSIBILITY_SERVICE",
            "SYSTEM_ALERT_WINDOW", "REQUEST_INSTALL_PACKAGES",
        ]

        for pkg in packages[:20]:
            perms = self._run_adb(f"shell dumpsys package {pkg} | grep permission")
            found_perms = []
            for dp in dangerous_perms:
                if dp.lower() in perms.lower():
                    found_perms.append(dp)
            if found_perms:
                dangerous.append({
                    "package": pkg,
                    "permissions": found_perms,
                    "count": len(found_perms)
                })
        return dangerous

    def is_rooted(self) -> Dict[str, Any]:
        checks = {}
        su_check = self._run_adb("shell which su")
        checks["su_binary"] = bool(su_check and "not found" not in su_check.lower())

        test_keys = self._run_adb("shell cat /system/build.prop | grep ro.debuggable")
        checks["debuggable"] = "1" in test_keys

        busybox = self._run_adb("shell which busybox")
        checks["busybox"] = bool(busybox and "not found" not in busybox.lower())

        result = self._run_adb("shell 'if [ -f /system/app/Superuser.apk ]; then echo 1; else echo 0; fi'")
        checks["superuser_apk"] = result.strip() == "1"

        result = self._run_adb("shell 'if [ -f /sbin/su ]; then echo 1; elif [ -f /system/xbin/su ]; then echo 1; elif [ -f /system/bin/su ]; then echo 1; else echo 0; fi'")
        checks["su_paths"] = result.strip() == "1"

        checks["rooted"] = any([checks["su_binary"], checks["superuser_apk"],
                                 checks["su_paths"], checks["busybox"]])
        return checks

    def to_dict(self) -> Dict:
        return self.info

    def __repr__(self) -> str:
        return f"<ADBDevice {self.serial} - {self.info.get('model', 'Unknown')}>"


class DeviceManager:
    @staticmethod
    def list_devices() -> List[str]:
        try:
            result = subprocess.run(
                "adb devices", shell=True, capture_output=True,
                text=True, timeout=10
            )
            lines = result.stdout.strip().split("\n")[1:]
            devices = []
            for line in lines:
                if line.strip() and "device" in line and "unauthorized" not in line:
                    serial = line.split("\t")[0].strip()
                    if serial:
                        devices.append(serial)
            return devices
        except (subprocess.TimeoutExpired, Exception):
            return []

    @staticmethod
    def check_adb() -> bool:
        try:
            result = subprocess.run("adb version", shell=True,
                                     capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def start_server() -> bool:
        try:
            subprocess.run("adb start-server", shell=True,
                          capture_output=True, timeout=10)
            return True
        except Exception:
            return False

    @staticmethod
    def get_device(serial: str) -> Optional[ADBDevice]:
        try:
            return ADBDevice(serial)
        except Exception:
            return None
