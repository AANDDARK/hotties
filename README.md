# hotties

A tiny CLI that saves command sequences under a short name and **re-runs them automatically whenever files in the current directory change**.

Think of it as a hot-reload for anything: compile and run C++, run tests, rebuild a project, lint a file. You describe the commands once, and then a single short command does the rest.

```bash
hotties add cpp 'g++ $1 -o out' '.\out.exe'
hotties cpp main.cpp
```

Edit and save `main.cpp`, and hotties compiles and runs it again.

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

## Installation

### Option 1: pipx (recommended)

Installs `hotties` globally, so it works in any terminal and any folder.

```bash
python -m pip install pipx
python -m pipx ensurepath
```

Restart the terminal, then from the project folder:

```bash
pipx install .
```

### Option 2: pipx in editable mode (for development)

Code changes apply immediately, with no reinstall.

```bash
pipx install -e .
```

### Option 3: virtual environment

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

### Save a command

```bash
hotties add <name> '<command 1>' '<command 2>' ...
```

**Always wrap commands in single quotes.** Otherwise your shell replaces `$1` with an empty string before hotties even starts.

Examples:

```bash
# C++: compile, then run
hotties add cpp 'g++ $1 -o out' '.\out.exe'

# Python: run a script
hotties add py 'python $1'

# Node: run tests
hotties add test 'npm test'
```

### Run a saved command

```bash
hotties <name> [arguments...]
```

```bash
hotties cpp main.cpp
```

This runs the command sequence once, then keeps watching the current directory. When a file changes, the sequence runs again. Press `Ctrl+C` to stop.

Arguments map to placeholders by position: `$1` is the first argument, `$2` the second, and so on.

```bash
hotties add copy 'copy $1 $2'
hotties copy a.txt b.txt      # runs: copy a.txt b.txt
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
├── main.py            # entry point, CLI routing
├── state.py           # shared globalMap instance
├── watcher.py         # file change detection
├── list_all.py        # `hotties list`
├── model/
│   ├── RunbleEntities.py
│   └── RunbleMap.py   # storage, loads/saves ~/.hotties.json
├── use_cases/
│   ├── add.py
│   ├── remove.py
│   └── use.py         # runs commands with placeholders
└── pyproject.toml
```

## Notes and limitations

- `add`, `remove` and `list` are reserved and cannot be used as command names.
- On Windows, commands run through `cmd.exe`, so use `.\out.exe` instead of `./out`, and remember that `g++` produces `out.exe`.
- The watcher polls, so very fast successive edits within 0.5 seconds are merged into one run.
- Arguments with spaces are quoted with `shlex.quote`, which targets POSIX shells. On Windows, paths with spaces may need extra care.
- Only the directory you run `hotties` from (and its subfolders) is watched.

## Uninstall

```bash
pipx uninstall hotties
```

Saved commands stay in `~/.hotties.json`. Delete that file to remove them.
