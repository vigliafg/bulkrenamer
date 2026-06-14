#!/usr/bin/env bash
# =============================================================================
# Bulk File Renamer PRO — macOS Installer & Launcher
# =============================================================================
# Usage:
#   1. Clone the repository:  git clone <repo-url> && cd bulkrenamer
#   2. Run this script:       bash install-macos.sh
#   3. Launch from anywhere:  bulk-renamer
#
# The script:
#   • Checks for Python 3.10+ (and Xcode CLT on Apple Silicon)
#   • Creates a virtual environment inside ~/.local/share/bulk-renamer/
#   • Installs PyQt6 and project dependencies
#   • Creates a global launcher at /usr/local/bin/bulk-renamer
#   • Ensures /usr/local/bin is in your PATH
# =============================================================================

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Paths ─────────────────────────────────────────────────────────────────────
INSTALL_DIR="$HOME/.local/share/bulk-renamer"
# macOS: prefer /usr/local/bin (standard for user-installed CLI tools)
BIN_DIR="/usr/local/bin"
LAUNCHER="$BIN_DIR/bulk-renamer"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   Bulk File Renamer PRO — macOS Installer         ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# ── 1. Check prerequisites ────────────────────────────────────────────────────
info "Checking prerequisites..."

# Check Xcode Command Line Tools (needed for compiling PyQt6 on some Macs)
if ! xcode-select -p &>/dev/null; then
    warn "Xcode Command Line Tools not found."
    info "Installing Xcode CLT (this may open a dialog)..."
    xcode-select --install 2>/dev/null || true
    warn "If the install dialog appeared, wait for it to complete, then re-run this script."
fi

# Check Python
if ! command -v python3 &>/dev/null; then
    err "python3 not found."
    echo "       Install from https://www.python.org/downloads/"
    echo "       or via Homebrew: brew install python@3"
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    err "Python 3.10+ is required. Found: $PY_VER"
    exit 1
fi
ok "Python $PY_VER detected."

if ! python3 -m pip --version &>/dev/null; then
    err "pip not available. Please install it first."
    exit 1
fi

# ── 2. Install project files ──────────────────────────────────────────────────
info "Installing to $INSTALL_DIR ..."
mkdir -p "$INSTALL_DIR"

# Copy project files (excluding .git, .venv, build artifacts)
if command -v rsync &>/dev/null; then
    rsync -a \
        --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
        --exclude='*.pyc' --exclude='*.spec' \
        --exclude='dist/' --exclude='build/' \
        --exclude='install-linux.sh' --exclude='install-windows.ps1' \
        "$PROJECT_DIR/" "$INSTALL_DIR/"
else
    warn "rsync not found, using cp (slower)..."
    cp -r "$PROJECT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
    rm -rf "$INSTALL_DIR/.git" "$INSTALL_DIR/.venv" "$INSTALL_DIR/__pycache__" \
           "$INSTALL_DIR/dist" "$INSTALL_DIR/build" \
           "$INSTALL_DIR/install-linux.sh" "$INSTALL_DIR/install-windows.ps1" 2>/dev/null || true
fi

# ── 3. Create and populate virtual environment ────────────────────────────────
info "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/.venv"

# shellcheck disable=SC1091
source "$INSTALL_DIR/.venv/bin/activate"

info "Installing dependencies..."
pip install --upgrade pip -q
pip install -r "$INSTALL_DIR/requirements.txt" -q

ok "Dependencies installed."

# ── 4. Create global launcher ─────────────────────────────────────────────────
info "Creating global launcher at $LAUNCHER ..."

# /usr/local/bin might require sudo on some macOS setups.
# If sudo is unavailable, fall back to ~/.local/bin (like Linux).
if [ ! -w "$BIN_DIR" ]; then
    if command -v sudo &>/dev/null; then
        info "/usr/local/bin is not writable — using sudo to create the launcher."
        sudo mkdir -p "$BIN_DIR"

        TMP_LAUNCHER=$(mktemp)
        cat > "$TMP_LAUNCHER" << 'LAUNCHEREOF'
#!/usr/bin/env bash
# Bulk File Renamer PRO — Global Launcher
INSTALL_DIR="$HOME/.local/share/bulk-renamer"
exec "$INSTALL_DIR/.venv/bin/python3" "$INSTALL_DIR/main.py" "$@"
LAUNCHEREOF

        sudo cp "$TMP_LAUNCHER" "$LAUNCHER"
        sudo chmod +x "$LAUNCHER"
        rm -f "$TMP_LAUNCHER"
    else
        warn "Cannot write to /usr/local/bin and sudo is not available."
        warn "Falling back to $HOME/.local/bin/bulk-renamer"
        BIN_DIR="$HOME/.local/bin"
        LAUNCHER="$BIN_DIR/bulk-renamer"
        mkdir -p "$BIN_DIR"
        cat > "$LAUNCHER" << 'LAUNCHEREOF'
#!/usr/bin/env bash
# Bulk File Renamer PRO — Global Launcher
INSTALL_DIR="$HOME/.local/share/bulk-renamer"
exec "$INSTALL_DIR/.venv/bin/python3" "$INSTALL_DIR/main.py" "$@"
LAUNCHEREOF
        chmod +x "$LAUNCHER"
    fi
else
    mkdir -p "$BIN_DIR"
    cat > "$LAUNCHER" << 'LAUNCHEREOF'
#!/usr/bin/env bash
# Bulk File Renamer PRO — Global Launcher
INSTALL_DIR="$HOME/.local/share/bulk-renamer"
exec "$INSTALL_DIR/.venv/bin/python3" "$INSTALL_DIR/main.py" "$@"
LAUNCHEREOF
    chmod +x "$LAUNCHER"
fi

ok "Launcher created."

# ── 5. Ensure /usr/local/bin is in PATH ───────────────────────────────────────
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not in your PATH."

    SHELL_RC=""
    case "$SHELL" in
        */bash) SHELL_RC="$HOME/.bash_profile" ;;  # macOS uses .bash_profile by default
        */zsh)  SHELL_RC="$HOME/.zshrc"  ;;
        */fish) SHELL_RC="$HOME/.config/fish/config.fish" ;;
        *)      SHELL_RC="$HOME/.profile" ;;
    esac

    if [ -n "$SHELL_RC" ]; then
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
        ok "Added $BIN_DIR to PATH in $SHELL_RC"
        warn "Restart your terminal or run:  source $SHELL_RC"
    fi
fi

# ── 6. Done ────────────────────────────────────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   ✅ Installation complete!                       ║"
echo "║                                                   ║"
echo "║   Launch from anywhere with:                      ║"
echo "║       bulk-renamer                                ║"
echo "║                                                   ║"
echo "║   Install dir: $INSTALL_DIR"
echo "║   Launcher:    $LAUNCHER"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
