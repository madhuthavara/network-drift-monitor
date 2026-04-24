from prometheus_client import Gauge, start_http_server
import time

# Gauge: 1 = drifted, 0 = compliant
bgp_drift_gauge = Gauge(
    "network_bgp_peer_drift",
    "BGP peer drift detected vs Nautobot intended state (1=drifted, 0=ok)",
    ["device", "peer_ip", "expected_state", "actual_state"],
)

interface_drift_gauge = Gauge(
    "network_interface_drift",
    "Interface drift detected vs Nautobot intended state (1=drifted, 0=ok)",
    ["device", "interface", "expected_state", "actual_state"],
)

drift_summary_gauge = Gauge(
    "network_drift_total",
    "Total number of drifted resources across all devices",
    ["device", "type"],
)


def publish_bgp_drift(device_name: str, drift_results: list):
    """Publish BGP drift findings to Prometheus gauges."""
    drifted_count = 0
    for result in drift_results:
        value = 1 if result["drifted"] else 0
        bgp_drift_gauge.labels(
            device=device_name,
            peer_ip=result["peer_ip"],
            expected_state=result["expected"],
            actual_state=result["actual"],
        ).set(value)
        if result["drifted"]:
            drifted_count += 1
    drift_summary_gauge.labels(device=device_name, type="bgp").set(drifted_count)


def publish_interface_drift(device_name: str, drift_results: list):
    """Publish interface drift findings to Prometheus gauges."""
    drifted_count = 0
    for result in drift_results:
        value = 1 if result["drifted"] else 0
        interface_drift_gauge.labels(
            device=device_name,
            interface=result["name"],
            expected_state=result["expected"],
            actual_state=result["actual"],
        ).set(value)
        if result["drifted"]:
            drifted_count += 1
    drift_summary_gauge.labels(device=device_name, type="interface").set(drifted_count)


def start_exporter(port: int):
    """Start the Prometheus HTTP metrics endpoint."""
    start_http_server(port)
    print(f"[INFO] Prometheus exporter running on port {port}")
