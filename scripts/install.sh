#!/usr/bin/env bash
# Remembrall One-Line Installer (Linux / macOS / Git Bash)
# Installs Remembrall CLI globally or locally into your environment.

set -e

echo "🔮 Installing Remembrall Universal State Engine..."

# Detect Node.js or Python runtime
HAS_NODE=false
HAS_PYTHON=false

if command -v node >/dev/null 2>&1; then
    HAS_NODE=true
fi

if command -v python3 >/dev/null 2>&1; then
    HAS_PYTHON=true
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    HAS_PYTHON=true
    PY_CMD="python"
fi

# Clone or update
INSTALL_DIR="${HOME}/.remembrall"
REPO_URL="https://github.com/dkrpl/remembrall.git"

if [ -d "$INSTALL_DIR" ]; then
    echo "📦 Updating existing Remembrall installation at $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --quiet
else
    echo "📦 Cloning Remembrall into $INSTALL_DIR..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" --quiet
fi

# Link binary to /usr/local/bin or ~/.local/bin
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"

if [ "$HAS_NODE" = true ]; then
    echo "⚡ Linking Node.js binary to $BIN_DIR/remembrall..."
    ln -sf "$INSTALL_DIR/bin/remembrall.js" "$BIN_DIR/remembrall"
    chmod +x "$BIN_DIR/remembrall"
elif [ "$HAS_PYTHON" = true ]; then
    echo "🐍 Linking Python binary to $BIN_DIR/remembrall..."
    ln -sf "$INSTALL_DIR/remembrall" "$BIN_DIR/remembrall"
    chmod +x "$BIN_DIR/remembrall"
fi

echo "✅ Remembrall installed successfully!"
echo "   Run 'remembrall status' to verify."
