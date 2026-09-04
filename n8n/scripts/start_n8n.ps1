# ============================================================
# MarketVoice SEA — Launch n8n Locally (Windows PowerShell)
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MarketVoice SEA — n8n Local Workflow Orchestrator" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Ensure working directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$N8nDir = Split-Path -Parent $ScriptDir
Set-Location $N8nDir

# 2. Check Node.js
try {
    $nodeVer = node -v
    Write-Host "[OK] Node.js version: $nodeVer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 3. Check environment variables
if (Test-Path "$N8nDir\.env") {
    Write-Host "[OK] Loading environment configuration from .env" -ForegroundColor Green
    Get-Content "$N8nDir\.env" | Where-Object { $_ -match "^[^#].+=.+" } | ForEach-Object {
        $key, $val = $_ -split '=', 2
        [System.Environment]::SetEnvironmentVariable($key.Trim(), $val.Trim(), [System.EnvironmentVariableTarget]::Process)
    }
}

# 4. Ensure local data directory
$DataDir = "$N8nDir\data"
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
    Write-Host "[OK] Created local data directory at: $DataDir" -ForegroundColor Green
}

$env:N8N_USER_FOLDER = $DataDir
$env:N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS = "false"

Write-Host ""
Write-Host ">> Starting n8n server on http://localhost:5678 ..." -ForegroundColor Yellow
Write-Host ">> Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Launch n8n via npx non-interactively
npx -y n8n start --port 5678
