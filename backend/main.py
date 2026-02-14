import asyncio
import json
import time
import logging
import websockets
import numpy as np

from scanner import scan_wifi
from signals import SignalBuffer
from correlation import pearson, corr_to_dist
from embedding import mds

# ---------------- LOGGING SETUP ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("WiFiMatrix")
# ------------------------------------------------

buffers = {}
positions = None
iteration = 0

async def producer(ws):
    global positions, iteration

    log.info("WebSocket client connected")

    while True:
        iteration += 1
        start_time = time.time()

        # ---- SCAN ----
        scans = scan_wifi()
        log.info(f"[{iteration}] Scan complete | APs detected: {len(scans)}")

        # ---- BUFFER UPDATE ----
        new_aps = 0
        for ap in scans:
            bssid = ap["bssid"]

            if bssid not in buffers:
                buffers[bssid] = {
                    "buf": SignalBuffer(),
                    "info": ap   # store all metadata
                }

            buffers[bssid]["buf"].add(ap["rssi"])

                # if bssid not in buffers:
                #     buffers[bssid] = {
                #         "buf": SignalBuffer(),
                #         "freq": freq
                #     }
                #     new_aps += 1
                #     log.info(f"NEW AP discovered → {bssid}")

                # buffers[bssid]["buf"].add(rssi)

        if new_aps:
            log.info(f"{new_aps} new AP(s) added | Total tracked: {len(buffers)}")

        aps = list(buffers.keys())
        n = len(aps)

        if n == 0:
            log.warning("No APs tracked yet, skipping iteration")
            await asyncio.sleep(1)
            continue

        # ---- SIGNAL STATS ----
        zscores = []
        valid_series = 0
        for a in aps:
            z = buffers[a]["buf"].zscore()
            if z is not None:
                valid_series += 1
            zscores.append(z)

        log.info(f"Signal buffers ready | Valid time-series: {valid_series}/{n}")

        # ---- CORRELATION ----
        corr = [[0.0]*n for _ in range(n)]
        dist = [[0.0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                r = pearson(zscores[i], zscores[j])
                corr[i][j] = r
                dist[i][j] = corr_to_dist(r)

        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                if corr[i][j] > 0.85:
                    edges.append([i, j, corr[i][j]])

        log.info(
            f"Correlation matrix computed | Size: {n}x{n} | "
            f"Strong edges: {len(edges)}"
        )

        # ---- EMBEDDING ----
        #positions = mds(dist, positions)
        # ---- EMBEDDING (SIZE-SAFE) ----
        if positions is not None:
            prev_n = positions.shape[0]
            if prev_n < n:
                log.info(f"Embedding expanded: {prev_n} → {n}")
                # initialize new points near origin
                new_pts = 0.1 * np.random.randn(n - prev_n, 3)
                positions = np.vstack([positions, new_pts])
            elif prev_n > n:
                log.info(f"Embedding shrunk: {prev_n} → {n}")
                positions = positions[:n]

        positions = mds(dist, positions)
        log.info("3D embedding updated (Incremental MDS)")

        log.info("3D embedding updated (Incremental MDS)")

        # ---- PAYLOAD ----
        # ---- PAYLOAD ----
        payload = {
    "nodes": [],
    "edges": edges
}

        for i, bssid in enumerate(aps):
            buf = buffers[bssid]["buf"]
            info = buffers[bssid]["info"]

            payload["nodes"].append({
                "id": bssid,
                "ssid": info["ssid"],
                "rssi": info["rssi"],
                "signal": info["signal"],
                "channel": info["channel"],
                "band": info["band"],
                "security": info["security"],
                "cipher": info["cipher"],
                "pos": positions[i].tolist(),
                "variance": buf.variance()
            })


        # ---- SEND ----
        await ws.send(json.dumps(payload))

        elapsed = (time.time() - start_time) * 1000

        log.info(
            f"Frame sent → Nodes: {n} | "
            f"Latency: {elapsed:.1f} ms"
        )

        await asyncio.sleep(1)

async def handler(ws):
    try:
        await producer(ws)
    except websockets.ConnectionClosed:
        log.warning("WebSocket client disconnected")

async def main():
    log.info("Starting WiFi Matrix backend")
    log.info("Listening on ws://127.0.0.1:9001")

    async with websockets.serve(handler, "127.0.0.1", 9001):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
