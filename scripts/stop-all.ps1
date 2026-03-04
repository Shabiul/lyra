# ============================================================
# Lyra — stop-all.ps1
# Kills all running Lyra service processes
# ============================================================

Write-Host "`n🛑 Stopping all Lyra services...`n" -ForegroundColor Red

# Kill uvicorn (Python services)
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -match "uvicorn" -or $_.CommandLine -match "uvicorn"
} | Stop-Process -Force

# Kill by port (more reliable)
$ports = @(8001, 8002, 8003, 8004, 3000, 3001)

foreach ($port in $ports) {
    $conn = netstat -ano | Select-String ":$port " | Select-String "LISTENING"
    if ($conn) {
        $pid = ($conn -split "\s+")[-1]
        if ($pid -match "^\d+$") {
            Write-Host "  Killing process on port $port (PID: $pid)" -ForegroundColor Yellow
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "`n✅ All services stopped.`n" -ForegroundColor Green
