from pathlib import Path


class LocalTextFileGateway:
    def read_text(self, path: Path) -> str | None:
        """Reads UTF-8 text or returns None when the file does not exist.

        Example: ``gateway.read_text(Path('state.json'))`` reads persisted state.
        """
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        """Writes UTF-8 text and creates parent directories when necessary.

        Example: ``gateway.write_text(Path('x/state.json'), '{}')``.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
