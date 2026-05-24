import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from jinja2 import Template

from core.ui import print_status, console

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


class ReportGenerator:
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def generate_json(self, data: Dict, filename: str = None) -> str:
        if not filename:
            filename = f"report_{self.session_id or datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(REPORTS_DIR, filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return path

    def generate_txt(self, data: Dict, filename: str = None) -> str:
        if not filename:
            filename = f"report_{self.session_id or datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        path = os.path.join(REPORTS_DIR, filename)

        lines = [
            "=" * 70,
            "  GHOSTDROID SECURITY ASSESSMENT REPORT",
            "=" * 70,
            f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Session ID: {self.session_id or 'N/A'}",
            "=" * 70,
            "",
        ]

        if "device" in data:
            dev = data["device"]
            lines.append("[DEVICE INFORMATION]")
            lines.append("-" * 40)
            for k, v in dev.items():
                lines.append(f"  {k.replace('_', ' ').title():25s}: {v}")
            lines.append("")

        if "findings" in data:
            findings = data["findings"]
            critical = sum(1 for f in findings if f.get("severity") == "critical")
            high = sum(1 for f in findings if f.get("severity") == "high")
            medium = sum(1 for f in findings if f.get("severity") == "medium")
            low = sum(1 for f in findings if f.get("severity") == "low")

            lines.append("[FINDINGS SUMMARY]")
            lines.append("-" * 40)
            lines.append(f"  Total Findings: {len(findings)}")
            lines.append(f"  Critical:       {critical}")
            lines.append(f"  High:           {high}")
            lines.append(f"  Medium:         {medium}")
            lines.append(f"  Low:            {low}")
            lines.append("")

            for i, finding in enumerate(findings, 1):
                lines.append(f"  #{i} [{finding.get('severity', 'info').upper()}] "
                            f"{finding.get('finding_type', 'N/A')}")
                lines.append(f"      {finding.get('description', '')}")
                lines.append("")

        if "risk_score" in data:
            lines.append(f"[OVERALL RISK SCORE: {data['risk_score']}/10]")
            lines.append("")

        lines.append("=" * 70)
        lines.append("  GhostDroid CLI - Ethical Security Testing Framework")
        lines.append("  For authorized testing and educational purposes only")
        lines.append("=" * 70)

        with open(path, "w") as f:
            f.write("\n".join(lines))
        return path

    def generate_html(self, data: Dict, filename: str = None) -> str:
        if not filename:
            filename = f"report_{self.session_id or datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        path = os.path.join(REPORTS_DIR, filename)

        template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GhostDroid Security Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0f;
            color: #00ffcc;
            padding: 30px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .header {
            border: 2px solid #ff00ff;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            background: linear-gradient(180deg, #0a0a0f 0%, #1a0a2e 100%);
        }
        .header h1 { color: #ff00ff; font-size: 28px; text-shadow: 0 0 20px #ff00ff; }
        .header .subtitle { color: #00ffcc; margin-top: 10px; }
        .section {
            border: 1px solid #00ffcc;
            padding: 20px;
            margin-bottom: 20px;
            background: rgba(0, 255, 204, 0.02);
        }
        .section h2 {
            color: #ff00ff;
            border-bottom: 1px solid #00ffcc;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .info-item { padding: 8px; border-bottom: 1px solid rgba(0,255,204,0.1); }
        .info-item .label { color: #ff00ff; }
        .info-item .value { color: #00ffcc; float: right; }
        .finding {
            padding: 12px;
            margin: 8px 0;
            border-left: 4px solid #00ffcc;
            background: rgba(0, 255, 204, 0.03);
        }
        .finding.critical { border-left-color: #ff0044; }
        .finding.high { border-left-color: #ff6600; }
        .finding.medium { border-left-color: #ffcc00; }
        .finding.low { border-left-color: #00ffcc; }
        .finding .severity {
            display: inline-block;
            padding: 2px 10px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .severity.critical { background: #ff0044; color: #fff; }
        .severity.high { background: #ff6600; color: #fff; }
        .severity.medium { background: #ffcc00; color: #000; }
        .severity.low { background: #00ffcc; color: #000; }
        .score {
            font-size: 48px;
            text-align: center;
            padding: 20px;
            color: #ff00ff;
            text-shadow: 0 0 30px #ff00ff;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #333;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⬡ GHOSTDROID SECURITY REPORT</h1>
            <div class="subtitle">Generated: {{ timestamp }}</div>
            <div class="subtitle">Session: {{ session_id }}</div>
        </div>

        {% if device %}
        <div class="section">
            <h2>► DEVICE INFORMATION</h2>
            <div class="info-grid">
                {% for key, value in device.items() %}
                <div class="info-item">
                    <span class="label">{{ key.replace('_', ' ').title() }}</span>
                    <span class="value">{{ value }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        {% if findings %}
        <div class="section">
            <h2>► FINDINGS ({{ findings|length }} total)</h2>
            {% set counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0} %}
            {% for f in findings %}
                {% set _ = counts.update({f.severity: counts[f.severity] + 1}) %}
            {% endfor %}
            <p>Critical: {{ counts.critical }} | High: {{ counts.high }} | Medium: {{ counts.medium }} | Low: {{ counts.low }}</p>
            {% for f in findings %}
            <div class="finding {{ f.severity }}">
                <span class="severity {{ f.severity }}">{{ f.severity.upper() }}</span>
                <strong>{{ f.finding_type }}</strong>
                <p>{{ f.description }}</p>
                {% if f.details %}<pre>{{ f.details }}</pre>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if risk_score is defined %}
        <div class="section">
            <h2>► RISK ASSESSMENT</h2>
            <div class="score">{{ risk_score }}/10</div>
        </div>
        {% endif %}

        <div class="footer">
            GhostDroid CLI v2.0.1 - Ethical Security Testing Framework<br>
            For authorized testing and educational purposes only
        </div>
    </div>
</body>
</html>
        """)

        html = template.render(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            session_id=self.session_id or "N/A",
            device=data.get("device", {}),
            findings=data.get("findings", []),
            risk_score=data.get("risk_score", "N/A"),
        )

        with open(path, "w") as f:
            f.write(html)
        return path

    def generate_report(self, data: Dict, fmt: str = "html") -> str:
        generators = {
            "json": self.generate_json,
            "txt": self.generate_txt,
            "html": self.generate_html,
        }
        gen = generators.get(fmt, self.generate_html)
        path = gen(data)
        print_status(f"Report generated: {path}", "success")
        return path
