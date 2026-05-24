import os
import re
import json
import hashlib
import random
import string
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


def generate_session_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = "".join(random.choices(string.hexdigits, k=6))
    return f"ghost_{timestamp}_{random_suffix}"


def generate_device_id(serial: str) -> str:
    return hashlib.md5(serial.encode()).hexdigest()[:12]


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-_\. ]", "_", name)


def read_file(path: str) -> Optional[str]:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        return None


def write_file(path: str, content: str) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return True
    except Exception:
        return False


def load_json(path: str) -> Optional[Dict]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_json(path: str, data: Dict) -> bool:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception:
        return False


def calculate_risk_score(findings: List[Dict]) -> float:
    weights = {
        "critical": 10.0,
        "high": 7.5,
        "medium": 5.0,
        "low": 2.5,
        "info": 0.0,
    }
    if not findings:
        return 0.0
    total = sum(weights.get(f.get("severity", "info"), 0) for f in findings)
    return min(10.0, total / max(len(findings), 1) * 1.5)


def truncate_string(s: str, max_len: int = 50) -> str:
    return s[:max_len] + "..." if len(s) > max_len else s


def bytes_to_human(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def is_valid_ip(ip: str) -> bool:
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(part) <= 255 for part in ip.split("."))


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def parse_adb_devices_output(output: str) -> List[Dict[str, str]]:
    devices = []
    for line in output.strip().split("\n")[1:]:
        if line.strip() and "device" in line:
            parts = line.split()
            device = {"serial": parts[0], "state": "device"}
            for part in parts[1:]:
                if ":" in part:
                    k, v = part.split(":", 1)
                    device[k] = v
            devices.append(device)
    return devices
