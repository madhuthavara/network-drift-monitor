# Running network-drift-monitor on Chromebook

## Step 1 — Open Linux terminal
Open the Terminal app on your Chromebook (it runs Debian inside Penguin).

## Step 2 — Install Python and pip
```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```

## Step 3 — Unzip and enter the project
```bash
cd ~/Downloads
unzip network-drift-monitor.zip
cd network-drift-monitor
```

## Step 4 — Install dependencies
```bash
pip3 install -r requirements.txt --break-system-packages
```

## Step 5 — Edit your device config
```bash
nano config/devices.yaml
```
Update with your real device IPs, credentials, Nautobot URL, and token.
Save with `Ctrl+O`, exit with `Ctrl+X`.

## Step 6 — Run the tool
```bash
python3 main.py
```

## Step 7 — Check Prometheus metrics
Open Chrome and go to:
```
http://localhost:8080/metrics
```
