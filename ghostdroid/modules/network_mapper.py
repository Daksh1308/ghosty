from typing import Dict, Any, List
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, print_table, console, show_progress
from utils.network_utils import network_scan, get_local_ip, get_network_range


class NetworkMapperModule(BaseModule):
    metadata = ModuleMetadata(
        name="network_mapper",
        version="1.0.0",
        description="Map local network topology and discover devices",
        author="GhostDroid",
        risk_level="low",
        requires_adb=False,
        category="network",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        subnet = kwargs.get("subnet")
        if not subnet:
            subnet = get_network_range()

        console.print(f"[bold cyan]╔══ Network Mapper ══╗[/]")
        print_status(f"Local IP: {get_local_ip()}", "info")
        print_status(f"Scanning subnet: {subnet}", "info")

        show_progress("Mapping network topology", 2.0)

        devices = network_scan(subnet)
        results = {"subnet": subnet, "devices_found": len(devices), "devices": devices}

        if devices:
            print_status(f"Found {len(devices)} active devices", "success")
            print_table(
                "Network Devices",
                ["IP", "Hostname", "Open Ports", "ADB Available", "Type"],
                [[
                    d["ip"],
                    d.get("hostname", "Unknown")[:25],
                    ", ".join(str(p) for p in d.get("open_ports", [])),
                    "[green]Yes[/]" if d.get("adb_available") else "[red]No[/]",
                    self._classify_device(d.get("open_ports", [])),
                ] for d in devices],
                "cyan"
            )
        else:
            print_status("No devices found on network", "warn")

        return results

    def _classify_device(self, ports: List[int]) -> str:
        if 5555 in ports:
            return "Android"
        if 22 in ports:
            return "Linux/SSH"
        if 80 in ports or 443 in ports:
            return "Web Server"
        return "Unknown"
