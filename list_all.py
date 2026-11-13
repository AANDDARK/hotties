from state import globalMap
def list_all(args: list[str]) -> None:
    if not globalMap.names:
        print("No saved commands.")
        return
    for name in globalMap.names:
        print(f"{name}: {globalMap.get_runble(name).commands}")