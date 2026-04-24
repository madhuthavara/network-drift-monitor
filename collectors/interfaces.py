import re
from netmiko import ConnectHandler


def get_interface_states(device: dict) -> list:
    """
    Connects to a device via Netmiko and pulls live interface up/down state.
    Returns list of dicts with interface name and current state.
    """
    connection_params = {
        "device_type": device["device_type"],
        "host": device["hostname"],
        "username": device["username"],
        "password": device["password"],
    }

    interfaces = []

    try:
        with ConnectHandler(**connection_params) as conn:
            output = conn.send_command("show interface status")
            interfaces = _parse_interface_status(output)
    except Exception as e:
        print(f"[ERROR] Could not connect to {device['name']}: {e}")

    return interfaces


def _parse_interface_status(output: str) -> list:
    """
    Parses NX-OS interface status output.
    Extracts interface name and connected/notconnect/disabled state.
    """
    interfaces = []
    # Match lines like: Eth1/1   --   connected   trunk  ...
    pattern = re.compile(
        r"^(Eth\S+|mgmt\S+)\s+\S*\s+(connected|notconnect|disabled|err-disabled)",
        re.IGNORECASE | re.MULTILINE,
    )
    for match in pattern.finditer(output):
        interfaces.append({
            "name": match.group(1),
            "current_state": match.group(2).lower(),
        })
    return interfaces
