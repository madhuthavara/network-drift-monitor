import requests


class NautobotClient:
    """
    Client for querying Nautobot as the source of truth.
    Retrieves intended BGP peer state and interface state per device.
    """

    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint: str) -> dict:
        response = requests.get(
            f"{self.url}/api/{endpoint}",
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_intended_bgp_peers(self, device_name: str) -> list:
        """
        Returns list of intended BGP peers for a device from Nautobot.
        Expected custom field or plugin: bgp_sessions with peer_ip and expected_state.
        """
        data = self._get(f"plugins/bgp/sessions/?device={device_name}")
        peers = []
        for session in data.get("results", []):
            peers.append({
                "peer_ip": session.get("remote_address"),
                "expected_state": session.get("status", {}).get("value", "established"),
                "peer_asn": session.get("remote_as"),
            })
        return peers

    def get_intended_interfaces(self, device_name: str) -> list:
        """
        Returns list of intended interface states for a device from Nautobot.
        """
        data = self._get(f"dcim/interfaces/?device={device_name}")
        interfaces = []
        for intf in data.get("results", []):
            interfaces.append({
                "name": intf.get("name"),
                "expected_enabled": intf.get("enabled", True),
            })
        return interfaces
