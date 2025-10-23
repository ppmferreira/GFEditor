<#
Simple runner for GFEditor on Windows PowerShell.

Behavior:
- Creates a venv in .venv if missing
- Activates the venv
- Installs requirements from requirements.txt
- Runs the GUI launcher (launch_gfeditor_gui.py) by default
#>

$root = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $root

$Launcher = 'launch_gfeditor_gui.py'

if (-not (Test-Path '.venv')) {
    Write-Host "Creating virtual environment in .venv..."
    python -m venv .venv
}

Write-Host "Activating venv..."
. .\.venv\Scripts\Activate.ps1

if (Test-Path 'requirements.txt') {
    Write-Host "Installing requirements (this may take a while the first time)..."
    pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found; skipping install."
}

Write-Host "Launching GUI ($Launcher)..."
python $Launcher
