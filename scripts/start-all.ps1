# ============================================================
# Lyra — start-all.ps1
# Launches all backend services in separate PowerShell windows
# Run from the lyra/ root directory
# ============================================================

Write-Host "`n🌸 Starting Lyra backend services...`n" -ForegroundColor Magenta

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

# ─── Helper ──────────────────────────────────────────────
function Start-Service($name, $command, $workDir) {
    $fullPath = Join-Path $root $workDir
    Write-Host "🚀 Starting: $name" -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$fullPath'; $command" -WindowStyle Normal
    Start-Sleep -Milliseconds 500
}

# ─── Python services ─────────────────────────────────────
Start-Service "llm-core   [:8001]" `
    "uvicorn main:app --host 0.0.0.0 --port 8001 --reload" `
    "services\llm-core"

Start-Service "memory     [:8002]" `
    "uvicorn main:app --host 0.0.0.0 --port 8002 --reload" `
    "services\memory"

Start-Service "voice      [:8003]" `
    "uvicorn main:app --host 0.0.0.0 --port 8003 --reload" `
    "services\voice"

Start-Service "vision     [:8004]" `
    "uvicorn main:app --host 0.0.0.0 --port 8004 --reload" `
    "services\vision"

# ─── Node.js services ────────────────────────────────────
Start-Service "api-gateway [:3000]" `
    "npm run dev" `
    "services\api-gateway"

Start-Service "avatar-bridge [:3001]" `
    "npm run dev" `
    "services\avatar-bridge"

Write-Host "`n✅ All services launched!`n" -ForegroundColor Green
Write-Host "  API Gateway  → http://localhost:3000" -ForegroundColor White
Write-Host "  LLM Core     → http://localhost:8001" -ForegroundColor White
Write-Host "  Memory       → http://localhost:8002" -ForegroundColor White
Write-Host "  Voice        → http://localhost:8003" -ForegroundColor White
Write-Host "  Vision       → http://localhost:8004" -ForegroundColor White
Write-Host "  Ollama       → http://localhost:11434`n" -ForegroundColor White
