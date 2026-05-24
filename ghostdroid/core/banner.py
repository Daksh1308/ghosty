import random
import time
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()

BANNERS = [
    r"""
[cyan]╔══════════════════════════════════════════════════════╗
║                                                         ║
║      [bold magenta]█████╗ ██╗  ██╗ ██████╗ ███████╗████████╗[/]      ║
║      [bold magenta]██╔══██╗██║  ██║██╔═══██╗██╔════╝╚══██╔══╝[/]      ║
║      [bold magenta]███████║███████║██║   ██║███████╗   ██║[/]         ║
║      [bold magenta]██╔════╝██╔══██║██║   ██║╚════██║   ██║[/]         ║
║      [bold magenta]██║     ██║  ██║╚██████╔╝███████║   ██║[/]         ║
║      [bold magenta]╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝[/]         ║
║                                                         ║
║          [bold yellow]██████╗ ██████╗  ██████╗ ██╗██████╗[/]           ║
║          [bold yellow]██╔════╝ ██╔══██╗██╔═══██╗██║██╔══██╗[/]          ║
║          [bold yellow]██║  ███╗██████╔╝██║   ██║██║██║  ██║[/]          ║
║          [bold yellow]██║   ██║██╔══██╗██║   ██║██║██║  ██║[/]          ║
║          [bold yellow]╚██████╔╝██║  ██║╚██████╔╝██║██████╔╝[/]          ║
║          [bold yellow] ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═════╝[/]           ║
║                                                         ║
║     [bold green]Android Security Framework v2.0.1 - Ethical Edition[/]      ║
║            [dim]Educational Purpose Only | Lab Use[/dim]              ║
╚══════════════════════════════════════════════════════════╝[/]
""",
    r"""
[cyan]╔══════════════════════════════════════════════════════╗
║            [bold magenta]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/]              ║
║            [bold magenta]▓  ██████  ██░ ██  ██████  ▓[/]              ║
║            [bold magenta]▓ ██       ██░ ██ ██       ▓[/]              ║
║            [bold magenta]▓ ██       ██████  ███████  ▓[/]              ║
║            [bold magenta]▓ ██       ██░ ██       ██  ▓[/]              ║
║            [bold magenta]▓  ██████  ██░ ██  ██████   ▓[/]              ║
║            [bold magenta]▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓[/]              ║
║                                                         ║
║     [bold yellow]░▒▓█ G H O S T D R O I D  C L I █▓▒░[/]              ║
║                                                         ║
║           [bold green]Security Testing Framework[/bold green]              ║
║            [dim]v2.0.1 | Ethical Use Only[/dim]                ║
╚══════════════════════════════════════════════════════════╝[/]
""",
]

MATRIX_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()"


def matrix_rain(console, duration=2, columns=60):
    import threading
    stop_rain = threading.Event()

    def rain():
        col_positions = [random.randint(0, columns) for _ in range(columns // 2)]
        while not stop_rain.is_set():
            line = ""
            for i in range(columns):
                if i in col_positions:
                    line += f"[green]{random.choice(MATRIX_CHARS)}[/]"
                else:
                    line += " "
            console.print(line, end="\r")
            col_positions = [c + random.choice([-1, 0, 1]) for c in col_positions]
            col_positions = [max(0, min(columns, c)) for c in col_positions]
            time.sleep(0.05)

    t = threading.Thread(target=rain, daemon=True)
    t.start()
    time.sleep(duration)
    stop_rain.set()


def animate_startup(console):
    boot_steps = [
        ("[cyan]Initializing GhostDroid kernel...", 0.3),
        ("[green]Loading core modules...", 0.2),
        ("[yellow]Establishing secure channels...", 0.3),
        ("[cyan]Scanning for ADB interfaces...", 0.4),
        ("[green]Cryptographic handshake complete", 0.2),
        ("[yellow]Loading payload templates...", 0.3),
        ("[cyan]Armoring shell environment...", 0.2),
        ("[bold green]GhostDroid CLI ready for deployment[/]", 0.5),
    ]

    for step, delay in boot_steps:
        console.print(f"  [dim]>>>[/] {step}")
        time.sleep(delay)


def show_banner(console):
    banner = random.choice(BANNERS)
    panel = Panel(
        Align.center(banner),
        box=box.HEAVY,
        border_style="cyan",
        padding=(1, 2),
        title="[bold magenta]GHOSTDROID CLI[/]",
        subtitle="[dim]ethical security testing[/]",
    )
    console.print(panel)
    console.print()
