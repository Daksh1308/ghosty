# ⬡ GhostDroid CLI v2.0.1

**Ethical Android Security Testing Framework**

GhostDroid CLI is a comprehensive, cyberpunk-themed terminal toolkit for educational Android security assessment. It communicates with Android devices through ADB and USB debugging in authorized lab environments.

```
╔══════════════════════════════════════════════════════╗
║      █████╗ ██╗  ██╗ ██████╗ ███████╗████████╗      ║
║      ██╔══██╗██║  ██║██╔═══██╗██╔════╝╚══██╔══╝      ║
║      ███████║███████║██║   ██║███████╗   ██║         ║
║      ██╔════╝██╔══██║██║   ██║╚════██║   ██║         ║
║      ██║     ██║  ██║╚██████╔╝███████║   ██║         ║
║      ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝         ║
║                                                         ║
║      ██████╗ ██████╗  ██████╗ ██╗██████╗               ║
║      ██╔════╝ ██╔══██╗██╔═══██╗██║██╔══██╗              ║
║      ██║  ███╗██████╔╝██║   ██║██║██║  ██║              ║
║      ██║   ██║██╔══██╗██║   ██║██║██║  ██║              ║
║      ╚██████╔╝██║  ██║╚██████╔╝██║██████╔╝              ║
║       ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝╚═════╝              ║
║                                                         ║
║     Android Security Framework v2.0.1 - Ethical Edition  ║
╚══════════════════════════════════════════════════════════╝
```

> **⚠ WARNING: For authorized testing and educational purposes ONLY.**
> Unauthorized use of this tool against systems you do not own or have
> explicit written permission to test is ILLEGAL.

---

## Features

### 🔍 Device Detection & Analysis
- Detect Android devices via ADB (USB and network)
- Comprehensive device information gathering
- Model, Android version, API level, security patch level
- Battery status, USB debugging state, root detection

### 🛡 Security Analysis
- Analyze installed applications for dangerous permissions
- Detect debug-enabled applications
- APK package inspection (permissions, activities, services)
- Root detection checks
- Weak security settings identification

### 📦 Modular Architecture
- Dynamic module loader system
- Modules stored in `/modules` directory
- Each module contains metadata, description, risk level
- Easy to create and extend

### 🎯 Simulation Modules
- Simulated reverse shell demonstration
- Phishing awareness training
- Sandbox payload runner
- Educational payload generator
- Mock exploitation workflow

### 📊 Reporting
- Export reports in JSON, TXT, HTML formats
- Device information, findings, risk score, timestamps
- Professional cyberpunk-styled HTML reports

### 🖥 Terminal UI
- Rich library-powered interface
- Neon cyan/purple color scheme
- Animated ASCII banners
- Matrix rain effect
- Interactive menu system
- Command history
- Hacker-style boot sequence

---

## Installation

### Linux (Ubuntu/Debian)

```bash
# Clone the repository
git clone https://github.com/yourusername/ghostdroid.git
cd ghostdroid

# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip adb android-tools-adb

# Install Python dependencies
pip install -r requirements.txt

# Run GhostDroid CLI
python3 main.py
```

### Linux (Arch)

```bash
sudo pacman -S python python-pip android-tools
pip install -r requirements.txt
python3 main.py
```

### macOS

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python adb
pip install -r requirements.txt
python3 main.py
```

### Windows

```bash
# Install Python 3.8+ from python.org
# Install Android platform-tools (includes ADB)
# Download from: https://developer.android.com/studio/releases/platform-tools

pip install -r requirements.txt
python main.py
```

### Docker

```bash
# Build the Docker image
docker build -t ghostdroid .

# Run with USB device passthrough
docker run -it --privileged -v /dev/bus/usb:/dev/bus/usb ghostdroid

# Run without USB
docker run -it ghostdroid --help
```

---

## ADB Setup

### Enable USB Debugging on Android

1. Open **Settings** → **About Phone**
2. Tap **Build Number** 7 times to enable Developer Options
3. Go to **Settings** → **Developer Options**
4. Enable **USB Debugging**
5. Connect device via USB
6. Accept the RSA key fingerprint on the device

### Wireless ADB (Android 11+)

```bash
# Connect via TCP/IP
adb tcpip 5555
adb connect <device_ip>:5555
```

### Verify Connection

```bash
adb devices
# Should show: <serial>    device
```

---

## Usage

### Interactive CLI Mode

```bash
python3 main.py
```

This starts the full interactive shell:

```
ghostdroid > devices
ghostdroid > analyze
ghostdroid > modules list
ghostdroid > run permission_audit
ghostdroid > generate report
ghostdroid > help
```

### Command-Line Arguments

```bash
python3 main.py --devices          # List connected devices
python3 main.py --scan             # Scan network for ADB devices
python3 main.py --analyze SERIAL   # Analyze a specific device
python3 main.py --modules          # List available modules
python3 main.py --version          # Show version
```

### Interactive Commands

| Command | Description |
|---------|-------------|
| `devices` | List connected Android devices |
| `scan` | Scan network for ADB-enabled devices |
| `analyze` | Analyze connected device |
| `sessions` | Manage active sessions |
| `modules list` | List available modules |
| `modules info <name>` | Show module details |
| `run <module>` | Execute a module |
| `payloads` | List available payload templates |
| `generate <name>` | Generate a payload |
| `exploit-lab` | Run exploitation simulation |
| `report [format]` | Generate security report (json/txt/html) |
| `logs` | View activity logs |
| `shell` | Interactive ADB shell |
| `info` | System information |
| `matrix` | Matrix rain effect |
| `clear` | Clear screen |
| `help` | Show help |
| `exit` | Exit |

---

## Module System

### Architecture

Modules are Python classes that inherit from `BaseModule` and implement a `run()` method. They are auto-discovered from the `/modules` directory.

### Built-in Modules

| Module | Description | Risk | Requires ADB |
|--------|-------------|------|:-----------:|
| `device_info` | Gather comprehensive device information | Low | ✓ |
| `wifi_scanner` | Scan WiFi networks for devices | Low | ✗ |
| `network_mapper` | Map local network topology | Low | ✗ |
| `apk_analyzer` | Analyze APK files for security issues | Low | ✗ |
| `permission_audit` | Audit app permissions for risks | Medium | ✓ |
| `root_checker` | Check device for root indicators | Medium | ✓ |
| `phishing_sim` | Phishing awareness simulation | Medium | ✗ |
| `reverse_shell_sim` | Simulated reverse shell demo | High | ✗ |
| `payload_generator` | Generate educational payloads | Critical | ✗ |
| `exploit_sim` | Mock exploitation workflow | Critical | ✗ |

### Creating Custom Modules

Create a new file in `/modules`:

```python
from core.module_loader import BaseModule, ModuleMetadata

class MyModule(BaseModule):
    metadata = ModuleMetadata(
        name="my_module",
        version="1.0.0",
        description="Description of my module",
        author="Your Name",
        risk_level="medium",
        requires_adb=False,
        category="analysis",
    )

    def run(self, *args, **kwargs):
        # Your module logic here
        result = {"status": "completed", "data": []}
        return result
```

Modules are auto-discovered on startup.

---

## Project Structure

```
ghostdroid/
├── main.py                 # Entry point
├── core/
│   ├── __init__.py
│   ├── cli.py             # Interactive CLI shell
│   ├── banner.py          # ASCII banners & animations
│   ├── database.py        # SQLite database manager
│   ├── device.py          # ADB device interaction
│   ├── module_loader.py   # Dynamic module system
│   ├── reporting.py       # Report generation (JSON/TXT/HTML)
│   └── ui.py             # Rich terminal UI components
├── modules/
│   ├── __init__.py
│   ├── wifi_scanner.py
│   ├── apk_analyzer.py
│   ├── permission_audit.py
│   ├── device_info.py
│   ├── network_mapper.py
│   ├── root_checker.py
│   ├── reverse_shell_sim.py
│   ├── phishing_sim.py
│   ├── payload_generator.py
│   └── exploit_sim.py
├── payloads/
│   ├── __init__.py
│   ├── templates/
│   └── generated/
├── utils/
│   ├── __init__.py
│   ├── adb_utils.py
│   ├── network_utils.py
│   └── helpers.py
├── database/
├── reports/
├── logs/
├── config.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Configuration

Edit `config.yaml` to customize:

```yaml
settings:
  theme: cyberpunk
  log_level: INFO
  animation_speed: 0.03
  banner_rotation: true

network:
  scan_range: 192.168.1.0/24
  scan_ports: [22, 80, 443, 5555, 8080]

modules:
  risk_level: educational
  sandbox_mode: true
```

---

## Screenshots (Mock Terminal Output)

```
╔══════════════════════════════════════════════════════╗
║         GHOSTDROID CLI v2.0.1 - Ethical Edition       ║
╚══════════════════════════════════════════════════════════╝

[*] Initializing GhostDroid kernel...
[+] Core modules loaded
[+] ADB detected: Android Debug Bridge version 1.0.41
[+] Device connected: R58M35A6K7F

ghostdroid > devices

┌─────────────────────────────────────────────────────────┐
│               Connected Devices                          │
├──────────────┬──────────────┬─────────┬─────┬──────────┤
│ Serial       │ Model        │ Android │ API │ Battery  │
├──────────────┼──────────────┼─────────┼─────┼──────────┤
│ R58M35A6K7F  │ Pixel 7 Pro │ 14      │ 34  │ 85%      │
└──────────────┴──────────────┴─────────┴─────┴──────────┘

ghostdroid > run root_checker

╔══ Root Checker ══╗
[+] Device: R58M35A6K7F
[!] Device is ROOTED - Security risk!

ghostdroid > generate report
[+] Report generated: reports/report_20250115_143022.html
```

---

## Ethical Use & Legal

### ⚠ IMPORTANT LEGAL NOTICE

GhostDroid CLI is designed STRICTLY for:
- **Educational purposes** - Learning about Android security
- **Authorized security testing** - Penetration testing with written permission
- **Lab environments** - Testing on devices you own

### You MUST:
- Only test devices you own or have explicit written permission to test
- Comply with all applicable local, state, federal, and international laws
- Use this tool solely for educational and authorized security assessment
- Not use this tool for any malicious or unauthorized purpose

### You MUST NOT:
- Use this tool against devices you do not own
- Deploy generated payloads without authorization
- Use this tool for any illegal activity
- Remove or bypass the ethical disclaimers

**Violating these terms may result in criminal and civil liability.**

---

## License

This project is provided for **educational and authorized security testing purposes only**.

No warranty is provided. Use at your own risk.

---

## Acknowledgments

- Metasploit Framework for inspiration
- Android Open Source Project
- Rich library for terminal UI
- The security research community

---

*"With great power comes great responsibility." - Uncle Ben*
