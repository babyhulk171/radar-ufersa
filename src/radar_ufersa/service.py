from radar_ufersa.errors import ExternalServiceError
from radar_ufersa.identity import build_candidate_fingerprint
from radar_ufersa.models import (
    OpportunityCandidate,
    RelevanceRule,
    RunSummary,
    ScoredOpportunity,
    SeenState,
    SourceDefinition,
)
from radar_ufersa.ports import (
    CandidateCollector,
    OpportunityNotifier,
    RadarLogger,
    SeenStateStore,
)
from radar_ufersa.relevance import score_candidate


class RadarService:
    def __init__(
        self,
        collector: CandidateCollector,
        state_store: SeenStateStore,
        notifier: OpportunityNotifier,
        logger: RadarLogger,
        rules: tuple[RelevanceRule, ...],
        minimum_score: int,
    ) -> None:
        self._collector = collector
        self._state_store = state_store
        self._notifier = notifier
        self._logger = logger
        self._rules = rules
        self._minimum_score = minimum_score

    def run(
        self, sources: tuple[SourceDefinition, ...], notify_existing: bool
    ) -> RunSummary:
        """Runs one scan; example: ``service.run(sources, False)`` performs daily work."""
        collection = self._collector.collect_all(sources)
        relevant = self._score_relevant(collection.candidates)
        unique_relevant = self._deduplicate_relevant(relevant)
        previous_state = self._state_store.load()
        if not previous_state.initialized and not notify_existing:
            return self._bootstrap(
                collection.failed_sources, collection.candidates, unique_relevant
            )

        sent, failed, updated_state = self._notify_new(unique_relevant, previous_state)
        self._state_store.save(updated_state)
        return RunSummary(
            len(collection.candidates), len(unique_relevant), sent, failed,
            collection.failed_sources, False,
        )

    def _score_relevant(
        self, candidates: tuple[OpportunityCandidate, ...]
    ) -> tuple[ScoredOpportunity, ...]:
        scored = (
            score_candidate(candidate, self._rules, self._minimum_score)
            for candidate in candidates
        )
        return tuple(opportunity for opportunity in scored if opportunity is not None)

    def _deduplicate_relevant(
        self, opportunities: tuple[ScoredOpportunity, ...]
    ) -> tuple[ScoredOpportunity, ...]:
        unique: dict[str, ScoredOpportunity] = {}
        for opportunity in opportunities:
            fingerprint = build_candidate_fingerprint(opportunity.candidate)
            unique.setdefault(fingerprint, opportunity)
        return tuple(unique.values())

    def _bootstrap(
        self,
        failed_sources: int,
        candidates: tuple[OpportunityCandidate, ...],
        opportunities: tuple[ScoredOpportunity, ...],
    ) -> RunSummary:
        fingerprints = frozenset(
            build_candidate_fingerprint(opportunity.candidate)
            for opportunity in opportunities
        )
        self._state_store.save(SeenState(True, fingerprints))
        self._logger.write("info", "state_bootstrapped", {"items": len(fingerprints)})
        return RunSummary(
            len(candidates), len(opportunities), 0, 0, failed_sources, True
        )

    def _notify_new(
        self,
        opportunities: tuple[ScoredOpportunity, ...],
        previous_state: SeenState,
    ) -> tuple[int, int, SeenState]:
        fingerprints = set(previous_state.fingerprints)
        sent = 0
        failed = 0
        for opportunity in opportunities:
            fingerprint = build_candidate_fingerprint(opportunity.candidate)
            if fingerprint in fingerprints:
                continue
            if not self._try_notify(opportunity):
                failed += 1
                continue
            fingerprints.add(fingerprint)
            sent += 1
        return sent, failed, SeenState(True, frozenset(fingerprints))

    def _try_notify(self, opportunity: ScoredOpportunity) -> bool:
        try:
            self._notifier.send(opportunity)
            return True
        except ExternalServiceError as exception:
            self._logger.write(
                "error",
                "notification_failed",
                {"url": opportunity.candidate.url, "error": str(exception)},
            )
            return False
