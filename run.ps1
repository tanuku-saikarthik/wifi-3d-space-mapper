$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$backend = Start-Process -FilePath python -ArgumentList "backend/main.py" -PassThru

Write-Host "Backend started on ws://127.0.0.1:9001"
Write-Host "Frontend server starting at http://127.0.0.1:8080"
Write-Host "Press Ctrl+C to stop both."

try {
  python -m http.server 8080 -d frontend
}
finally {
  if ($backend -and -not $backend.HasExited) {
    Stop-Process -Id $backend.Id -Force
  }
}
