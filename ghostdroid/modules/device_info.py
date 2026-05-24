from typing import Dict, Any
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, print_table, console, print_panel
from core.device import DeviceManager, ADBDevice


class DeviceInfoModule(BaseModule):
    metadata = ModuleMetadata(
        name="device_info",
        version="1.0.0",
        description="Gather comprehensive Android device information",
        author="GhostDroid",
        risk_level="low",
        requires_adb=True,
        category="reconnaissance",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        serial = kwargs.get("serial") or args[0] if args else None
        console.print("[bold cyan]╔══ Device Information Gathering ══╗[/]")

        if not serial:
            devices = DeviceManager.list_devices()
            if not devices:
                print_status("No devices connected", "error")
                return {"error": "No devices"}
            serial = devices[0]
            print_status(f"Analyzing device: {serial}", "info")

        device = ADBDevice(serial)
        info = device.to_dict()

        print_panel(
            f"[bold magenta]Device:[/] {info.get('manufacturer', 'Unknown')} {info.get('model', 'Unknown')}\n"
            f"[bold cyan]Android:[/] {info.get('android_version', 'Unknown')} (API {info.get('api_level', 'Unknown')})\n"
            f"[bold green]Security Patch:[/] {info.get('security_patch', 'Unknown')}\n"
            f"[bold yellow]Battery:[/] {info.get('battery_level', '?')}% ({info.get('battery_status', 'Unknown')})\n"
            f"[bold red]USB Debugging:[/] {'[green]Enabled[/]' if info.get('usb_debugging') else '[red]Disabled[/]'}\n"
            f"[bold blue]Resolution:[/] {info.get('resolution', 'Unknown')}\n"
            f"[bold white]RAM:[/] {info.get('total_ram', 'Unknown')}\n"
            f"[bold]ABI:[/] {info.get('cpu_abi', 'Unknown')}",
            title="Device Information",
            style="cyan"
        )

        print_table(
            "Detailed Device Properties",
            ["Property", "Value"],
            [[k.replace("_", " ").title(), str(v)] for k, v in info.items()],
            "green"
        )

        return {"device_info": info}
