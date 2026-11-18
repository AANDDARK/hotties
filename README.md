# hotties

A tiny CLI that saves command sequences under a short name and **re-runs them automatically whenever files in the current directory change**.

Think of it as hot-reload for anything: compile and run C++, run tests, rebuild a project, lint a file. Describe the commands once, then a single short command does the rest.

```bash
hotties add cpp 'g++ $1 -o out' './out'
hotties cpp main.cpp
```

Edit and save `main.cpp`, and hotties compiles and runs it again.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Quick install with scripts](#quick-install-with-scripts)
  - [Manual install](#manual-install)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Notes and limitations](#notes-and-limitations)
- [Updating and uninstalling](#updating-and-uninstalling)

## Features

- Save any number of shell commands under one name
- `$1`, `$2`, ... placeholders are replaced with the arguments you pass
- Watches the current directory and re-runs on any file change
- Stops the sequence if a command fails (non-zero exit code)
- Saved commands persist between runs in `~/.hotties.json`
- Ignores `.git`, `node_modules`, `__pycache__`, `.venv`, `.idea`
- No dependencies, pure Python standard library

## Requirements

- Python 3.10 or newer
- `git` (only for the install scripts)

## Installation

### Quick install with scripts

The repository ships two installers. Both do the same three things:

1. Check that `git` is available.
2. Clone the repository (or `git pull --ff-only` if it is already cloned).
3. Detect the project type and install it. For hotties this means creating a virtual environment at `<install dir>/.venv` and running `pip install .` inside it.

| Script | Platform | Default install directory |
| --- | --- | --- |
| `install_unix.bash` | Linux, macOS | `~/.local/share/hotties` |
| `install_windows.ps1` | Windows (PowerShell) | `%LOCALAPPDATA%\hotties` |

Set the `INSTALL_DIR` environment variable to install somewhere else.

#### Linux / macOS

```bash
curl -fsSL https://github.com/AANDDARK/hotties/raw/refs/heads/master/install_unix.bash | bash
```

Or download and inspect it first:

```bash
git clone https://github.com/AANDDARK/hotties.git
cd hotties
bash install_unix.bash
```

Custom location:

```bash
INSTALL_DIR="$HOME/tools/hotties" bash install_unix.bash
```

#### Windows (PowerShell)

```powershell
irm https://github.com/AANDDARK/hotties/raw/refs/heads/master/install_windows.ps1 | iex
```

Or from a local clone:

```powershell
git clone https://github.com/AANDDARK/hotties.git
cd hotties
.\install_windows.ps1
```

If PowerShell blocks the script, allow it for the current session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Custom location:

```powershell
$env:INSTALL_DIR = "C:\tools\hotties"
.\install_windows.ps1
```

#### Make `hotties` available everywhere

The scripts install into a virtual environment and **do not modify your `PATH`**. After the script finishes, pick one of these:

**Linux / macOS**

```bash
# Option A: symlink into a folder that is already on PATH
mkdir -p ~/.local/bin
ln -sf ~/.local/share/hotties/.venv/bin/hotties ~/.local/bin/hotties

# Option B: add the venv's bin folder to PATH (put this line in ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/share/hotties/.venv/bin:$PATH"
```

**Windows (PowerShell)**

```powershell
# Add the venv's Scripts folder to your user PATH, then restart the terminal
$scripts = Join-Path $env:LOCALAPPDATA "hotties\.venv\Scripts"
$path = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$path;$scripts", "User")
```

#### Other project types

The scripts are generic and also detect Node.js (`package.json`), Rust (`Cargo.toml`) and Go (`go.mod`) projects; the Unix script additionally runs `make install` for a `Makefile`. None of these apply to hotties itself, which is a Python project.

### Manual install

#### Option 1: pipx (recommended)

Installs `hotties` globally, so it works in any terminal and any folder.

```bash
python -m pip install pipx
python -m pipx ensurepath
```

Restart the terminal, then from the project folder:

```bash
pipx install .
```

#### Option 2: pipx in editable mode (for development)

Code changes apply immediately, with no reinstall.

```bash
pipx install -e .
```

#### Option 3: virtual environment

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

python -m pip install -e .
```

The `hotties` command is only available while the venv is active.

### Check the installation

```bash
hotties list
```

If it prints `No saved commands.`, everything works.

## Usage

### Commands at a glance

| Command | What it does |
| --- | --- |
| `hotties add <name> '<cmd 1>' '<cmd 2>' ...` | Save a command sequence under `<name>` |
| `hotties <name> [args...]` | Run the sequence, then re-run it on every file change |
| `hotties list` | Show all saved sequences |
| `hotties remove <name>` | Delete a saved sequence |

### Save a command

```bash
hotties add <name> '<command 1>' '<command 2>' ...
```

**Always wrap commands in single quotes.** Otherwise your shell replaces `$1` with an empty string before hotties even starts. (In Windows `cmd.exe`, single quotes are not quoting characters, so use PowerShell or a POSIX-style shell such as Git Bash.)

```bash
# C++: compile, then run
hotties add cpp 'g++ $1 -o out' './out'

# Python: run a script
hotties add py 'python $1'

# Node: run tests
hotties add test 'npm test'
```

On Windows, run the compiled program as `.\out.exe` instead of `./out`.

### Run a saved command

```bash
hotties <name> [arguments...]
```

```bash
hotties cpp main.cpp
```

This runs the sequence once, then keeps watching the current directory. When a file changes, the sequence runs again. Press `Ctrl+C` to stop.

Arguments map to placeholders by position: `$1` is the first argument, `$2` the second, and so on.

```bash
hotties add copy 'cp $1 $2'
hotties copy a.txt b.txt      # runs: cp a.txt b.txt
```

### List saved commands

```bash
hotties list
```

### Remove a saved command

```bash
hotties remove <name>
```

## How it works

1. `hotties add` stores the list of commands in `~/.hotties.json`.
2. `hotties <name> ...` loads the commands, substitutes `$N` placeholders, and runs them one by one through the shell.
3. If a command exits with a non-zero code, the rest of the sequence is skipped.
4. A watcher polls the directory every 0.5 seconds and compares file modification times. On a change, the sequence runs again.
5. The snapshot of files is taken **after** each run, so build artifacts such as `out.exe` don't trigger an endless rerun loop.

## Project structure

```
hotties/
├── main.py              # entry point, CLI routing
├── state.py             # shared globalMap instance
├── watcher.py           # file change detection
├── list_all.py          # `hotties list`
├── install_unix.bash    # installer for Linux / macOS
├── install_windows.ps1  # installer for Windows
├── model/
│   ├── RunbleEntities.py
│   └── RunbleMap.py     # storage, loads/saves ~/.hotties.json
├── use_cases/
│   ├── add.py
│   ├── remove.py
│   └── use.py           # runs commands with placeholders
└── pyproject.toml
```

## Notes and limitations

- `add`, `remove` and `list` are reserved and cannot be used as command names.
- On Windows, commands run through `cmd.exe`, so use `.\out.exe` instead of `./out`, and remember that `g++` produces `out.exe`.
- The watcher polls, so very fast successive edits within 0.5 seconds are merged into one run.
- Arguments with spaces are quoted with `shlex.quote`, which targets POSIX shells. On Windows, paths with spaces may need extra care.
- Only the directory you run `hotties` from (and its subfolders) is watched.

## Updating and uninstalling

### Installed with the scripts

**Update:** run the same install script again. It detects the existing clone and runs `git pull --ff-only`.

**Uninstall:** delete the install directory and any symlink or `PATH` entry you added.

```bash
# Linux / macOS
rm -rf ~/.local/share/hotties
rm -f ~/.local/bin/hotties
```

```powershell
# Windows
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hotties"
```

### Installed with pipx

```bash
pipx uninstall hotties
```

### Saved commands

Saved commands stay in `~/.hotties.json` after uninstalling. Delete that file to remove them.
