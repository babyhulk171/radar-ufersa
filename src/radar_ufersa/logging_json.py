import json
from datetime import UTC, datetime
from typing import Mapping

from radar_ufersa.ports import JsonScalar, TextSink


class JsonLineLogger:
    def __init__(self, sink: TextSink) -> None:
        self._sink = sink

    def write(
        self,
        level: str,
        event: str,
        fields: Mapping[str, JsonScalar],
    ) -> None:
        """Writes one structured JSON log event to the injected sink.

        Example: ``logger.write('info', 'scan_started', {'sources': 7})``.
        """
        payload: dict[str, JsonScalar] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "event": event,
        }
        payload.update(fields)
        self._sink.write_line(json.dumps(payload, ensure_ascii=False, sort_keys=True))
