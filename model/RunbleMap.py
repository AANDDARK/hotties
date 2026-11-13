import json
from pathlib import Path

from model.RunbleEntities import RunnableEntity

CONFIG_PATH = Path.home() / ".hotties.json"


class RunbleMap:
    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self._path = path
        self._entities: dict[str, RunnableEntity] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        data = json.loads(self._path.read_text(encoding="utf-8"))
        self._entities = {n: RunnableEntity(cmds) for n, cmds in data.items()}

    def _save(self) -> None:
        data = {n: e.commands for n, e in self._entities.items()}
        self._path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def add_runble(self, name: str, commands: list[str]) -> None:
        self._entities[name] = RunnableEntity(commands)
        self._save()

    def remove_runble(self, name: str) -> RunnableEntity | None:
        removed = self._entities.pop(name, None)
        if removed is not None:
            self._save()
        return removed

    @property
    def names(self) -> list[str]:
        return list(self._entities.keys())

    def get_runble(self, name: str) -> RunnableEntity | None:
        return self._entities.get(name)