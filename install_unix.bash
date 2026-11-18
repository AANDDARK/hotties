#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/AANDDARK/hotties.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/hotties}"

echo "==> Installing hotties from $REPO_URL..."

# 1. Check for git
if ! command -v git >/dev/null 2>&1; then
    echo "Error: git is required but not installed." >&2
    exit 1
fi

# 2. Clone or update the repository
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "==> Updating existing installation in $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --ff-only
else
    echo "==> Cloning into $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# 3. Auto-detect stack and install dependencies
if [ -f "package.json" ]; then
    echo "==> Node.js project detected. Installing dependencies..."
    if command -v pnpm >/dev/null 2>&1; then
        pnpm install
    elif command -v yarn >/dev/null 2>&1; then
        yarn install
    elif command -v npm >/dev/null 2>&1; then
        npm install
    else
        echo "Error: Node.js/npm is required." >&2
        exit 1
    fi
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "==> Python project detected. Setting up virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    [ -f "requirements.txt" ] && pip install -r requirements.txt
    [ -f "pyproject.toml" ] && pip install .
elif [ -f "Cargo.toml" ]; then
    echo "==> Rust project detected. Building release..."
    cargo build --release
elif [ -f "go.mod" ]; then
    echo "==> Go project detected. Building binary..."
    go build -o hotties .
elif [ -f "Makefile" ]; then
    echo "==> Makefile detected. Running make..."
    make install || make
fi

echo "==> Installation complete! Located at: $INSTALL_DIR"