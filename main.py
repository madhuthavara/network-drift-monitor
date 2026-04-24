import time
import yaml
from rich.console import Console
from rich.table import Table

from nautobot.client import NautobotClient
from collectors.bgp import get_bgp_neighbors
from collectors.interfaces import get_interface_states
from drift.comparator import compare_bgp_state, compare_interface_state
from prometheus.exporter import (
    publish_bgp_drift,
    publish_interface_drift,
    start_exporter,
)

console = Console()


def load_config(path: str = "config/devices.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def print_drift_report(device_name: str, bgp_drift: list, intf_drift: list):
    console.print(f"\n[bold cyan]Device: {device_name}[/bold cyan]")

    bgp_table = Table(title="BGP Drift", show_lines=True)
    bgp_table.add_column("Peer IP")
    bgp_table.add_column("Expected")
    bgp_table.add_column("Actual")
    bgp_table.add_column("Drifted")

    for r in bgp_drift:
        color = "red" if r["drifted"] else "green"
        bgp_table.add_row(
            r["peer_ip"], r["expected"], r["actual"],
            f"[{color}]{'YES' if r['drifted'] else 'NO'}[/{color}]"
        )
    console.print(bgp_table)

    intf_table = Table(title="Interface Drift", show_lines=True)
    intf_table.add_column("Interface")
    intf_table.add_column("Expected")
    intf_table.add_column("Actual")
    intf_table.add_column("Drifted")

    for r in intf_drift:
        color = "red" if r["drifted"] else "green"
        intf_table.add_row(
            r["name"], r["expected"], r["actual"],
            f"[{color}]{'YES' if r['drifted'] else 'NO'}[/{color}]"
        )
    console.print(intf_table)


def run_once(config: dict, nautobot: NautobotClient):
    for device in config["devices"]:
        name = device["name"]
        console.print(f"[bold]Polling {name}...[/bold]")

        # Pull intended state from Nautobot
        intended_bgp = nautobot.get_intended_bgp_peers(name)
        intended_intf = nautobot.get_intended_interfaces(name)

        # Pull live state from device
        live_bgp = get_bgp_neighbors(device)
        live_intf = get_interface_states(device)

        # Compare
        bgp_drift = compare_bgp_state(intended_bgp, live_bgp)
        intf_drift = compare_interface_state(intended_intf, live_intf)

        # Publish to Prometheus
        publish_bgp_drift(name, bgp_drift)
        publish_interface_drift(name, intf_drift)

        # Print to console
        print_drift_report(name, bgp_drift, intf_drift)


def main():
    config = load_config()
    nautobot = NautobotClient(
        url=config["nautobot"]["url"],
        token=config["nautobot"]["token"],
    )
    scrape_interval = config["prometheus"].get("scrape_interval", 60)
    prometheus_port = config["prometheus"].get("port", 8080)

    start_exporter(prometheus_port)

    console.print(f"[bold green]Network Drift Monitor started. Polling every {scrape_interval}s.[/bold green]")

    while True:
        run_once(config, nautobot)
        time.sleep(scrape_interval)


if __name__ == "__main__":
    main()
