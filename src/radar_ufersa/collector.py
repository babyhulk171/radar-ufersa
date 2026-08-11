from radar_ufersa.errors import ExternalServiceError
from radar_ufersa.models import CollectionResult, OpportunityCandidate, SourceDefinition
from radar_ufersa.ports import AnchorExtractor, HttpClient, RadarLogger


class OpportunityCollector:
    def __init__(
        self,
        http_client: HttpClient,
        anchor_extractor: AnchorExtractor,
        logger: RadarLogger,
    ) -> None:
        self._http_client = http_client
        self._anchor_extractor = anchor_extractor
        self._logger = logger

    def collect_all(self, sources: tuple[SourceDefinition, ...]) -> CollectionResult:
        """Collects anchors from every source while isolating individual HTTP failures.

        Example: ``collector.collect_all(sources)`` returns candidates plus failure count.
        """
        candidates: list[OpportunityCandidate] = []
        failed_sources = 0
        for source in sources:
            source_candidates = self._try_collect_source(source)
            if source_candidates is None:
                failed_sources += 1
                continue
            candidates.extend(source_candidates)
        return CollectionResult(tuple(candidates), failed_sources)

    def _try_collect_source(
        self, source: SourceDefinition
    ) -> tuple[OpportunityCandidate, ...] | None:
        try:
            return self._collect_source(source)
        except ExternalServiceError as exception:
            self._logger.write(
                "error",
                "source_fetch_failed",
                {"source": source.label, "url": source.url, "error": str(exception)},
            )
            return None

    def _collect_source(
        self, source: SourceDefinition
    ) -> tuple[OpportunityCandidate, ...]:
        html = self._http_client.get_text(source.url)
        anchors = self._anchor_extractor.extract(source.url, html)
        return tuple(
            OpportunityCandidate(source.key, source.label, anchor.title, anchor.url)
            for anchor in anchors
        )
