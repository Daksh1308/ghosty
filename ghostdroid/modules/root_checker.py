from typing import Dict, Any
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, print_table, console, print_panel
from core.device import DeviceManager, ADBDevice


class RootCheckerModule(BaseModule):
    metadata = ModuleMetadata(
        name="root_checker",
        version="1.0.0",
        description="Check Android device for root access indicators",
        author="GhostDroid",
        risk_level="medium",
        requires_adb=True,
        category="analysis",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        serial = kwargs.get("serial") or args[0] if args else None
        console.print("[bold cyan]╔══ Root Checker ══╗[/]")

        if not serial:
            devices = DeviceManager.list_devices()
            if not devices:
                print_status("No devices connected", "error")
                return {"error": "No devices"}
            serial = devices[0]

        device = ADBDevice(serial)
        root_checks = device.is_rooted()
        results = {"device": serial, "checks": root_checks, "rooted": root_checks["rooted"]}

        print_status(f"Device: {serial}", "info")

        print_panel(
            f"[bold]Root Status:[/] {'[bold red]DEVICE IS ROOTED[/]' if root_checks['rooted'] else '[bold green]Device is NOT rooted[/]'}\n\n"
            f"[cyan]su binary:[/] {'[red]Found[/]' if root_checks['su_binary'] else '[green]Not found[/]'}\n"
            f"[cyan]Debuggable:[/] {'[yellow]Yes[/]' if root_checks['debuggable'] else '[green]No[/]'}\n"
            f"[cyan]BusyBox:[/] {'[yellow]Found[/]' if root_checks['busybox'] else '[green]Not found[/]'}\n"
            f"[cyan]Superuser.apk:[/] {'[red]Present[/]' if root_checks['superuser_apk'] else '[green]Not present[/]'}\n"
            f"[cyan]su in PATH:[/] {'[red]Found[/]' if root_checks['su_paths'] else '[green]Not found[/]'}",
            title="Root Check Results",
            style="cyan"
        )

        severity = "critical" if root_checks["rooted"] else "info"
        print_status(
            f"Device root status: {'ROOTED - Security risk!' if root_checks['rooted'] else 'Secure'}",
            severity
        )

        return results
