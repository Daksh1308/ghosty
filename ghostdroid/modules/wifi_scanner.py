import subprocess
import re
from typing import Dict, Any, List
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, print_table, console, show_progress


class WifiScannerModule(BaseModule):
    metadata = ModuleMetadata(
        name="wifi_scanner",
        version="1.0.0",
        description="Scan WiFi networks and list connected devices",
        author="GhostDroid",
        risk_level="low",
        requires_adb=False,
        category="network",
    )

    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        console.print("[bold cyan]╔══ WiFi Network Scanner ══╗[/]")
        results = {"networks": [], "clients": [], "interface_info": {}}

        interface = kwargs.get("interface")
        networks = self._scan_networks(interface)
        results["networks"] = networks

        if networks:
            print_table(
                "Available Networks",
                ["SSID", "Signal", "Channel", "Security", "BSSID"],
                [[n["ssid"], f"{n['signal']}%", n["channel"],
                  n["security"], n["bssid"]] for n in networks[:10]],
                "cyan"
            )
        else:
            print_status("No wireless networks found or interface not available", "warn")

        return results

    def _scan_networks(self, interface: str = None) -> List[Dict]:
        networks = []
        try:
            cmd = ["nmcli", "-t", "-f", "SSID,SIGNAL,CHAN,SECURITY,BSSID", "dev", "wifi", "list"]
            if interface:
                cmd.extend(["ifname", interface])
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            for line in result.stdout.strip().split("\n"):
                if line and ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 5:
                        networks.append({
                            "ssid": parts[0] or "Hidden",
                            "signal": int(parts[1]) if parts[1].isdigit() else 0,
                            "channel": parts[2],
                            "security": parts[3],
                            "bssid": parts[4],
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                result = subprocess.run(
                    ["iwlist", "scanning", "2>/dev/null"],
                    shell=True, capture_output=True, text=True, timeout=30
                )
                current_net = {}
                for line in result.stdout.split("\n"):
                    if "ESSID" in line:
                        current_net["ssid"] = re.search(r'"(.+)"', line).group(1) if re.search(r'"(.+)"', line) else "Hidden"
                        if current_net:
                            networks.append(current_net)
                        current_net = {}
                    if "Signal level" in line:
                        match = re.search(r"Signal level[=:](-?\d+)", line)
                        if match:
                            current_net["signal"] = int(match.group(1))
                    if "Channel" in line:
                        match = re.search(r"Channel[=:](\d+)", line)
                        if match:
                            current_net["channel"] = match.group(1)
                    if "Encryption key" in line:
                        current_net["security"] = "on" if "on" in line else "off"
            except Exception:
                pass
        return networks
