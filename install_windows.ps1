$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/AANDDARK/hotties.git"
$InstallDir = if ($env:INSTALL_DIR) { $env:INSTALL_DIR } else { Join-Path $env:LOCALAPPDATA "hotties" }

Write-Host "==> Installing hotties from $RepoUrl..." -ForegroundColor Cyan

# 1. Check for git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is required but not installed or not in PATH."
    exit 1
}

# 2. Clone or update the repository
if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Host "==> Updating existing installation in $InstallDir..." -ForegroundColor Yellow
    git -C $InstallDir pull --ff-only
} else {
    Write-Host "==> Cloning into $InstallDir..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path (Split-Path $InstallDir) | Out-Null
    git clone $RepoUrl $InstallDir
}

Set-Location $InstallDir

# 3. Auto-detect stack and install dependencies
if (Test-Path "package.json") {
    Write-Host "==> Node.js project detected. Installing dependencies..." -ForegroundColor Cyan
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        pnpm install
    } elseif (Get-Command yarn -ErrorAction SilentlyContinue) {
        yarn install
    } elseif (Get-Command npm -ErrorAction SilentlyContinue) {
        npm install
    } else {
        Write-Error "Node.js/npm is required."
        exit 1
    }
} elseif ((Test-Path "requirements.txt") -or (Test-Path "pyproject.toml")) {
    Write-Host "==> Python project detected. Setting up virtual environment..." -ForegroundColor Cyan
    python -m venv .venv
    & ".\.venv\Scripts\Activate.ps1"
    python -m pip install --upgrade pip
    if (Test-Path "requirements.txt") { pip install -r requirements.txt }
    if (Test-Path "pyproject.toml") { pip install . }
} elseif (Test-Path "Cargo.toml") {
    Write-Host "==> Rust project detected. Building release..." -ForegroundColor Cyan
    cargo build --release
} elseif (Test-Path "go.mod") {
    Write-Host "==> Go project detected. Building binary..." -ForegroundColor Cyan
    go build -o hotties.exe .
}

Write-Host "==> Installation complete! Located at: $InstallDir" -ForegroundColor Green