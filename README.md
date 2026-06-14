# Bulk File Renamer PRO

**Clone of ReNamer (den4b.com) in Python + PyQt6 with 17 composable rename rules.**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt-6-green.svg)
![Theme](https://img.shields.io/badge/Theme-Catppuccin%20Mocha-mauve.svg)

---

## What it is

Bulk File Renamer PRO is a GUI application for batch file renaming. You can compose a **rule stack** (up to 17 different rule types) and see a live preview of the result, with colors highlighting changes and conflicts.

The interface is inspired by [ReNamer](https://den4b.com) with a **Catppuccin Mocha** dark theme.

---

## Installation

### ⚡ One-Command Install (Recommended)

Use the platform-specific install script. It sets up everything automatically — virtual environment, dependencies, and a **global `bulk-renamer` command** you can run from any terminal.

| Platform | Script | Command |
|----------|--------|---------|
| 🐧 **Linux** | [`install-linux.sh`](install-linux.sh) | `bash install-linux.sh` |
| 🍎 **macOS** | [`install-macos.sh`](install-macos.sh) | `bash install-macos.sh` |
| 🪟 **Windows** | [`install-windows.ps1`](install-windows.ps1) | `powershell -File install-windows.ps1` |

#### What each script does

1. **Checks prerequisites** — Python 3.10+, pip, git (Xcode CLT on macOS)
2. **Installs the project** into a user-local directory:
   - Linux/macOS: `~/.local/share/bulk-renamer/`
   - Windows: `%LOCALAPPDATA%\bulk-renamer\`
3. **Creates a virtual environment** and installs PyQt6 + dependencies
4. **Creates a global launcher** named `bulk-renamer`:
   - Linux: `~/.local/bin/bulk-renamer`
   - macOS: `/usr/local/bin/bulk-renamer`
   - Windows: `%LOCALAPPDATA%\Microsoft\WindowsApps\bulk-renamer.cmd`
5. **Adds the launcher to your PATH** so `bulk-renamer` works from any terminal

#### Step-by-step

```bash
# 1. Clone the repository
git clone <repo-url>
cd bulkrenamer

# 2. Run the install script for your OS
# Linux:
bash install-linux.sh

# macOS:
bash install-macos.sh

# Windows (PowerShell — open as normal user, NOT as Administrator):
#   If you get a script execution policy error, first run:
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
powershell -File install-windows.ps1

# 3. Restart your terminal (or run 'source ~/.bashrc' / 'source ~/.zshrc')

# 4. Launch from anywhere!
bulk-renamer
```

The application starts with one default rule ready to use.

> **Note for Windows**: if `bulk-renamer` is not found after installation, open a **new** PowerShell/CMD window so the PATH change takes effect.

---

### 🛠 Manual Setup (Alternative)

If you prefer to set up manually or the install script is not suitable:

#### Requirements

- **Python 3.10 or higher**
- **pip** (included with Python)
- **git** (to clone the repository)

#### Dependencies

The only external dependency is **PyQt6** (≥ 6.5). Everything else is Python standard library.

| Package | Minimum version | Purpose |
|---------|----------------|---------|
| [PyQt6](https://pypi.org/project/PyQt6/) | ≥ 6.5 | Full GUI (windows, widgets, tables, splitter, menus) |

#### Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd bulkrenamer

# 2. Create and activate a virtual environment
# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell / CMD):
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
python main.py
# or, on Linux/macOS:
python3 main.py
```

---

## The 17 Rules

Each rule is an independent module you can add, remove, reorder, enable/disable in the stack.

| # | Rule | Description |
|---|------|-------------|
| 1 | 📝 **Insert** | Inserts text before, after, at a specific position, or after/before a delimiter. Supports meta-tags `[[MTIME_DATE]]`, `[[INDEX]]`, etc. |
| 2 | ✂️ **Delete** | Deletes a range of characters (by position, delimiter, or count). |
| 3 | 🗑 **Remove** | Removes all occurrences of text (or first/last only), with case-sensitive and whole-word support. Multiple texts with `*|*`. |
| 4 | 🔄 **Replace** | Find and replace with regex, wildcard (`*` and `?`), case-sensitive, and whole-word support. |
| 5 | 🔀 **Rearrange** | Reorders name tokens using delimiters or exact positions. Template with `$1`, `$2`, etc. |
| 6 | 🔧 **Extension** | Changes the file extension. Can also append and remove consecutive duplicates. |
| 7 | ✂️ **Strip** | Removes specific characters (or preset sets: digits, symbols, letters, brackets) from start, end, or everywhere. Invert mode available. |
| 8 | 🔠 **Case** | Converts: lowercase, UPPERCASE, Title Case, Invert, First capital, Sentence case. Supports forced fragments. |
| 9 | 🔢 **Serialize** | Sequential numbering: decimal, roman, English letters (a-z, ba-bz...), music notes. Customizable padding, step, and reset. |
| 10 | 🎲 **Randomize** | Adds a random string as prefix/suffix or replaces the name. Configurable length and character set. |
| 11 | 📏 **Padding** | Adds/removes zero-padding on numbers in filenames. Also supports text padding (characters left or right). |
| 12 | 🧹 **Clean Up** | Cleans the name: removes bracket content (round, square, curly), normalizes spaces, splits camelCase, removes emoji and diacritical marks. |
| 13 | 🌍 **Translit** | Transliteration from non-Latin alphabets: German, French, Italian, Spanish, Portuguese, Russian, Greek, Japanese (Romaji) + custom maps. Bidirectional. |
| 14 | 📅 **Reformat Date** | Detects dates in filenames via regex and reformats them (e.g. `2025-06-01` → `01062025`). |
| 15 | 🔣 **Regex** | Arbitrary regex substitution. For advanced users. |
| 16 | 📋 **User Input** | Replaces filenames with a user-provided list. |
| 17 | 🗺 **Mapping** | Renames based on a key-value map (old name → new name). |

---

## Available Meta-tags

Some rules support meta-tags that are expanded dynamically:

| Tag | Description |
|-----|-------------|
| `[[MTIME_DATE]]` | Modification date (`YYYYMMDD`) |
| `[[MTIME_YEAR]]` | Modification year |
| `[[MTIME_MONTH]]` | Modification month (`01`-`12`) |
| `[[MTIME_DAY]]` | Modification day (`01`-`31`) |
| `[[MTIME_TIME]]` | Modification time (`HHMMSS`) |
| `[[INDEX]]` | 1-based progressive index with auto padding |
| `[[INDEX0]]` | 0-based progressive index with auto padding |

---

## Quick Start

### Typical workflow

1. **Load files** — click `📂 Folder` (load all files from a folder) or `📄 Files` (select specific files).
2. **Add rules** — from the `Rules` menu choose the rules you need. They appear in the left panel as stackable cards.
3. **Configure each rule** — each card has its parameters. Enable/disable with the checkbox.
4. **Check the preview** — the right panel shows: original name, new name, and status (✓ changed, ⚠ duplicate, — unchanged).
5. **Select files** — check the boxes in the ☑ column for each file you want to rename. Click the ☑ header to select/deselect all.
6. **Rename!** — click `✅ Rename (N)` to apply changes to the selected files.

### Undo

After a rename, you can undo the operation with `↩ Undo`. The undo stack is unlimited.

### Presets

Save the current rule configuration to a `.json` file (`File → Save Preset`) and reload it later (`File → Load Preset`). Great for repetitive operations!

### Factory Reset

`Tools → Factory Reset` resets all rules to default values.

---

## Project Structure

```
bulkrenamer/
├── main.py                  # Application entry point
├── requirements.txt         # Pip dependencies
├── install-linux.sh         # 🐧 Linux: one-command installer + global launcher
├── install-macos.sh         # 🍎 macOS: one-command installer + global launcher
├── install-windows.ps1      # 🪟 Windows: one-command installer + global launcher
├── test_engine.py           # 🧪 Unit tests: 93 tests covering all engine functions
├── renamer/
│   ├── app.py               # MainWindow: menus, toolbar, splitter, status bar
│   ├── engine.py            # Rename engine (pure logic, zero GUI)
│   ├── theme.py             # Catppuccin Mocha theme (color palette + QSS)
│   ├── undo.py              # UndoManager (LIFO stack for undo operations)
│   ├── preview.py           # PreviewTable: 4 columns (☑ | Original name | New name | Status)
│   └── rules/
│       ├── __init__.py      # ALL_RULES registry (17 rules)
│       ├── base.py          # RenameRule base class
│       ├── insert.py        # 📝 Insert
│       ├── delete.py        # ✂ Delete
│       ├── remove.py        # 🗑 Remove
│       ├── replace.py       # 🔄 Replace
│       ├── rearrange.py     # 🔀 Rearrange
│       ├── extension.py     # 🔧 Extension
│       ├── strip.py         # ✂ Strip
│       ├── case.py          # 🔠 Case
│       ├── serialize.py     # 🔢 Serialize
│       ├── randomize.py     # 🎲 Randomize
│       ├── padding.py       # 📏 Padding
│       ├── cleanup.py       # 🧹 Clean Up
│       ├── translit.py      # 🌍 Translit
│       ├── reformat_date.py # 📅 Reformat Date
│       ├── regex_rule.py    # 🔣 Regex
│       ├── user_input.py    # 📋 User Input
│       └── mapping.py       # 🗺 Mapping
```

---

---

## Running Tests

The project includes a comprehensive test suite (`test_engine.py`) with **93 unit + end‑to‑end tests** covering:

- Every engine function (`_apply_strip`, `_apply_delete`, `_apply_mapping`, `_apply_user_input`, etc.)
- `apply_rules_stack` with rule combinations, ordering, disabled rules, and meta‑tokens
- Bug‑fix regression cases (invert flag, full‑name matching, `keep_delimiters`, Path‑based split)

```bash
# Run all 93 tests
python3 -m unittest test_engine.py -v

# Or with pytest (optional — pip install pytest)
python3 -m pytest test_engine.py -v
```

All tests use only the Python standard library — no extra dependencies needed.

---

## Previous Versions

Two historical versions of the application, based on **customtkinter** instead of PyQt6, are in the repository root:

| File | Version | Framework | Rules | UI |
|------|---------|-----------|-------|----|
| `bulk_renamer.py` | v1 | customtkinter + tkinter | 9 basic rules | Single scrollable panel + treeview |
| `bulk_renamer_pro.py` | v2 | customtkinter + tkinter | 9 basic rules | Menus, preferences (custom colors/fonts), interactive guide |

These versions are **no longer maintained** and require `customtkinter`:

```bash
pip install customtkinter
python3 bulk_renamer_pro.py   # more advanced version
```

The current version (`main.py` + `renamer/` folder) is the only one in active development.

---

## Build Standalone Executable with PyInstaller

[PyInstaller](https://pyinstaller.org) converts the project into a **standalone executable** — a single file that runs on any computer **without Python installed**.

The result is placed in the `dist/` folder after building.

> **Note**: PyInstaller must be installed **inside the virtual environment**. Each procedure below includes the `pip install pyinstaller` command.

---

### 🐧 Linux

#### Prerequisites

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git libxcb-cursor0

# Fedora
sudo dnf install python3 python3-pip git libxcb-cursor

# Arch / Manjaro
sudo pacman -S python python-pip git libxcb
```

#### Step 1 — Prepare the project

```bash
git clone <repo-url>
cd bulkrenamer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
```

#### Step 2 — Create an icon (optional)

PyInstaller on Linux accepts `.png` files directly. Place an icon at the project root (e.g. `icon.png`) and add `--icon icon.png` to the build command.

> If you don't have an icon, simply remove `--icon icon.png` from the build command.

#### Step 3 — Build

```bash
pyinstaller \
  --onefile \
  --name BulkRenamerPRO \
  --add-data "renamer:renamer" \
  --hidden-import PyQt6.QtCore \
  --hidden-import PyQt6.QtGui \
  --hidden-import PyQt6.QtWidgets \
  main.py
```

The executable will be created at: **`dist/BulkRenamerPRO`**

#### Step 4 — Verify

```bash
ls -lh dist/BulkRenamerPRO    # check it exists (~60 MB)
./dist/BulkRenamerPRO          # launch the application
```

#### ⭐ Extra: `.deb` package (Debian/Ubuntu)

```bash
# Install fpm
sudo apt install ruby
sudo gem install fpm

# Create Debian structure
mkdir -p pkg/usr/bin pkg/usr/share/applications
cp dist/BulkRenamerPRO pkg/usr/bin/

cat > pkg/usr/share/applications/bulkrenamer.desktop << 'EOF'
[Desktop Entry]
Name=Bulk File Renamer PRO
Comment=Batch file renaming
Exec=/usr/bin/BulkRenamerPRO
Type=Application
Categories=Utility;FileTools;
Terminal=false
EOF

# Create the .deb
fpm -s dir -t deb -n bulkrenamer-pro -v 3.0 \
  -C pkg \
  -p bulkrenamer-pro.deb \
  -d "libxcb-cursor0"

# Install (requires sudo)
sudo dpkg -i bulkrenamer-pro.deb
```

#### ⭐ Extra: AppImage package

```bash
mkdir -p AppDir/usr/bin
cp dist/BulkRenamerPRO AppDir/usr/bin/

cat > AppDir/bulkrenamer.desktop << 'EOF'
[Desktop Entry]
Name=Bulk File Renamer PRO
Exec=BulkRenamerPRO
Type=Application
Categories=Utility;
EOF

wget https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
./appimagetool-x86_64.AppImage AppDir BulkRenamerPRO.AppImage
```

---

### 🍎 macOS

#### Prerequisites

```bash
# Install Xcode Command Line Tools (required for compilation)
xcode-select --install

# Install Python 3.10+ from https://www.python.org/downloads/
# or via Homebrew:
brew install python@3
```

> **Verify**: open Terminal and type `python3 --version`. Must be ≥ 3.10.

#### Step 1 — Prepare the project

```bash
git clone <repo-url>
cd bulkrenamer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller
```

#### Step 2 — Create `.icns` icon (optional)

If you have a `.png` file (at least 1024×1024), convert it to `.icns` **before** building:

```bash
# Create icns structure
mkdir -p icon.iconset
sips -z 16 16   icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32   icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32   icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64   icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128 icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256 icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256 icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512 icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512 icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset

# Now you have icon.icns in the project root
```

> If you don't have an icon, remove `--icon icon.icns` from the build command.

#### Step 3 — Build

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name "Bulk Renamer PRO" \
  --add-data "renamer:renamer" \
  --hidden-import PyQt6.QtCore \
  --hidden-import PyQt6.QtGui \
  --hidden-import PyQt6.QtWidgets \
  --icon icon.icns \
  main.py
```

The result is a native `.app` bundle at: **`dist/Bulk Renamer PRO.app`**

> **Important**: on macOS, do **NOT** use `--onefile` alone — always add `--windowed` with `--onefile` to prevent a terminal window from opening.

#### Step 4 — Verify

```bash
ls -la "dist/Bulk Renamer PRO.app"      # check it exists
open "dist/Bulk Renamer PRO.app"         # launch the application
```

#### ⭐ Extra: Create `.dmg` (disk image)

```bash
mkdir -p dmg
cp -R "dist/Bulk Renamer PRO.app" dmg/
ln -s /Applications dmg/Applications

hdiutil create -volname "Bulk Renamer PRO" \
  -srcfolder dmg \
  -ov -format UDZO \
  "Bulk Renamer PRO.dmg"

# The .dmg is ready for distribution
open "Bulk Renamer PRO.dmg"
```

#### ⭐ Extra: Sign and Notarize (public distribution)

On macOS, unsigned executables are **blocked by Gatekeeper**. To distribute the app without the security warning, you have three options:

**Option A — Sign with Apple Developer certificate** (requires paid account: $99/year)

```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  "dist/Bulk Renamer PRO.app"

# Verify the signature
codesign --verify --verbose "dist/Bulk Renamer PRO.app"
```

**Option B — User bypasses Gatekeeper manually** (no cost, but requires user action)

The end user must run **once**:
```bash
# Removes quarantine attribute (safe: acts on this app only)
xattr -cr "/Applications/Bulk Renamer PRO.app"
# Then right-click the app → Open (needed only the first time)
```

> ⚠️ **Never use** `sudo spctl --master-disable`: it disables ALL Gatekeeper globally, making the Mac vulnerable. Only use `xattr -cr` which targets a single app.

**Option C — Full notarization** (requires Xcode + Apple Developer account)

```bash
# 1. Sign the app (see Option A)
# 2. Create an archive and submit to Apple for notarization
xcrun notarytool submit "Bulk Renamer PRO.dmg" \
  --apple-id "you@email.com" \
  --team-id "YOURTEAMID" \
  --password "@keychain:AC_PASSWORD" \
  --wait

# 3. Staple the notarization ticket to the app
xcrun stapler staple "dist/Bulk Renamer PRO.app"
```

---

### 🪟 Windows

#### Prerequisites

1. **Install Python 3.10+** from [python.org/downloads](https://www.python.org/downloads/)
   - ✅ Check **"Add Python to PATH"** during installation
2. **Install Git** from [git-scm.com/download/win](https://git-scm.com/download/win)

> **Verify**: open **Command Prompt** (`cmd.exe`) and type:
> ```
> python --version
> git --version
> ```
> Both should show the installed version.

#### Step 1 — Prepare the project

Open **Command Prompt** or **PowerShell**:

```cmd
git clone <repo-url>
cd bulkrenamer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

#### Step 2 — Create `.ico` icon (optional)

If you have a `.png` file, convert it to `.ico` **before** building. Use one of these free methods:

- **Online**: upload the `.png` to [icoconverter.com](https://icoconverter.com) and download the `.ico`
- **With Python**:
  ```cmd
  pip install Pillow
  python -c "from PIL import Image; img = Image.open('icon.png'); img.save('icon.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
  ```

> If you don't have an icon, remove `--icon icon.ico` from the build command.

#### Step 3 — Build

```cmd
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name BulkRenamerPRO ^
  --add-data "renamer;renamer" ^
  --hidden-import PyQt6.QtCore ^
  --hidden-import PyQt6.QtGui ^
  --hidden-import PyQt6.QtWidgets ^
  --icon icon.ico ^
  main.py
```

> ⚠️ **Important**: on Windows, the separator for `--add-data` is `;` (semicolon), **NOT** `:` as on Linux/macOS. And the line continuation character is `^`, not `\`.

The executable will be created at: **`dist\BulkRenamerPRO.exe`**

#### Step 4 — Verify

```cmd
dir dist\BulkRenamerPRO.exe       REM check it exists (~60 MB)
dist\BulkRenamerPRO.exe           REM launch the application
```

#### ⭐ Extra: Create installer with NSIS

[NSIS](https://nsis.sourceforge.io/Download) (Nullsoft Scriptable Install System) is free and creates professional `.exe` installers.

1. **Install NSIS** from [nsis.sourceforge.io/Download](https://nsis.sourceforge.io/Download)
2. Create an `installer.nsi` file at the project root:

```nsis
!define NAME "Bulk File Renamer PRO"
!define EXE  "BulkRenamerPRO.exe"
!define VERSION "3.0"
!define PUBLISHER "Your Name"

OutFile "${NAME} Setup ${VERSION}.exe"
InstallDir "$PROGRAMFILES64\${NAME}"
RequestExecutionLevel admin

Section "Install"
  SetOutPath $INSTDIR
  File "dist\${EXE}"
  CreateShortCut "$DESKTOP\${NAME}.lnk" "$INSTDIR\${EXE}"
  CreateDirectory "$SMPROGRAMS\${NAME}"
  CreateShortCut "$SMPROGRAMS\${NAME}\${NAME}.lnk" "$INSTDIR\${EXE}"
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\${EXE}"
  Delete "$INSTDIR\uninstall.exe"
  Delete "$DESKTOP\${NAME}.lnk"
  RMDir /r "$SMPROGRAMS\${NAME}"
  RMDir "$INSTDIR"
SectionEnd
```

3. Compile the installer:
   ```cmd
   "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
   ```
   The installer will be created at the project root: `Bulk File Renamer PRO Setup 3.0.exe`

#### ⭐ Extra: Alternative — Inno Setup

[Inno Setup](https://jrsoftware.org/isinfo.php) is another great free option for Windows installers, with a guided graphical interface. Load the exe, choose an install folder, and generate the installer in a few clicks.

---

### PyInstaller Command Summary

| Platform | `main.py` | `renamer/` | `PyQt6` | Icon |
|----------|-----------|------------|---------|------|
| **Linux** | ✅ | `--add-data "renamer:renamer"` | 3 × `--hidden-import` | `--icon icon.png` |
| **macOS** | ✅ | `--add-data "renamer:renamer"` | 3 × `--hidden-import` | `--icon icon.icns` |
| **Windows** | ✅ | `--add-data "renamer;renamer"` | 3 × `--hidden-import` | `--icon icon.ico` |

| Flag | Purpose |
|------|---------|
| `--onefile` | Creates a single executable file (instead of a folder) |
| `--windowed` (macOS) | Launches as GUI app without a terminal |
| `--noconsole` (Windows) | Hides the terminal window |
| `--name "Name"` | Executable name |
| `--add-data "src:tgt"` | Includes the `renamer/` folder inside the executable |
| `--hidden-import pkg` | Forces inclusion of modules not automatically detected |
| `--icon file` | Sets the executable icon |
| `--clean` | Cleans up temporary build files from previous runs |

### Key Differences Between Platforms

| Aspect | Linux | macOS | Windows |
|--------|-------|-------|---------|
| `--add-data` separator | `:` (colon) | `:` (colon) | `;` (semicolon) |
| Line continuation | `\` | `\` | `^` |
| GUI mode flag | (not needed) | `--windowed` | `--noconsole` |
| Icon format | `.png` | `.icns` | `.ico` |
| Output | `dist/BulkRenamerPRO` | `dist/Bulk Renamer PRO.app` | `dist\BulkRenamerPRO.exe` |
| Extra OS deps | `libxcb-cursor0` | Xcode CLT | (none) |

### Troubleshooting

| Problem | Likely cause | Solution |
|---------|-------------|----------|
| `ModuleNotFoundError: PyQt6` | PyInstaller doesn't detect all Qt modules | Add `--hidden-import PyQt6.QtCore --hidden-import PyQt6.QtGui --hidden-import PyQt6.QtWidgets` |
| Executable can't find `renamer/` | `--add-data` with wrong separator or path | Linux/macOS: `--add-data "renamer:renamer"`. Windows: `--add-data "renamer;renamer"`. Run from project root. |
| Huge executable (100+ MB) | PyQt6 includes the Qt framework (~50-80 MB) | Normal. Use `--onedir` instead of `--onefile` for faster startup (files are separate but the folder is larger). |
| `error while loading shared libraries: libxcb-cursor.so.0` (Linux) | Missing XCB cursor library | `sudo apt install libxcb-cursor0` |
| `libtiff.so.5: cannot open shared object` (Linux) | Optional Qt TIFF library missing | Harmless — the app works anyway. Ignore. |
| Windows Defender blocks the exe | Digitally unsigned executable | Add an exception in Windows Security, or sign the exe with a certificate. |
| macOS: "app is damaged" | Gatekeeper blocks unsigned app | User must run: `xattr -cr "/Applications/Bulk Renamer PRO.app"` |
| macOS: `--onefile` produces an app that won't launch | Missing `--windowed` | On macOS you MUST always add `--windowed` together with `--onefile` |
| Build is slow or fails | Corrupted PyInstaller cache | `rm -rf build/ dist/ *.spec` and retry with `--clean` |

---

## License

This project is open source. Feel free to use, modify, and distribute it.

---

## Credits

- **ReNamer** by [den4b.com](https://den4b.com) — original inspiration
- **Catppuccin Mocha** — dark theme color palette
- **PyQt6** — GUI framework
- **PyInstaller** — tool for creating standalone executables
