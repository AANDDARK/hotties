import sys

from list_all import list_all
from state import globalMap
from use_cases.add import add
from use_cases.remove import remove
from use_cases.use import use
from watcher import watch
BUILTIN = {"add": add, "remove": remove, "list": list_all}


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print("Usage: hotties add|remove|list ... | hotties <name> [args...]")
        return

    cmd, rest = argv[0], argv[1:]

    if cmd in BUILTIN:
        BUILTIN[cmd](rest)
        return

    if globalMap.get_runble(cmd) is None:
        print(f"'{cmd}' not found. Use: hotties add {cmd} '<command>'")
        return

    watch(lambda: use(cmd, rest))


if __name__ == "__main__":
    main()