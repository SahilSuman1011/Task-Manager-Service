# Django Development Server Runner
# This script ensures the correct Python environment is used

$VENV_PYTHON = "$PSScriptRoot\venv\bin\python.exe"

Write-Host "Starting Django server with virtual environment..." -ForegroundColor Green
& $VENV_PYTHON "$PSScriptRoot\manage.py" runserver
