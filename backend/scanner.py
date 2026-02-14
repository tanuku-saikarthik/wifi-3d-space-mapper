import subprocess
import time
import re
import logging

log = logging.getLogger("WiFiMatrix")

RSSI_RE = re.compile(r"Signal\s*:\s*(\d+)%")
BSSID_RE = re.compile(r"BSSID\s+\d+\s*:\s*([0-9A-Fa-f:]+)")
FREQ_RE = re.compile(r"Channel\s*:\s*(\d+)")

# def scan_wifi():
#     results = []

#     try:
#         proc = subprocess.run(
#             ["netsh", "wlan", "show", "networks", "mode=bssid"],
#             capture_output=True,
#             text=True,
#             timeout=5
#         )

#         if proc.returncode != 0:
#             raise RuntimeError("netsh failed")

#         lines = proc.stdout.splitlines()
#         current_bssid = None
#         current_channel = None

#         for line in lines:
#             line = line.strip()

#             bssid_match = BSSID_RE.search(line)
#             if bssid_match:
#                 current_bssid = bssid_match.group(1)
#                 continue

#             signal_match = RSSI_RE.search(line)
#             if signal_match and current_bssid:
#                 signal_pct = int(signal_match.group(1))
#                 rssi = signal_pct / 2 - 100  # Windows heuristic
#                 continue

#             freq_match = FREQ_RE.search(line)
#             if freq_match and current_bssid:
#                 channel = int(freq_match.group(1))
#                 freq = 2400 if channel <= 14 else 5000

#                 results.append((current_bssid, rssi, freq))
#                 current_bssid = None

#         if results:
#             log.info(f"OS WiFi scan successful | APs: {len(results)}")
#             return results

#         raise RuntimeError("No APs parsed")

#     except Exception as e:
#         log.warning(f"Using synthetic WiFi data (OS scan unavailable): {e}")

#         # fallback (keeps system alive)
#         import random
#         return [
#             (f"AP_{i}", -40 - random.random()*30, random.choice([2400, 5000]))
#             for i in range(30)
#         ]
import subprocess
import re
import logging
import random
import os

log = logging.getLogger("WiFiMatrix")

SSID_RE = re.compile(r"SSID\s+\d+\s*:\s*(.+)")
BSSID_RE = re.compile(r"BSSID\s+\d+\s*:\s*([0-9A-Fa-f:]+)")
SIGNAL_RE = re.compile(r"Signal\s*:\s*(\d+)%")
CHANNEL_RE = re.compile(r"Channel\s*:\s*(\d+)")
SECURITY_RE = re.compile(r"Authentication\s*:\s*(.+)")
CIPHER_RE = re.compile(r"Encryption\s*:\s*(.+)")

def scan_wifi():
    results = []
    use_synthetic = os.getenv("WIFI_SYNTHETIC", "0") == "1"

    try:
        if use_synthetic:
            raise RuntimeError("Synthetic mode forced by WIFI_SYNTHETIC=1")

        proc = subprocess.run(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if proc.returncode != 0:
            raise RuntimeError(f"netsh failed with exit code {proc.returncode}")

        ssid = None
        security = None
        cipher = None
        bssid = None
        signal = None
        channel = None

        for line in proc.stdout.splitlines():
            line = line.strip()

            if m := SSID_RE.match(line):
                ssid = m.group(1)

            elif m := SECURITY_RE.match(line):
                security = m.group(1)

            elif m := CIPHER_RE.match(line):
                cipher = m.group(1)

            elif m := BSSID_RE.match(line):
                bssid = m.group(1)

            elif m := SIGNAL_RE.match(line):
                signal_pct = int(m.group(1))
                rssi = signal_pct / 2 - 100

            elif m := CHANNEL_RE.match(line):
                channel = int(m.group(1))
                band = 2400 if channel <= 14 else 5000

                results.append({
                    "bssid": bssid,
                    "ssid": ssid,
                    "rssi": rssi,
                    "signal": signal_pct,
                    "channel": channel,
                    "band": band,
                    "security": security,
                    "cipher": cipher
                })

        return results

    except Exception as e:
        log.warning(f"WiFi scan failed, using synthetic data: {e}")
        synthetic = []
        for i in range(24):
            signal = random.randint(35, 95)
            channel = random.choice([1, 6, 11, 36, 40, 44, 149, 157])
            band = 2400 if channel <= 14 else 5000
            rssi = signal / 2 - 100
            synthetic.append({
                "bssid": f"DE:MO:AP:{i:02X}:{random.randint(0,255):02X}:{random.randint(0,255):02X}",
                "ssid": f"DemoWiFi-{i:02d}",
                "rssi": rssi,
                "signal": signal,
                "channel": channel,
                "band": band,
                "security": random.choice(["WPA2-Personal", "WPA3-Personal", "Open"]),
                "cipher": random.choice(["CCMP", "GCMP", "None"]),
            })
        return synthetic
