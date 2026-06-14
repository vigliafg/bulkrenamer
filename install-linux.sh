#!/usr/bin/env bash
# =============================================================================
# Bulk File Renamer PRO — Linux Installer & Launcher
# =============================================================================
# Usage:
#   1. Clone the repository:  git clone <repo-url> && cd bulkrenamer
#   2. Run this script:       bash install-linux.sh
#   3. Launch from anywhere:  bulk-renamer
#
# The script:
#   • Checks for Python 3.10+ and pip
#   • Creates a virtual environment inside ~/.local/share/bulk-renamer/
#   • Installs PyQt6 and project dependencies
#   • Creates a global launcher at ~/.local/bin/bulk-renamer
#   • Ensures ~/.local/bin is in your PATH
# =============================================================================

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Paths ─────────────────────────────────────────────────────────────────────
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/bulk-renamer"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/bulk-renamer"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   Bulk File Renamer PRO — Linux Installer         ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# ── 1. Check prerequisites ────────────────────────────────────────────────────
info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    err "python3 not found. Please install Python 3.10+ first:"
    echo "       sudo apt install python3 python3-pip python3-venv   (Debian/Ubuntu)"
    echo "       sudo dnf install python3 python3-pip                 (Fedora)"
    echo "       sudo pacman -S python python-pip                     (Arch)"
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
        "$PROJECT_DIR/" "$INSTALL_DIR/"
else
    warn "rsync not found, using cp (slower)..."
    cp -r "$PROJECT_DIR"/* "$INSTALL_DIR/" 2>/dev/null || true
    rm -rf "$INSTALL_DIR/.git" "$INSTALL_DIR/.venv" "$INSTALL_DIR/__pycache__" \
           "$INSTALL_DIR/dist" "$INSTALL_DIR/build" 2>/dev/null || true
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
mkdir -p "$BIN_DIR"

cat > "$LAUNCHER" << 'LAUNCHEREOF'
#!/usr/bin/env bash
# Bulk File Renamer PRO — Global Launcher
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/bulk-renamer"
exec "$INSTALL_DIR/.venv/bin/python3" "$INSTALL_DIR/main.py" "$@"
LAUNCHEREOF

chmod +x "$LAUNCHER"
ok "Launcher created."

# ── 5. Ensure ~/.local/bin is in PATH ─────────────────────────────────────────
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warn "$BIN_DIR is not in your PATH."

    # Detect shell and add to appropriate rc file
    SHELL_RC=""
    case "$SHELL" in
        */bash) SHELL_RC="$HOME/.bashrc" ;;
        */zsh)  SHELL_RC="$HOME/.zshrc"  ;;
        */fish) SHELL_RC="$HOME/.config/fish/config.fish" ;;
        *)      SHELL_RC="$HOME/.profile" ;;
    esac

    if [ -n "$SHELL_RC" ]; then
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
        ok "Added $BIN_DIR to PATH in $SHELL_RC"
        warn "Restart your shell or run:  source $SHELL_RC"
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
