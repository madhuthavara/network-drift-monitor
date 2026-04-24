# network-drift-monitor

A Python-based network state drift detection tool that compares live BGP neighbor and interface state against Nautobot as the source of truth, exposes metrics via a Prometheus endpoint, and visualizes results in Grafana.

## What it does

- Connects to network devices (Cisco NX-OS) via Netmiko
- Queries Nautobot API for intended BGP peer state and interface state
- Compares live state against intended state and flags any drift
- Exposes drift metrics via a Prometheus HTTP endpoint
- Includes a Grafana dashboard for visualization

## Architecture

```
Nautobot (source of truth)
        |
        v
  comparator.py  <---  Netmiko (live device state)
        |
        v
 Prometheus exporter  -->  Grafana dashboard
```

## Setup

```bash
pip install -r requirements.txt
```

Edit `config/devices.yaml` with your device inventory, Nautobot URL, and token.

## Run

```bash
python main.py
```

Prometheus metrics will be available at `http://localhost:8080/metrics`

Import `grafana/dashboard.json` into your Grafana instance and point it at your Prometheus datasource.

## Metrics exposed

| Metric | Description |
|---|---|
| `network_bgp_peer_drift` | BGP peer drift per device and peer IP (1=drifted, 0=ok) |
| `network_interface_drift` | Interface drift per device and interface (1=drifted, 0=ok) |
| `network_drift_total` | Total drifted resource count per device and type |

## Supported platforms

- Cisco NX-OS (leaf-spine, data center)
- Extensible to Arista EOS, Cisco IOS-XE via Netmiko device_type

## Use case

Designed for large-scale multi-vendor environments where Nautobot is the authoritative source of truth. Identifies configuration and state drift before it causes outages, and feeds observability pipelines for SRE and NOC teams.
