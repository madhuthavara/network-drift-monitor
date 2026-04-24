import re
from netmiko import ConnectHandler


def get_bgp_neighbors(device: dict) -> list:
    """
    Connects to a device via Netmiko and pulls live BGP neighbor state.
    Returns list of dicts with peer_ip and current state.
    """
    connection_params = {
        "device_type": device["device_type"],
        "host": device["hostname"],
        "username": device["username"],
        "password": device["password"],
    }

    neighbors = []

    try:
        with ConnectHandler(**connection_params) as conn:
            # Cisco NX-OS BGP summary output
            output = conn.send_command("show bgp ipv4 unicast summary")
            neighbors = _parse_bgp_summary(output)
    except Exception as e:
        print(f"[ERROR] Could not connect to {device['name']}: {e}")

    return neighbors


def _parse_bgp_summary(output: str) -> list:
    """
    Parses NX-OS BGP summary output.
    Extracts peer IP and session state (Established or Idle/Active).
    """
    neighbors = []
    # Match lines like: 10.0.0.1   4  65001  ...  Established
    pattern = re.compile(
        r"(\d+\.\d+\.\d+\.\d+)\s+\d+\s+(\d+).*?(Established|Idle|Active|Connect|OpenSent|OpenConfirm)",
        re.IGNORECASE,
    )
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            neighbors.append({
                "peer_ip": match.group(1),
                "peer_asn": match.group(2),
                "current_state": match.group(3).lower(),
            })
    return neighbors
