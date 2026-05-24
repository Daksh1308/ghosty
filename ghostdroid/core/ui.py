import time
import random
import sys
from typing import List, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.tree import Tree
from rich.columns import Columns
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown


console = Console()


def type_out(text: str, speed: float = 0.03, color: str = "cyan"):
    for char in text:
        console.print(f"[{color}]{char}[/]", end="")
        time.sleep(speed)
    console.print()


def print_status(message: str, status: str = "info"):
    icons = {"info": "[cyan]*[/]", "success": "[green]+[/]",
             "warn": "[yellow]![/]", "error": "[red]x[/]",
             "arrow": "[magenta]->[/]"}
    icon = icons.get(status, "[cyan]*[/]")
    colors = {"info": "cyan", "success": "green",
              "warn": "yellow", "error": "red", "arrow": "magenta"}
    color = colors.get(status, "cyan")
    console.print(f"  {icon} [{color}]{message}[/]")


def print_table(title: str, columns: List[str], rows: List[List], style: str = "cyan"):
    table = Table(
        title=f"[bold {style}]{title}[/]",
        box=box.HEAVY,
        border_style=style,
        header_style=f"bold {style}",
        title_style=f"bold {style}",
    )
    for col in columns:
        table.add_column(col, style=style)
    for row in rows:
        table.add_row(*[str(c) for c in row])
    console.print(table)


def print_panel(content: str, title: str = "", style: str = "cyan", subtitle: str = ""):
    panel = Panel(
        content,
        title=f"[bold {style}]{title}[/]",
        subtitle=subtitle,
        border_style=style,
        box=box.HEAVY,
    )
    console.print(panel)


def show_progress(task_name: str, duration: float = 2.0):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="green"),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]{task_name}...", total=100)
        while not progress.finished:
            progress.update(task, advance=random.uniform(1, 5))
            time.sleep(0.05)


def animate_typing(text: str, speed: float = 0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write("\n")


def hacker_input(prompt_text: str, password: bool = False) -> str:
    text = Text(prompt_text, style="bold cyan")
    if password:
        return Prompt.ask(text, password=True)
    return Prompt.ask(text)


def hacker_confirm(prompt_text: str) -> bool:
    text = Text(prompt_text, style="bold yellow")
    return Confirm.ask(text)


def show_disclaimer():
    disclaimer = """
[bold red]╔══════════════════════════════════════════════════════════════╗
║                    ETHICAL USE DISCLAIMER                    ║
╠══════════════════════════════════════════════════════════════╣
║  GhostDroid CLI is designed STRICTLY for educational and     ║
║  authorized security testing purposes only.                 ║
║                                                              ║
║  [yellow]WARNING:[/yellow] Unauthorized use of this tool against          ║
║  systems or devices you do not own or have explicit          ║
║  written permission to test is ILLEGAL.                     ║
║                                                              ║
║  By using this software, you agree to:                      ║
║  • Only test devices you own or have permission to test     ║
║  • Comply with all applicable laws and regulations          ║
║  • Use this tool for educational purposes only              ║
║  • Not use this tool for any malicious purpose             ║
║                                                              ║
║  [bold green]GhostDroid CLI v2.0.1 - Ethical Edition[/]                    ║
╚══════════════════════════════════════════════════════════════╝[/]
"""
    console.print(Panel(disclaimer.strip(), border_style="red", box=box.DOUBLE))
    return hacker_confirm("[yellow]Do you accept the ethical usage terms?")


def show_help():
    help_text = """
[bold cyan]Available Commands:[/]

[green]  devices[/]            List connected Android devices
[green]  scan[/]               Scan network for ADB-enabled devices
[green]  analyze[/]            Analyze a connected device
[green]  sessions[/]           Manage active sessions
[green]  modules[/]            List and manage modules
[green]  run[/]                Run a specific module
[green]  payloads[/]           List available payloads
[green]  generate[/]           Generate a payload
[green]  exploit-lab[/]       Run exploitation simulation
[green]  report[/]             Generate security report
[green]  logs[/]               View activity logs
[green]  shell[/]              Interactive ADB shell
[green]  info[/]               Show system information
[green]  clear[/]              Clear the screen
[green]  help[/]               Show this help message
[green]  exit[/]               Exit GhostDroid CLI

[dim]Type 'help <command>' for detailed usage.[/]
"""
    console.print(Panel(help_text.strip(), title="[bold magenta]GHOSTDROID HELP[/]",
                         border_style="cyan", box=box.HEAVY))


def show_module_help():
    help_text = """
[bold cyan]Module Management:[/]

[green]  modules list[/]               List all available modules
[green]  modules info <name>[/]       Show module information
[green]  modules load <name>[/]       Load a module
[green]  modules unload <name>[/]     Unload a module

[bold cyan]Available Modules:[/]

[yellow]  wifi_scanner[/]        - Scan WiFi networks for devices
[yellow]  apk_analyzer[/]       - Analyze APK packages
[yellow]  permission_audit[/]   - Audit app permissions
[yellow]  device_info[/]        - Gather device information
[yellow]  network_mapper[/]     - Map local network topology
[yellow]  root_checker[/]       - Check device root status
[yellow]  reverse_shell_sim[/]  - Simulated reverse shell demo
[yellow]  phishing_sim[/]      - Phishing awareness simulation
[yellow]  payload_generator[/]  - Generate educational payloads
[yellow]  exploit_sim[/]       - Mock exploitation workflow
"""
    console.print(Panel(help_text.strip(), title="[bold magenta]MODULE SYSTEM[/]",
                         border_style="purple", box=box.HEAVY))
