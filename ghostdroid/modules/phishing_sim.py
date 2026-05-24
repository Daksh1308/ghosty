import time
import random
from typing import Dict, Any
from core.module_loader import BaseModule, ModuleMetadata
from core.ui import print_status, console, print_panel, show_progress


PHISHING_TEMPLATES = [
    {
        "name": "Google Account Alert",
        "platform": "Google",
        "vector": "Email",
        "description": "Fake security alert asking to verify account credentials",
    },
    {
        "name": "Banking Notification",
        "platform": "Financial",
        "vector": "SMS",
        "description": "Fake bank alert about suspicious transaction requiring login",
    },
    {
        "name": "Social Media Warning",
        "platform": "Social Media",
        "vector": "In-App Notification",
        "description": "Fake account compromise warning with malicious link",
    },
    {
        "name": "Package Delivery",
        "platform": "Logistics",
        "vector": "SMS",
        "description": "Fake delivery notification with tracking link",
    },
    {
        "name": "Security Update Required",
        "platform": "System",
        "vector": "System Notification",
        "description": "Fake Android security update prompt with malware payload",
    },
]


class PhishingSimModule(BaseModule):
    metadata = ModuleMetadata(
        name="phishing_sim",
        version="1.0.0",
        description="Phishing awareness simulation for educational training",
        author="GhostDroid",
        risk_level="medium",
        requires_adb=False,
        category="education",
    )

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        console.print("[bold cyan]╔══ Phishing Awareness Simulation ══╗[/]")
        console.print("[dim]Educational demonstration of common phishing vectors[/]\n")

        template_name = kwargs.get("template")
        if template_name:
            template = next((t for t in PHISHING_TEMPLATES
                           if t["name"].lower() == template_name.lower()), None)
            if not template:
                print_status(f"Template '{template_name}' not found", "warn")
                template = random.choice(PHISHING_TEMPLATES)
        else:
            template = random.choice(PHISHING_TEMPLATES)

        results = {
            "simulation_type": "phishing_awareness",
            "template_used": template,
            "scenario_steps": [],
            "findings": [],
        }

        console.print(f"\n[bold yellow]Scenario: {template['name']}[/]")
        print_status(f"Platform: {template['platform']}", "info")
        print_status(f"Vector: {template['vector']}", "info")
        print_status(f"Description: {template['description']}", "info")

        print_panel(
            "[bold red]⚠ PHISHING SCENARIO ⚠[/]\n\n"
            f"You receive a {template['vector'].lower()} pretending to be from "
            f"{template['platform']}. It claims there is an urgent security issue "
            f"and requires you to click a link and enter your credentials.\n\n"
            f"[yellow]Red flags to identify:[/]\n"
            f"• Sense of urgency / pressure to act quickly\n"
            f"• Generic greeting instead of personal salutation\n"
            f"• Suspicious sender address/phone number\n"
            f"• Requests for personal information\n"
            f"• Poor grammar or spelling mistakes\n"
            f"• Mismatched or suspicious URLs",
            title="Phishing Scenario",
            style="yellow",
        )

        console.print("\n[bold cyan][*] Simulating phishing attack chain...[/]")
        show_progress("Attack chain simulation", 2.0)

        steps = [
            f"Attacker crafts fake {template['platform']} notification",
            f"Phishing message delivered via {template['vector']}",
            "Victim receives urgent security alert",
            "Social engineering triggers urgency response",
            "Victim clicks embedded link",
            "Fake login page captures credentials",
            "Stolen credentials sent to attacker server",
            "Attacker gains unauthorized access",
        ]

        for i, step in enumerate(steps, 1):
            time.sleep(0.3)
            print_status(f"Step {i}: {step}", "arrow")
            results["scenario_steps"].append(step)

            if i == 5:
                print_status("[bold red]Victim clicked the malicious link![/]", "error")
            if i == 7:
                print_status("[bold red]Credentials compromised![/]", "error")

        console.print("\n[bold green][+] Simulation complete[/]")
        print_panel(
            "[bold yellow]Key Takeaways:[/]\n"
            "• Always verify the sender's identity through alternative channels\n"
            "• Never click links in unsolicited messages\n"
            "• Check URLs carefully before entering credentials\n"
            "• Enable two-factor authentication on all accounts\n"
            "• Report phishing attempts to your security team\n\n"
            "[dim]This simulation demonstrates how easily users can be deceived.[/]",
            title="Security Awareness",
            style="green",
        )

        results["findings"] = [
            {
                "type": "phishing_simulation",
                "severity": "high",
                "description": f"Demonstrated {template['name']} phishing vector",
                "mitigation": "User awareness training and email filtering",
            }
        ]

        return results
