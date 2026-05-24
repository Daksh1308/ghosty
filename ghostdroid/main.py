#!/usr/bin/env python3
"""
GhostDroid CLI - Ethical Android Security Testing Framework
Version: 2.0.1
License: Educational Use Only

GhostDroid CLI is a comprehensive Android security assessment framework
designed for authorized security testing and educational purposes.
It communicates with Android devices through ADB and USB debugging
in controlled lab environments.

WARNING: This tool is for authorized testing ONLY.
Unauthorized use against systems you do not own is ILLEGAL.
"""

import sys
import os
import argparse
import time
import subprocess


BOLD = '\033[1m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
PURPLE = '\033[95m'
RESET = '\033[0m'


def check_python_version():
    if sys.version_info < (3, 8):
        print(f"{RED}Error: Python 3.8+ is required{RESET}")
        sys.exit(1)


def check_dependencies():
    missing = []
    try:
        import rich
    except ImportError:
        missing.append("rich")

    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")

    if missing:
        print(f"{RED}Missing dependencies: {', '.join(missing)}{RESET}")
        print(f"{YELLOW}Install with: pip install -r requirements.txt{RESET}")
        sys.exit(1)


def check_adb():
    try:
        result = subprocess.run(["adb", "version"],
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0] if result.stdout else "ADB"
            print(f"{GREEN}[+] {version}{RESET}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print(f"{YELLOW}[!] ADB not found in PATH{RESET}")
    print(f"{YELLOW}    Install Android platform tools:{RESET}")
    print(f"{CYAN}    https://developer.android.com/studio/releases/platform-tools{RESET}")
    return False


def banner():
    banner_art = f"""
{BOLD}{CYAN}
╔══════════════════════════════════════════════════════╗
║                                                     ║
║      {PURPLE}█████╗ ██╗  ██╗ ██████╗ ███████╗████████╗{CYAN}      ║
║      {PURPLE}██╔══██╗██║  ██║██╔═══██╗██╔════╝╚══██╔══╝{CYAN}      ║
║      {PURPLE}███████║███████║██║   ██║███████╗   ██║{CYAN}         ║
║      {PURPLE}██╔════╝██╔══██║██║   ██║╚════██║   ██║{CYAN}         ║
║      {PURPLE}██║     ██║  ██║╚██████╔╝███████║   ██║{CYAN}         ║
║      {PURPLE}╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝{CYAN}         ║
║                                                     ║
║      {YELLOW}██████╗ ██████╗  ██████╗ ██╗██████╗{CYAN}           ║
║      {YELLOW}██╔════╝ ██╔══██╗██╔═══██╗██║██╔══██╗{CYAN}          ║
║      {YELLOW}██║  ███╗██████╔╝██║   ██║██║██║  ██║{CYAN}          ║
║      {YELLOW}██║   ██║██╔══██╗██║   ██║██║██║  ██║{CYAN}          ║
║      {YELLOW}╚██████╔╝██║  ██║╚██████╔╝██║██████╔╝{CYAN}          ║
║      {YELLOW} ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═════╝{CYAN}           ║
║                                                     ║
║     {GREEN}Android Security Framework v2.0.1 - Ethical Edition{CYAN}    ║
╚══════════════════════════════════════════════════════════╝
{RESET}"""
    print(banner_art)


def main():
    check_python_version()
    check_dependencies()

    parser = argparse.ArgumentParser(
        description=f"{BOLD}GhostDroid CLI - Ethical Android Security Testing Framework{RESET}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{GREEN}Examples:{RESET}
  python3 main.py                  {CYAN}# Start interactive CLI{RESET}
  python3 main.py --devices        {CYAN}# List connected devices{RESET}
  python3 main.py --scan           {CYAN}# Scan network{RESET}
  python3 main.py --analyze SERIAL {CYAN}# Analyze a device{RESET}

{RED}WARNING: For authorized testing only!{RESET}
"""
    )

    parser.add_argument("--devices", action="store_true", help="List connected devices")
    parser.add_argument("--scan", action="store_true", help="Scan network for devices")
    parser.add_argument("--analyze", metavar="SERIAL", help="Analyze a specific device")
    parser.add_argument("--modules", action="store_true", help="List available modules")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--no-banner", action="store_true", help="Skip banner display")

    args = parser.parse_args()

    if args.version:
        print(f"GhostDroid CLI v2.0.1")
        print("Ethical Android Security Testing Framework")
        return

    if not args.no_banner:
        banner()
        time.sleep(0.5)

    check_adb()

    if args.devices:
        from core.device import DeviceManager
        devices = DeviceManager.list_devices()
        if devices:
            print(f"\n{GREEN}[+] Connected devices:{RESET}")
            for d in devices:
                print(f"  {CYAN}→{RESET} {d}")
        else:
            print(f"\n{YELLOW}[!] No devices connected{RESET}")
        return

    if args.scan:
        print(f"\n{CYAN}[*] Scanning network for ADB-enabled devices...{RESET}")
        from utils.network_utils import network_scan, get_network_range
        results = network_scan(get_network_range())
        if results:
            adb_found = [d for d in results if d.get("adb_available")]
            print(f"\n{GREEN}[+] Found {len(results)} devices ({len(adb_found)} with ADB){RESET}")
            for d in results:
                adb_mark = f"{GREEN}[ADB]{RESET}" if d.get("adb_available") else ""
                print(f"  {CYAN}{d['ip']:15s}{RESET} {', '.join(str(p) for p in d.get('open_ports', [])):15s} {adb_mark}")
        else:
            print(f"\n{YELLOW}[!] No devices found{RESET}")
        return

    if args.analyze:
        from core.device import ADBDevice
        serial = args.analyze
        print(f"\n{CYAN}[*] Analyzing device: {serial}{RESET}")
        device = ADBDevice(serial)
        info = device.to_dict()
        for k, v in info.items():
            print(f"  {GREEN}{k.replace('_', ' ').title():25s}{RESET}: {v}")
        root = device.is_rooted()
        print(f"  {RED if root['rooted'] else GREEN}{'Root Status':25s}{RESET}: {'ROOTED' if root['rooted'] else 'Secure'}")
        return

    if args.modules:
        from core.module_loader import ModuleManager
        mm = ModuleManager()
        modules = mm.list_modules()
        print(f"\n{CYAN}[*] Available modules ({len(modules)}):{RESET}")
        for m in modules:
            risk_colors = {"low": GREEN, "medium": YELLOW, "high": RED, "critical": RED}
            risk_symbol = {"low": "○", "medium": "◇", "high": "◆", "critical": "■"}
            rc = risk_colors.get(m["risk_level"], CYAN)
            rs = risk_symbol.get(m["risk_level"], "○")
            adb_req = f"{GREEN}[ADB]{RESET}" if m["requires_adb"] else ""
            print(f"  {CYAN}→{RESET} {m['name']:25s} {rc}{rs}{RESET} {m['description'][:45]} {adb_req}")
        return

    from core.cli import GhostDroidCLI
    try:
        cli = GhostDroidCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrupted{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] Fatal error: {e}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
