# Script to run Django server and ngrok
Write-Host "Starting Django server and ngrok..." -ForegroundColor Green

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Start Django server in background
Write-Host "Starting Django server on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python manage.py runserver 0.0.0.0:8000"

# Wait for Django to start
Write-Host "Waiting for Django server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start ngrok
Write-Host "Starting ngrok tunnel..." -ForegroundColor Cyan
ngrok http 8000

Write-Host "Done!" -ForegroundColor Green

