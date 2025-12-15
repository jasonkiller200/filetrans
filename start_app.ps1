# Set the script's location as the current working directory
Set-Location -Path $PSScriptRoot

# Activate the Python virtual environment
Write-Host "Activating virtual environment..."
. .\.venv\Scripts\Activate.ps1

# Start the Python application
Write-Host "Starting the application (run.py)..."
python run.py
