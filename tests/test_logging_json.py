import json

from radar_ufersa.logging_json import JsonLineLogger
from tests.fakes import FakeTextSink


def test_json_line_logger_writes_structured_event() -> None:
    sink = FakeTextSink()
    logger = JsonLineLogger(sink)

    logger.write("info", "scan_finished", {"items": 3, "ok": True})

    payload = json.loads(sink.lines[0])
    assert payload["level"] == "info"
    assert payload["event"] == "scan_finished"
    assert payload["items"] == 3
    assert payload["ok"] is True
    assert "timestamp" in payload
