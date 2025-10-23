param(
    [string]$Name = 'GFEditor',
    [string]$Entry = 'launch_gfeditor.py'
)

Write-Host "Activating venv and running PyInstaller..."
. .\.venv\Scripts\Activate.ps1
pip install pyinstaller -q
pyinstaller -F -n $Name $Entry
Write-Host "Finished. Dist folder contains the exe. Ensure 'Lib' folder is next to the exe."
