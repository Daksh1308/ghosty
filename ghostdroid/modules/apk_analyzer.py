import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, print_table, console, show_progress, print_panel

DANGEROUS_PERMISSIONS = {
    "android.permission.READ_CALL_LOG": "Reads call logs",
    "android.permission.READ_CONTACTS": "Reads contact data",
    "android.permission.READ_SMS": "Reads SMS messages",
    "android.permission.RECEIVE_SMS": "Receives SMS messages",
    "android.permission.SEND_SMS": "Sends SMS messages",
    "android.permission.RECORD_AUDIO": "Records audio",
    "android.permission.CAMERA": "Accesses camera",
    "android.permission.ACCESS_FINE_LOCATION": "Precise GPS location",
    "android.permission.ACCESS_COARSE_LOCATION": "Approximate location",
    "android.permission.READ_EXTERNAL_STORAGE": "Reads external storage",
    "android.permission.WRITE_EXTERNAL_STORAGE": "Writes to external storage",
    "android.permission.PROCESS_OUTGOING_CALLS": "Monitors outgoing calls",
    "android.permission.SYSTEM_ALERT_WINDOW": "Draws overlay windows",
    "android.permission.BIND_ACCESSIBILITY_SERVICE": "Accessibility service access",
    "android.permission.REQUEST_INSTALL_PACKAGES": "Installs APKs",
    "android.permission.GET_ACCOUNTS": "Accesses account list",
    "android.permission.READ_PHONE_STATE": "Reads phone state/IMEI",
    "android.permission.CALL_PHONE": "Makes phone calls",
}


class ApkAnalyzerModule(BaseModule):
    metadata = ModuleMetadata(
        name="apk_analyzer",
        version="1.0.0",
        description="Analyze APK files for permissions, signatures, and security issues",
        author="GhostDroid",
        risk_level="low",
        requires_adb=False,
        category="analysis",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        apk_path = kwargs.get("apk_path") or args[0] if args else None

        if not apk_path:
            from core.ui import hacker_input
            apk_path = hacker_input("[cyan]Enter path to APK file[/]")

        if not os.path.exists(apk_path):
            print_status(f"APK not found: {apk_path}", "error")
            return {"error": "APK not found"}

        console.print(f"[bold cyan]Analyzing:[/] {apk_path}")
        show_progress("Decompiling APK structure", 1.0)

        result = self._analyze_apk(apk_path)

        print_panel(
            f"[bold green]Package:[/] {result['package']}\n"
            f"[bold green]Version:[/] {result['version_name']} ({result['version_code']})\n"
            f"[bold green]Min SDK:[/] {result['min_sdk']}\n"
            f"[bold green]Target SDK:[/] {result['target_sdk']}\n"
            f"[bold green]Debuggable:[/] {'[red]YES[/]' if result['debuggable'] else '[green]No[/]'}\n"
            f"[bold green]Permissions:[/] {result['permission_count']} ({result['dangerous_count']} dangerous)",
            title="APK Summary",
            style="cyan"
        )

        if result["permissions"]:
            print_table(
                "Permissions",
                ["Permission", "Description", "Risk"],
                [[p["name"], p["description"], p["risk"]] for p in result["permissions"]],
                "cyan"
            )

        if result["dangerous_permissions"]:
            print_status(f"Found {len(result['dangerous_permissions'])} dangerous permissions!", "warn")

        return result

    def _analyze_apk(self, apk_path: str) -> Dict[str, Any]:
        result = {
            "package": "Unknown",
            "version_name": "Unknown",
            "version_code": "Unknown",
            "min_sdk": "Unknown",
            "target_sdk": "Unknown",
            "debuggable": False,
            "permissions": [],
            "dangerous_permissions": [],
            "permission_count": 0,
            "dangerous_count": 0,
            "activities": [],
            "services": [],
            "receivers": [],
            "signature_info": {},
        }

        try:
            with zipfile.ZipFile(apk_path, "r") as zf:
                if "AndroidManifest.xml" in zf.namelist():
                    manifest_data = zf.read("AndroidManifest.xml")
                    self._parse_manifest_binary(manifest_data, result)
        except zipfile.BadZipFile:
            print_status("Invalid APK file (not a valid ZIP)", "error")
        except Exception as e:
            print_status(f"Error analyzing APK: {e}", "error")

        return result

    def _parse_manifest_binary(self, data: bytes, result: Dict):
        try:
            text = data.decode("utf-8", errors="replace")
            self._parse_manifest_text(text, result)
        except Exception:
            try:
                text = data.decode("latin-1", errors="replace")
                self._parse_manifest_text(text, result)
            except Exception:
                print_status("Could not parse AndroidManifest.xml", "warn")

    def _parse_manifest_text(self, text: str, result: Dict):
        package_match = re.search(r'package="([^"]+)"', text)
        if package_match:
            result["package"] = package_match.group(1)

        version_match = re.search(r'android:versionName="([^"]*)"', text)
        if version_match:
            result["version_name"] = version_match.group(1) or "Unknown"

        code_match = re.search(r'android:versionCode="(\d+)"', text)
        if code_match:
            result["version_code"] = code_match.group(1)

        min_sdk = re.search(r'android:minSdkVersion="?(\d+)"?', text)
        if min_sdk:
            result["min_sdk"] = min_sdk.group(1)

        target_sdk = re.search(r'android:targetSdkVersion="?(\d+)"?', text)
        if target_sdk:
            result["target_sdk"] = target_sdk.group(1)

        debuggable = re.search(r'android:debuggable="?true"?', text)
        result["debuggable"] = bool(debuggable)

        perms = re.findall(r'uses-permission[^>]*android:name="([^"]+)"', text)
        result["permission_count"] = len(perms)

        for perm in perms:
            info = {
                "name": perm.replace("android.permission.", ""),
                "full_name": perm,
                "description": DANGEROUS_PERMISSIONS.get(perm, "General permission"),
                "risk": "HIGH" if perm in DANGEROUS_PERMISSIONS else "low",
            }
            result["permissions"].append(info)
            if perm in DANGEROUS_PERMISSIONS:
                result["dangerous_permissions"].append(info)
                result["dangerous_count"] += 1

        activities = re.findall(r'<activity[^>]*android:name="([^"]+)"', text)
        result["activities"] = activities

        services = re.findall(r'<service[^>]*android:name="([^"]+)"', text)
        result["services"] = services

        receivers = re.findall(r'<receiver[^>]*android:name="([^"]+)"', text)
        result["receivers"] = receivers
