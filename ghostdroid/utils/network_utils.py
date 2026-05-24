import socket
import subprocess
import re
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_network_range() -> str:
    ip = get_local_ip()
    parts = ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def scan_port(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception:
        return False


def scan_device(host: str, ports: List[int] = None) -> Optional[Dict]:
    if ports is None:
        ports = [22, 80, 443, 5555, 8080, 8443]
    open_ports = []
    for port in ports:
        if scan_port(host, port):
            open_ports.append(port)

    if open_ports:
        try:
            hostname = socket.gethostbyaddr(host)[0]
        except Exception:
            hostname = "Unknown"
        return {
            "ip": host,
            "hostname": hostname,
            "open_ports": open_ports,
            "adb_available": 5555 in open_ports,
        }
    return None


def network_scan(subnet: str = None, max_workers: int = 20) -> List[Dict]:
    if subnet is None:
        subnet = get_network_range()

    base_ip = subnet.split("/")[0]
    parts = base_ip.split(".")
    network = f"{parts[0]}.{parts[1]}.{parts[2]}"

    devices = []

    def check_host(host_ip: str) -> Optional[Dict]:
        return scan_device(host_ip)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(check_host, f"{network}.{i}"): i
            for i in range(1, 255)
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    devices.append(result)
            except Exception:
                continue

    return sorted(devices, key=lambda d: [int(x) for x in d["ip"].split(".")])


def ping_host(host: str) -> bool:
    try:
        param = "-n" if subprocess.os.name == "nt" else "-c"
        result = subprocess.run(
            ["ping", param, "1", "-W", "1", host],
            capture_output=True, timeout=3
        )
        return result.returncode == 0
    except Exception:
        return False


def get_mac_address(ip: str) -> Optional[str]:
    try:
        if subprocess.os.name == "nt":
            result = subprocess.run(
                ["arp", "-a", ip], capture_output=True, text=True, timeout=5
            )
            match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", result.stdout)
        else:
            result = subprocess.run(
                ["arp", "-n", ip], capture_output=True, text=True, timeout=5
            )
            match = re.search(r"([0-9a-f]{2}[:-]){5}([0-9a-f]{2})", result.stdout)
        return match.group(0) if match else None
    except Exception:
        return None


def identify_device_type(open_ports: List[int]) -> str:
    if 5555 in open_ports:
        return "Android Device"
    if 22 in open_ports:
        return "Linux/SSH Server"
    if 80 in open_ports or 443 in open_ports:
        return "Web Server"
    if 8080 in open_ports:
        return "HTTP Proxy/Server"
    return "Unknown Device"


def bulk_ping(hosts: List[str]) -> List[str]:
    alive = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(ping_host, host): host for host in hosts}
        for future in as_completed(futures):
            host = futures[future]
            try:
                if future.result():
                    alive.append(host)
            except Exception:
                continue
    return sorted(alive, key=lambda ip: [int(x) for x in ip.split(".")])
