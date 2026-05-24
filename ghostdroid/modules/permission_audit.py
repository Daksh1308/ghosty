from typing import Dict, Any, List
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, print_table, console, show_progress, print_panel
from core.device import DeviceManager

DANGEROUS_PERMISSION_DESCRIPTIONS = {
    "CAMERA": "Access camera hardware",
    "RECORD_AUDIO": "Record audio with microphone",
    "READ_CONTACTS": "Read user contacts database",
    "ACCESS_FINE_LOCATION": "Access precise GPS location",
    "ACCESS_COARSE_LOCATION": "Access approximate location",
    "READ_SMS": "Read SMS messages",
    "RECEIVE_SMS": "Receive SMS messages",
    "SEND_SMS": "Send SMS messages",
    "READ_CALL_LOG": "Read call history",
    "READ_EXTERNAL_STORAGE": "Read external storage contents",
    "WRITE_EXTERNAL_STORAGE": "Write to external storage",
    "PROCESS_OUTGOING_CALLS": "Monitor outgoing phone calls",
    "BIND_ACCESSIBILITY_SERVICE": "Full device control via accessibility",
    "SYSTEM_ALERT_WINDOW": "Draw overlay windows",
    "REQUEST_INSTALL_PACKAGES": "Install apps without user consent",
    "GET_ACCOUNTS": "Access account credentials",
    "READ_PHONE_STATE": "Read phone state and identifiers",
    "CALL_PHONE": "Make phone calls",
    "BODY_SENSORS": "Access health sensor data",
    "READ_CALENDAR": "Read calendar events",
    "WRITE_CALENDAR": "Modify calendar events",
}


class PermissionAuditModule(BaseModule):
    metadata = ModuleMetadata(
        name="permission_audit",
        version="1.0.0",
        description="Audit Android app permissions for security risks",
        author="GhostDroid",
        risk_level="medium",
        requires_adb=True,
        category="analysis",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        serial = kwargs.get("serial") or args[0] if args else None
        console.print("[bold cyan]╔══ Permission Audit Engine ══╗[/]")

        if not serial:
            devices = DeviceManager.list_devices()
            if not devices:
                print_status("No devices connected", "error")
                return {"error": "No devices"}
            serial = devices[0]
            print_status(f"Using device: {serial}", "info")

        from core.device import ADBDevice
        device = ADBDevice(serial)
        packages = device.get_installed_packages()
        print_status(f"Found {len(packages)} third-party apps", "info")

        results = {"device": serial, "packages_analyzed": 0, "dangerous_findings": [], "risk_score": 0}
        total_dangerous = 0

        for pkg in packages:
            perms = self._get_package_permissions(serial, pkg)
            dangerous = [p for p in perms if p in DANGEROUS_PERMISSION_DESCRIPTIONS]
            if dangerous:
                total_dangerous += len(dangerous)
                results["dangerous_findings"].append({
                    "package": pkg,
                    "dangerous_permissions": dangerous,
                    "count": len(dangerous),
                })
            results["packages_analyzed"] += 1

        if results["dangerous_findings"]:
            print_status(f"Found {total_dangerous} dangerous permission grants across {len(results['dangerous_findings'])} apps", "warn")
            print_table(
                "Dangerous Permission Findings",
                ["Package", "Dangerous Permissions", "Count"],
                [[f["package"][:30], ", ".join(f["dangerous_permissions"][:3]),
                  str(f["count"])] for f in results["dangerous_findings"][:15]],
                "yellow"
            )
        else:
            print_status("No dangerous permissions found", "success")

        results["risk_score"] = min(10, total_dangerous * 1.5)
        return results

    def _get_package_permissions(self, serial: str, package: str) -> List[str]:
        from utils.adb_utils import shell_command
        output = shell_command(serial, f"dumpsys package {package} 2>/dev/null | grep -i 'permission:'")
        permissions = []
        for line in output.split("\n"):
            line = line.strip()
            if "android.permission." in line:
                perm = line.split("android.permission.")[-1].split(":")[0].strip()
                if perm:
                    permissions.append(perm)
        return permissions
