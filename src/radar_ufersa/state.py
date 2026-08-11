import json
from pathlib import Path

from radar_ufersa.models import SeenState
from radar_ufersa.ports import TextFileGateway


class JsonSeenStateStore:
    def __init__(self, gateway: TextFileGateway, path: Path) -> None:
        self._gateway = gateway
        self._path = path

    def load(self) -> SeenState:
        """Loads the initialized flag and fingerprints from the JSON state file.

        Example: ``store.load()`` returns an uninitialized state on first run.
        """
        raw_state = self._gateway.read_text(self._path)
        if raw_state is None:
            return SeenState(initialized=False, fingerprints=frozenset())
        try:
            parsed_state: object = json.loads(raw_state)
        except json.JSONDecodeError as exception:
            raise ValueError(
                f"Invalid state value={raw_state!r}; expected valid JSON with "
                "{'initialized': bool, 'seen': list[str]}."
            ) from exception
        return self._parse_state(parsed_state)

    def save(self, state: SeenState) -> None:
        """Persists state deterministically so Git commits stay easy to review.

        Example: ``store.save(SeenState(True, frozenset({'abc'})))``.
        """
        payload = {
            "initialized": state.initialized,
            "seen": sorted(state.fingerprints),
        }
        serialized_state = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        self._gateway.write_text(self._path, serialized_state)

    def _parse_state(self, parsed_state: object) -> SeenState:
        if not isinstance(parsed_state, dict):
            raise ValueError(
                f"Invalid state value={parsed_state!r}; expected a JSON object."
            )
        initialized = parsed_state.get("initialized")
        seen = parsed_state.get("seen")
        if not isinstance(initialized, bool) or not self._is_string_list(seen):
            raise ValueError(
                f"Invalid state value={parsed_state!r}; expected "
                "{'initialized': bool, 'seen': list[str]}."
            )
        return SeenState(initialized=initialized, fingerprints=frozenset(seen))

    def _is_string_list(self, value: object) -> bool:
        if not isinstance(value, list):
            return False
        return all(isinstance(item, str) for item in value)
