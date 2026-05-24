import subprocess
import re
import os
from typing import Optional, List, Dict, Tuple


def check_adb_installed() -> bool:
    try:
        result = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_adb_path() -> str:
    if os.name == "nt":
        paths = ["adb.exe", os.path.expanduser("~/platform-tools/adb.exe")]
    else:
        paths = ["adb", os.path.expanduser("~/platform-tools/adb"),
                 "/usr/bin/adb", "/usr/local/bin/adb"]

    for p in paths:
        try:
            subprocess.run([p, "version"], capture_output=True, timeout=3)
            return p
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return "adb"


def get_devices() -> List[Dict[str, str]]:
    adb = get_adb_path()
    try:
        result = subprocess.run([adb, "devices", "-l"], capture_output=True, text=True, timeout=10)
        devices = []
        lines = result.stdout.strip().split("\n")[1:]
        for line in lines:
            if line.strip() and "device" in line:
                parts = line.split()
                device = {"serial": parts[0], "state": "device"}
                for part in parts[1:]:
                    if ":" in part:
                        key, val = part.split(":", 1)
                        device[key] = val
                devices.append(device)
        return devices
    except (subprocess.TimeoutExpired, Exception):
        return []


def run_adb_command(serial: str, command: str, timeout: int = 15) -> Tuple[bool, str]:
    adb = get_adb_path()
    try:
        if serial:
            full_cmd = [adb, "-s", serial] + command.split()
        else:
            full_cmd = [adb] + command.split()
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        return (result.returncode == 0, result.stdout.strip())
    except subprocess.TimeoutExpired:
        return (False, "Command timed out")
    except Exception as e:
        return (False, str(e))


def install_apk(serial: str, apk_path: str) -> Tuple[bool, str]:
    return run_adb_command(serial, f"install -r {apk_path}", timeout=60)


def pull_file(serial: str, remote_path: str, local_path: str) -> Tuple[bool, str]:
    return run_adb_command(serial, f"pull \"{remote_path}\" \"{local_path}\"", timeout=30)


def push_file(serial: str, local_path: str, remote_path: str) -> Tuple[bool, str]:
    return run_adb_command(serial, f"push \"{local_path}\" \"{remote_path}\"", timeout=30)


def shell_command(serial: str, cmd: str, timeout: int = 15) -> str:
    adb = get_adb_path()
    try:
        result = subprocess.run(
            [adb, "-s", serial, "shell", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_device_property(serial: str, prop: str) -> str:
    return shell_command(serial, f"getprop {prop}")


def forward_port(serial: str, local: int, remote: int) -> bool:
    success, _ = run_adb_command(serial, f"forward tcp:{local} tcp:{remote}")
    return success


def is_device_authorized(serial: str) -> bool:
    try:
        adb = get_adb_path()
        result = subprocess.run(
            [adb, "-s", serial, "get-state"],
            capture_output=True, text=True, timeout=5
        )
        return "device" in result.stdout.strip()
    except Exception:
        return False
