from typing import List


def compare_bgp_state(intended: list, live: list) -> list:
    """
    Compares intended BGP peers from Nautobot against live state from device.
    Returns list of drift findings.
    """
    drift = []
    live_map = {n["peer_ip"]: n["current_state"] for n in live}

    for peer in intended:
        peer_ip = peer["peer_ip"]
        expected = peer["expected_state"].lower()

        if peer_ip not in live_map:
            drift.append({
                "type": "bgp",
                "peer_ip": peer_ip,
                "expected": expected,
                "actual": "missing",
                "drifted": True,
            })
        else:
            actual = live_map[peer_ip]
            drift.append({
                "type": "bgp",
                "peer_ip": peer_ip,
                "expected": expected,
                "actual": actual,
                "drifted": actual != expected,
            })

    return drift


def compare_interface_state(intended: list, live: list) -> list:
    """
    Compares intended interface states from Nautobot against live state from device.
    Returns list of drift findings.
    """
    drift = []
    live_map = {i["name"]: i["current_state"] for i in live}

    for intf in intended:
        name = intf["name"]
        expected_enabled = intf["expected_enabled"]
        expected_state = "connected" if expected_enabled else "disabled"

        if name not in live_map:
            drift.append({
                "type": "interface",
                "name": name,
                "expected": expected_state,
                "actual": "missing",
                "drifted": True,
            })
        else:
            actual = live_map[name]
            is_drifted = (expected_enabled and actual != "connected") or \
                         (not expected_enabled and actual == "connected")
            drift.append({
                "type": "interface",
                "name": name,
                "expected": expected_state,
                "actual": actual,
                "drifted": is_drifted,
            })

    return drift
