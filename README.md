<div align="center">

```
  ______ ___   ___  ____  _____  ____  ___  ____  _____  _____  ____ ___  ____
 /  ___//   \ /   \/  _ \/  __/ /  _ \/   \/  _ \/  __//  __/ /  _//   \/  _ \
 |  |  | | | | | | | | \| |  \ | | \| | | | | \| |  \  |  \   | |  | | | | | |
 |  |__| |_| | |_| | |_/| |  /_ | |_/| |_/| | |_/| |  /_ |  /_  | |_ | |_| | |_/|
 \____/\____/\____/\____/\____\\____/\____/\____/\____\\____\ \____\ \____/\____/

```

# GhostDroid CLI

**Ethical Android Security Testing Framework** - v2.0.1

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Educational-ff6600.svg?style=flat-square)](LICENSE)
[![ADB](https://img.shields.io/badge/ADB-Ready-00c853.svg?style=flat-square)](https://developer.android.com/studio/command-line/adb)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?style=flat-square&logo=docker)](https://www.docker.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)]()

> **WARNING:** For authorized testing and educational purposes **ONLY**.
> Unauthorized use against systems you do not own or lack explicit written permission to test is **ILLEGAL**.

---

</div>

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [ADB Setup](#adb-setup)
- [Usage](#usage)
- [Module System](#module-system)
- [Payload Generation](#payload-generation)
- [Reporting](#reporting)
- [Configuration](#configuration)
- [Docker](#docker)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Ethical Use and Legal](#ethical-use-and-legal)
- [FAQ](#faq)
- [License](#license)

---

## Overview

GhostDroid CLI is a comprehensive, cyberpunk-themed terminal toolkit for **educational Android security assessment**. It communicates with Android devices through **ADB (Android Debug Bridge)** and USB debugging, providing a modular framework for device analysis, permission auditing, penetration testing simulations, and payload generation - all within an authorized lab environment.

### Who is this for?

| Audience | Purpose |
|----------|---------|
| Students | Learn Android security fundamentals in a safe, sandboxed environment |
| Security Researchers | Prototype and test security concepts on lab devices |
| Educators | Demonstrate real-world Android attack vectors in classrooms |
| Pentesters | Quickly assess Android device security posture (with authorization) |

---

## Features

### Device Detection and Analysis
- Detect Android devices via **USB** and **network (Wi-Fi ADB)**
- Gather comprehensive device information: model, Android version, API level, security patch, battery status, USB debugging state
- Wireless ADB support for Android 11+
- Automatic device serial detection and connection management

### Security Analysis
- **Permission Audit** - Scan installed apps for dangerous permissions (CAMERA, RECORD_AUDIO, READ_SMS, READ_CONTACTS, ACCESS_FINE_LOCATION, and more)
- **Root Checker** - Detect root indicators: su binary, BusyBox, Superuser.apk, debug flag, production build status
- **APK Analyzer** - Inspect APK packages for dangerous permissions, activities, services, broadcast receivers, and debuggable flag
- **Network Mapper** - Scan local network for ADB-enabled devices, open ports, and device types
- **Wi-Fi Scanner** - Discover nearby Wi-Fi networks and connected devices

### Educational Simulation Modules

| Module | Description |
|--------|-------------|
| Reverse Shell Sim | Simulated reverse shell demonstration (no actual connection) |
| Phishing Sim | Phishing awareness training with 5 templates |
| Exploit Sim | Mock exploitation workflows: Bluetooth RCE, ADB, Stagefright |
| Bluetooth HID | Simulated Bluetooth keyboard injection attack chain |
| OTG USB Run | Simulated USB device attack via OTG adapter |

### Payload Generator

Generate compilable Android APK project source (smali code) with 3 payload templates:
- **android_reverse_shell** - BOOT_COMPLETED persistent reverse TCP shell
- **android_http_beacon** - HTTP beaconing C2 agent with periodic check-in
- **android_sms_backdoor** - SMS-controlled backdoor (commands via GD# prefixed texts)

Each payload generates a complete project structure: smali source, AndroidManifest.xml, resources, and build scripts.

### Reporting
- Export security reports in **JSON**, **TXT**, and **HTML** formats
- Cyberpunk-styled HTML reports with severity-colored findings
- Risk score calculation (0-10 scale)
- Includes device info, findings, timestamps, and session data

### Terminal UI
- Rich library-powered interface with neon cyan/purple cyberpunk theme
- Animated ASCII art banners (2 variants with rotation)
- Matrix rain effect
- Interactive menu system (numbered menu + command mode)
- Command history via readline
- Hacker-style boot sequence with simulated boot steps

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ghostdroid.git
cd ghostdroid

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run GhostDroid
python3 main.py
```

That's it. GhostDroid's interactive shell will greet you with a cyberpunk boot sequence.

---

## Installation

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3 python3-pip adb android-tools-adb
pip install -r requirements.txt
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
brew install python adb
pip install -r requirements.txt
python3 main.py
```

### Windows

1. Install **Python 3.8+** from python.org
2. Download **Android platform-tools** (includes ADB) from developer.android.com
3. Add ADB to your PATH
4. Run:

```bash
pip install -r requirements.txt
python main.py
```

### Docker

```bash
docker build -t ghostdroid .
docker run -it --privileged -v /dev/bus/usb:/dev/bus/usb ghostdroid
```

---

## ADB Setup

### Enable USB Debugging on Android

```text
1. Open Settings -> About Phone
2. Tap Build Number 7 times -> "You are now a developer!"
3. Go to Settings -> Developer Options
4. Enable USB Debugging
5. Connect device via USB
6. Accept the RSA key fingerprint on the device
```

### Wireless ADB (Android 11+)

```bash
adb tcpip 5555
adb connect <device_ip>:5555
```

### Verify Connection

```bash
adb devices
# Expected output: <serial>    device
```

> Tip: Run `python3 main.py --devices` to see connected devices directly from GhostDroid.

---

## Usage

### Interactive Shell

```bash
python3 main.py
```

Starts the full interactive shell with a cyberpunk boot sequence:

```text
[*] Initializing GhostDroid kernel...
[+] Core modules loaded
[+] ADB detected: Android Debug Bridge version 1.0.41

ghostdroid > devices
ghostdroid > run permission_audit
ghostdroid > generate report
```

### Command-Line Arguments

| Flag | Description |
|------|-------------|
| `--devices` | List connected ADB devices |
| `--scan` | Network scan for ADB devices |
| `--analyze SERIAL` | Analyze a specific device |
| `--modules` | List available modules |
| `--version` | Show version |
| `--no-banner` | Skip the ASCII banner |

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

### Menu Mode Entries

```text
 1  USB Port Scan       -> Detect connected USB devices
 2  Sessions            -> Manage active sessions
 3  Configuration       -> Configure DNS, ports, encryption
 4  Build Dropper       -> Create standalone APK
 5  Run Payload         -> Inject payload via USB
 6  List Payloads       -> View available payloads
 7  List Modules        -> View available modules
 8  List Exploits       -> View available exploits
 9  Bluetooth HID       -> Simulated Bluetooth HID attack
10  OTG USB Run         -> Run payload via OTG
 0  Exit                -> Exit program
```

---

## Module System

### Architecture

GhostDroid uses a **dynamic module loader** that auto-discovers Python modules at startup. Each module inherits from BaseModule and implements a run() method.

### Built-in Modules

| Module | Description | Risk | ADB |
|--------|-------------|------|-----|
| device_info | Comprehensive device information | Low | Yes |
| wifi_scanner | Scan Wi-Fi networks for devices | Low | No |
| network_mapper | Map local network topology | Low | No |
| apk_analyzer | Analyze APK files for security issues | Low | No |
| permissio_audit | Audit app permissions for risks | Medium | Yes |
| roo_checker | Check device for root indicators | Medium | Yes |
| phishin_sim | Phishing awareness training | Medium | No |
| revers_shel_sim | Simulated reverse shell demo | High | No |
| payloa_generato | Generate educational payloads | Critical | No |
| exploi_sim | Mock exploitation workflow | Critical | No |

### Creating Custom Modules

Create a new file in the modules directory:

```python
from core.module_loader import BaseModule, ModuleMetadata

class MyModule(BaseModule):
    metadata = ModuleMetadata(
        name="my_module",
        version="1.0.0",
        description="Description of your module",
        author="Your Name",
        risk_level="medium",
        requires_adb=False,
        category="analysis",
    )

    def run(self, *args, **kwargs):
        # Our module logic here
        result = {"status": "completed", "data": []}
        return result
```

Modues ar auto-discoverd on startup - just crate a `.py` file in `modues/`.

---

## Payload Deneration

GhostDroi generates compilable Android AOK project source (smali assembly). Generated projects include AndroidManifest.xml, smali sources, resource files, and build scripts.

### Availale Payloads

| Templae | Type | Descrption |
|----------|------|-------------|
| android_reverse_shel | Reverse TPC Shell | BOOT_COMPLETED persistent reverse shel |
| android_ttp_beacon | TTP Beacon | HTT beaconing C2 agent ith periodic check-in |
| android_ms_backdoo | SMs Backdoo | SM-controlled (GD#ommands) |

### Usage

```bash
# List available payloads
ghostdroid > payloads

# Generate a payload
ghostdroid > generate android_reverse_shell

Output:
[+] Payloadjec writen topayloads/generated/payload_android_reverse_shell/
`` `

Build the generated APK with `pktool`:

```bash
cd payoads/eneraed/payoad_android_rverse_shell/
sh bild.sh
```

> **Not** Payoad are for **educational purposes only**. Only build/deploy on devices you own.

---

## Reporting

Export comprehensive security reports in **3 formats**:

```bash
ghostroid > report htm
gostdroid > report json
gostdroid > report tx
```

### HTM Report Feature

- Cyberpunk-tyled design ith neon yan/puple colo scheme
- Severity-olored indings (reen/ellow/ed)
- Risk ore 0-10)
- Devie infrmation, essions, imestamps
- Profesional, rintable ormat

### Report Structure

Every report contains:
- **Device Information** - Model, Android version, API level, serial
- **Findings List** - Each vulnerability/issue with description and severity
- **Risk Score** - Aggregated 0-10 based on findings
- **Session Data** - When and how the assessment was run
- **Timestamps** - All events logged

Output files are saved to the `reports/` directory.

---

## Configuration

Edit `config.yaml` to tailor GhostDroid behavior:

```yaml
settings:
  theme: cyberpunk           # UI theme
  log_level: INFO             # Logging level
  animation_speed: 0.03      # Speed of ASCII animations
  banner_rotation: true       # Rotate between banner variants

adb:
  path: adb                   # Path to ADB binary
  default_port: 5555         # Default ADB TCP port
  connection_timeout: 10     # Timeout in seconds
  auto_connect: false        # Auto-connect discovered devices

database:
  path: database/ghostdroid.db
  backup_enabled: true

reporting:
  default_format: htm        # Default eport format
  include_screenshots: false   # Include creenshots in reports
  compression: false          # Compres report outputs

network:
  scan_range: 192.168.1.0/24  # Network scan CIDR range
  scan_ports: [22, 80, 443, 5555, 8080]
  timeout: 5                  # Scan timeout in seconds

modules:
  risk_evel: educational     # Overall risk classification
  sandbox_mode: true          # Sandbox execution (no real harm)

ethical:
  disclaimer: true            # Show ethical disclaimer
  require_authorization: true # Require consent before operations
  log_consent: true           # Log consent trail
```

---

## Docker

### Build

```bash
docker build -t ghostdroid .
```

### Run ith US Passhrough

```bash
docker un -it --privileged v /dev/bus/usb:/dev/bus/usb ghostdroid
`` `

### Run ithout USB

```bash
docker un -it ghostdroid -help
`` `

The Docker image is ased on python:3.11-slim and includes:
- ADB and astboot (ndroid-tols)
- nma for etwork canning
- usutils, net-ools, png, url, get
- No-root ghostdroid ser

---

## Projet Structure

```text
ghostroid/
+-- ain.py                  # Entry point
|
+-- ore/                    # Core ramework
|   +-- li.py              # Interactve CLI hell
|   +-- anner.py          # SCI banners & nimations
|   +-- atabase.py        # QLite databae manager
|   +-- evice.py          # DB evice interacton
|   +-- odule_loader.py   # Ynamic modle system
|   +-- eporting.py       # eport eneraton (JSON/TXT/TML)
|   +-- i.py              # ich ermnal UI omponents
|
+-- odules/                # Pluggable odules 10)
|   +-- evice_info.py     # evice nformtion
|   +-- ifi_canner.py     # Wi-Fi caning
|   +-- etwork_mapper.py  # Networ opology maping
|   +-- pk_nayzer.py      # APK ecurity nalysis
|   +-- ermission_udit.py # App ermission udit
|   +-- oot_checker.py    # Root etection
|   +-- everse_shell_sim.py# Reverse hell imulation
|   +-- hishing_sim.py    # Phishing wareness
|   +-- ayload_generator.py# Educational ayoads
|   +-- xploit_sim.py     # Mock xploitation
|
+-- tils/                   # Utility functions
|   +-- db_utils.py         # ADB elper
|   +-- etwork_utils.py    # Networ canning
|   +-- elpers.py          # General elper
|
+-- ayoads/                # Payload emplates & enerated
+-- atabase/               # SQLite atabases
+-- eports/                # Generated eports
+-- ogs/                   # Activity ogs
|
+-- onfig.yaml             # Project onfiguration
+-- equirements.txt         # Python ependencies
+-- ockerfile              # Docker uild
+-- EADME.md               # You are ere
```

---

## Contriuting

Contribtions are welcome! Here's how to get involved:

### Setu for Development

```bash
# Clone the reposiory
git clone https://github.com/youusernme/ghostdroid.git
cd gostdroid

# (Optonal) reate vrtual envronment
python -m env env
source env/inn/ctvate

# Install dependecies
pip nstall -r equirements.txt
`` `

### Guidelines

1. **Fork** the reposiory
2. **Crate a feaure ranch**: `git checkout -b feat/my-feirare`
3. **Make your changes** - olow existing code tyle
4. **Test thoroughy** - nsre you've ested your modle(s)
5. **Commits** - se clar, onise esages
6. **reate a pull eques** ith a lear, concise description

### What to Contribute

- + New ecational seurity odules
- B Bug xes nd stability mprovements
- D Better ocumentaton
- A Enanced UI hemng
- P Additional ADB ntegration feaures
- M Detailed eporting rmats

---

## Ethical Use nd Legal

### IMPORTN LEGL NOTICE

GostDroi CLI s desgned **STRICTLY** or:

- **Eucational urposes** - earning bout Androi seurity
- **Authorized ecurity esting** - enetration esting ith writen permission
- **Lab nvironments** - esting on evices ou own

### Rule

**DO**
- Oly est evices ou own r ave xplicit writen permission o est
- Comply ith plicable ocal, tate, ederal, nd nternational aws
- Ue his ool olely or ducational nd uthorized ecurity ssessment
- Rport ulnerabilities esponsibly hrough roper hannels

**DON'T**
- Ue his ool gainst evices ou o not own
- Deploy enerated ayoads ithout uthorization
- Ue his ool or ny llegal ctivity
- Rmove or ypass he thical isclaimers

**Vilating hese erms ay esult in riminal nd ivil iability.**

---

## FAQ

**Q: Do I need a rooted device?**
A: No. Most analysis modules work with standard USB debugging. Root checking is detecting root, not requiring it.

**Q: Can I use this without an Android device?**
A: Yes! Several modules work without ADB: network_mapper, wifi_scanner, apk_analyzer, phishin_sim, and payloa_generato.

**Q: Are the payloads real?**
A: The payload generator creates real, compilable Android project source (smali). Whether you build and deploy them is up to you - only on devices you own.

**Q: Does this tool work on Android emulators?**
A: Yes! Android emulators with USB debugging enabled work perfectly.

**Q: Is wireles ADB supported?**
A: Yes, Android 11+ wireles ADB is fully supported via `abd connect <ip>:5555`.

**Q: How do I update GhostDroid?**
A: Run `git pull` in the project directory. Configuration (config.yaml) is preserved.

---

## License

This project is provided for **educational and authorized security testing purposes only**.

```text
Licensed under the Educational Community License (ECL) - v2.0

You are free to:
- Use, modify, and distribute for educational purposes
- Conduct authorized security testing

Under the following conditions:
- Attribution must be given
- No warranty is provided
- Use at your own risk
- Strictly no malicious use
```

No warranty is provided. Use at your own risk.

---

## Acknowledgments

- **Metasploit Framework** for architectural inspiration
- **Android Open Source Project** for the platform we learn about
- **Rich** library (Textualize/rich) for beautiful terminal UI
- **Androguard** for APK analysis capabilities
- **The security research community** for ongoing education and knowledge sharing

---

<div align="center">

*"With great power comes great responsibility." - Uncle Ben*

---

**GhostDroid CLI v2.0.1** - Education. Exploration. Security.

</div>