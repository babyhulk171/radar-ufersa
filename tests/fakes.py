from pathlib import Path
from typing import Mapping

from radar_ufersa.errors import ExternalServiceError
from radar_ufersa.models import (
    CollectionResult,
    PageAnchor,
    ScoredOpportunity,
    SeenState,
    SourceDefinition,
)
from radar_ufersa.ports import JsonScalar


class FakeHttpClient:
    def __init__(self) -> None:
        self.pages: dict[str, str] = {}
        self.posts: list[tuple[str, Mapping[str, str]]] = []
        self.failing_get_urls: set[str] = set()
        self.fail_posts = False

    def get_text(self, url: str) -> str:
        if url in self.failing_get_urls:
            raise ExternalServiceError(
                f"Fake GET failed for url={url!r}; expected configured fake page."
            )
        if url not in self.pages:
            raise ExternalServiceError(
                f"Unknown fake url={url!r}; expected a key in FakeHttpClient.pages."
            )
        return self.pages[url]

    def post_form(self, url: str, form: Mapping[str, str]) -> str:
        if self.fail_posts:
            raise ExternalServiceError(
                f"Fake POST failed for url={url!r}; expected fail_posts=False."
            )
        self.posts.append((url, form))
        return '{"ok":true}'


class FakeAnchorExtractor:
    def __init__(self) -> None:
        self.anchors_by_url: dict[str, tuple[PageAnchor, ...]] = {}

    def extract(self, base_url: str, html: str) -> tuple[PageAnchor, ...]:
        del html
        return self.anchors_by_url.get(base_url, ())


class FakeRadarLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, Mapping[str, JsonScalar]]] = []

    def write(
        self, level: str, event: str, fields: Mapping[str, JsonScalar]
    ) -> None:
        self.events.append((level, event, fields))


class FakeTextFileGateway:
    def __init__(self) -> None:
        self.files: dict[Path, str] = {}

    def read_text(self, path: Path) -> str | None:
        return self.files.get(path)

    def write_text(self, path: Path, content: str) -> None:
        self.files[path] = content


class FakeTextSink:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def write_line(self, text: str) -> None:
        self.lines.append(text)


class FakeCollector:
    def __init__(self, result: CollectionResult) -> None:
        self.result = result
        self.received_sources: tuple[SourceDefinition, ...] = ()

    def collect_all(self, sources: tuple[SourceDefinition, ...]) -> CollectionResult:
        self.received_sources = sources
        return self.result


class FakeSeenStateStore:
    def __init__(self, state: SeenState) -> None:
        self.state = state
        self.saved_states: list[SeenState] = []

    def load(self) -> SeenState:
        return self.state

    def save(self, state: SeenState) -> None:
        self.state = state
        self.saved_states.append(state)


class FakeOpportunityNotifier:
    def __init__(self) -> None:
        self.sent: list[ScoredOpportunity] = []
        self.fail_urls: set[str] = set()

    def send(self, opportunity: ScoredOpportunity) -> None:
        if opportunity.candidate.url in self.fail_urls:
            raise ExternalServiceError(
                f"Fake notify failed for url={opportunity.candidate.url!r}; "
                "expected URL outside fail_urls."
            )
        self.sent.append(opportunity)
