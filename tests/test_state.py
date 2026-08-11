from pathlib import Path

import pytest

from radar_ufersa.models import SeenState
from radar_ufersa.state import JsonSeenStateStore
from tests.fakes import FakeTextFileGateway


def test_load_returns_uninitialized_state_when_file_is_missing() -> None:
    gateway = FakeTextFileGateway()
    store = JsonSeenStateStore(gateway, Path("state.json"))

    state = store.load()

    assert state == SeenState(False, frozenset())


def test_save_and_load_round_trip_is_deterministic() -> None:
    gateway = FakeTextFileGateway()
    path = Path("state.json")
    store = JsonSeenStateStore(gateway, path)

    store.save(SeenState(True, frozenset({"z", "a"})))
    loaded = store.load()

    assert loaded == SeenState(True, frozenset({"a", "z"}))
    assert gateway.files[path].index('"a"') < gateway.files[path].index('"z"')


def test_load_rejects_invalid_json_shape() -> None:
    gateway = FakeTextFileGateway()
    path = Path("state.json")
    gateway.files[path] = '{"initialized":"yes","seen":42}'
    store = JsonSeenStateStore(gateway, path)

    with pytest.raises(ValueError, match="expected.*initialized.*seen"):
        store.load()


def test_load_rejects_malformed_json_with_offending_value() -> None:
    gateway = FakeTextFileGateway()
    path = Path("state.json")
    gateway.files[path] = "{broken"
    store = JsonSeenStateStore(gateway, path)

    with pytest.raises(ValueError, match="broken.*expected valid JSON"):
        store.load()
