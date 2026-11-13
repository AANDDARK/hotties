from state import globalMap


def add(args: list[str]) -> None:
    if len(args) < 2:
        print("Usage: add <name> '<cmd 1>' '<cmd 2>' ...")
        return

    name, commands = args[0], args[1:]
    globalMap.add_runble(name, commands)
    print(f"Saved '{name}': {commands}")
