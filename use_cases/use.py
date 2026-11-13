import re
import shlex
import subprocess

from state import globalMap


def _format(command: str, args: list[str]) -> str:
    # $1 -> args[0], $2 -> args[1]; \d+ щоб $10 не ламався через $1
    def repl(m: re.Match) -> str:
        idx = int(m.group(1)) - 1
        return shlex.quote(args[idx]) if 0 <= idx < len(args) else m.group(0)

    return re.sub(r"\$(\d+)", repl, command)


def use(name: str, args: list[str]) -> bool:

    entity = globalMap.get_runble(name)
    if entity is None:
        print(f"'{name}' not found.")
        return False

    for command in entity.commands:
        formatted = _format(command, args)
        print(f"$ {formatted}")
        result = subprocess.run(formatted, shell=True)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}.")
            return False
    return True