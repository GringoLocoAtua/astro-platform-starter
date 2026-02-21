$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

if (-not (Test-Path .venv)) {
  py -3.11 -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller .\package\snapquote.spec --clean
