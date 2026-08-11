from pathlib import Path
from typing import Mapping, Protocol

from radar_ufersa.models import (
    CollectionResult,
    PageAnchor,
    ScoredOpportunity,
    SeenState,
    SourceDefinition,
)

JsonScalar = str | int | float | bool | None


class HttpClient(Protocol):
    def get_text(self, url: str) -> str: ...

    def post_form(self, url: str, form: Mapping[str, str]) -> str: ...


class AnchorExtractor(Protocol):
    def extract(self, base_url: str, html: str) -> tuple[PageAnchor, ...]: ...


class SeenStateStore(Protocol):
    def load(self) -> SeenState: ...

    def save(self, state: SeenState) -> None: ...


class OpportunityNotifier(Protocol):
    def send(self, opportunity: ScoredOpportunity) -> None: ...


class RadarLogger(Protocol):
    def write(
        self, level: str, event: str, fields: Mapping[str, JsonScalar]
    ) -> None: ...


class TextFileGateway(Protocol):
    def read_text(self, path: Path) -> str | None: ...

    def write_text(self, path: Path, content: str) -> None: ...


class TextSink(Protocol):
    def write_line(self, text: str) -> None: ...


class CandidateCollector(Protocol):
    def collect_all(
        self, sources: tuple[SourceDefinition, ...]
    ) -> CollectionResult: ...
