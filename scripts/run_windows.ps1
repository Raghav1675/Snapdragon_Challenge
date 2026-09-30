$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not installed or is not on PATH."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "Ollama detected. Checking configured model..."
    ollama list
} else {
    Write-Host "Ollama is not installed. AURA will still run its local extraction/privacy features."
    Write-Host "Install Ollama and then run: ollama pull gemma3:1b"
}

& ".\.venv\Scripts\python.exe" -m streamlit run app.py
