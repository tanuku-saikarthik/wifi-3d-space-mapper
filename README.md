# WiFi 3D Mapper

Realtime WiFi topology visualizer:
- Python backend scans nearby WiFi and streams node/edge data over WebSocket.
- Three.js frontend renders AP nodes, links, and live signal board.

## Quick Start

### Option 1 (recommended): one command

#### Windows (PowerShell)
```powershell
git clone <your-repo-url>
cd "Wifi 3d"
./run.ps1
```

#### macOS / Linux
```bash
git clone <your-repo-url>
cd "Wifi 3d"
chmod +x run.sh
./run.sh
```

Then open:
- `http://127.0.0.1:8080`

## Manual Setup

```bash
git clone <your-repo-url>
cd "Wifi 3d"
python -m venv .venv
```

Activate venv:

- Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

- macOS / Linux:
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run backend in one terminal:

```bash
python backend/main.py
```

Run frontend server in another terminal:

```bash
python -m http.server 8080 -d frontend
```

Open `http://127.0.0.1:8080`.

## Notes

- On Windows, real WiFi scan uses `netsh`.
- On non-Windows systems (or if scan fails), the backend automatically falls back to synthetic WiFi data so the app still runs.
- You can force synthetic data on any platform:
  - PowerShell: `$env:WIFI_SYNTHETIC="1"; python backend/main.py`
  - Bash: `WIFI_SYNTHETIC=1 python backend/main.py`

## Project Structure

```text
backend/
  main.py
  scanner.py
  signals.py
  correlation.py
  embedding.py
frontend/
  index.html
requirements.txt
run.ps1
run.sh
```
