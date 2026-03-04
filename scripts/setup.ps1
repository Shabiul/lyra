# ============================================================
# Lyra — setup.ps1
# Installs all Python + Node.js dependencies for every service
# Run once from the lyra/ root directory
# ============================================================

Write-Host "`n🌸 Lyra Setup — Installing all dependencies`n" -ForegroundColor Magenta

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

# ─── Python services ─────────────────────────────────────
$pythonServices = @("llm-core", "memory", "voice", "vision")

foreach ($svc in $pythonServices) {
    $path = Join-Path $root "services\$svc"
    $req  = Join-Path $path "requirements.txt"

    if (Test-Path $req) {
        Write-Host "📦 Installing Python deps for: $svc" -ForegroundColor Cyan
        Push-Location $path
        pip install -r requirements.txt
        Pop-Location
    } else {
        Write-Host "⚠️  Skipping $svc — no requirements.txt found" -ForegroundColor Yellow
    }
}

# ─── Node.js services ────────────────────────────────────
$nodeServices = @("api-gateway", "avatar-bridge")

foreach ($svc in $nodeServices) {
    $path    = Join-Path $root "services\$svc"
    $pkgJson = Join-Path $path "package.json"

    if (Test-Path $pkgJson) {
        Write-Host "📦 Installing Node deps for: $svc" -ForegroundColor Cyan
        Push-Location $path
        npm install
        Pop-Location
    } else {
        Write-Host "⚠️  Skipping $svc — no package.json found" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Setup complete! Run .\scripts\start-all.ps1 to launch Lyra.`n" -ForegroundColor Green
