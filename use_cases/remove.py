from state import globalMap

def remove(args: list[str]) -> None:
    if len(args) < 1:
        print("Usage: remove <name>")
        return

    name = args[0]
    if globalMap.remove_runble(name) is None:
        print(f"'{name}' not found.")
    else:
        print(f"Removed '{name}'.")
