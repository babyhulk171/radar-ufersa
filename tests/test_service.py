from radar_ufersa.identity import build_candidate_fingerprint
from radar_ufersa.models import (
    CollectionResult,
    OpportunityCandidate,
    SeenState,
    SourceDefinition,
)
from radar_ufersa.relevance import DEFAULT_MINIMUM_SCORE, DEFAULT_RELEVANCE_RULES
from radar_ufersa.service import RadarService
from tests.fakes import (
    FakeCollector,
    FakeOpportunityNotifier,
    FakeRadarLogger,
    FakeSeenStateStore,
)


def test_run_bootstraps_without_sending_existing_items() -> None:
    candidate = OpportunityCandidate(
        "correcional",
        "Unidade Correcional",
        "Edital para banco de servidores em comissão",
        "https://example.test/1",
    )
    collector = FakeCollector(CollectionResult((candidate,), 0))
    store = FakeSeenStateStore(SeenState(False, frozenset()))
    notifier = FakeOpportunityNotifier()
    logger = FakeRadarLogger()
    service = RadarService(
        collector,
        store,
        notifier,
        logger,
        DEFAULT_RELEVANCE_RULES,
        DEFAULT_MINIMUM_SCORE,
    )

    summary = service.run((SourceDefinition("x", "X", "https://x.test"),), False)

    assert summary.bootstrapped is True
    assert summary.sent_notifications == 0
    assert notifier.sent == []
    assert len(store.state.fingerprints) == 1
    assert logger.events[0][1] == "state_bootstrapped"


def test_run_notify_existing_sends_on_uninitialized_state() -> None:
    candidate = OpportunityCandidate(
        "progepe",
        "PROGEPE",
        "Edital para seleção de formadores internos",
        "https://example.test/formadores",
    )
    collector = FakeCollector(CollectionResult((candidate,), 0))
    store = FakeSeenStateStore(SeenState(False, frozenset()))
    notifier = FakeOpportunityNotifier()
    logger = FakeRadarLogger()
    service = RadarService(
        collector,
        store,
        notifier,
        logger,
        DEFAULT_RELEVANCE_RULES,
        DEFAULT_MINIMUM_SCORE,
    )

    summary = service.run((), True)

    assert summary.sent_notifications == 1
    assert len(notifier.sent) == 1
    assert store.state.initialized is True


def test_run_only_sends_new_fingerprints_and_deduplicates() -> None:
    seen_candidate = OpportunityCandidate(
        "proec", "PROEC", "Projeto de extensão com bolsa", "https://example.test/seen"
    )
    new_candidate = OpportunityCandidate(
        "proppg", "PROPPG", "Projeto de pesquisa com bolsa", "https://example.test/new"
    )
    duplicate_new = OpportunityCandidate(
        "assecom",
        "Assecom",
        "Projeto de pesquisa com bolsa",
        "https://example.test/new",
    )
    seen_id = build_candidate_fingerprint(seen_candidate)
    collector = FakeCollector(
        CollectionResult((seen_candidate, new_candidate, duplicate_new), 0)
    )
    store = FakeSeenStateStore(SeenState(True, frozenset({seen_id})))
    notifier = FakeOpportunityNotifier()
    logger = FakeRadarLogger()
    service = RadarService(
        collector,
        store,
        notifier,
        logger,
        DEFAULT_RELEVANCE_RULES,
        DEFAULT_MINIMUM_SCORE,
    )

    summary = service.run((), False)

    assert summary.relevant_candidates == 2
    assert summary.sent_notifications == 1
    assert notifier.sent[0].candidate.url == "https://example.test/new"
    assert len(store.state.fingerprints) == 2


def test_run_does_not_mark_failed_notification_as_seen() -> None:
    candidate = OpportunityCandidate(
        "proppg", "PROPPG", "Projeto de pesquisa com bolsa", "https://example.test/fail"
    )
    collector = FakeCollector(CollectionResult((candidate,), 1))
    store = FakeSeenStateStore(SeenState(True, frozenset()))
    notifier = FakeOpportunityNotifier()
    notifier.fail_urls.add(candidate.url)
    logger = FakeRadarLogger()
    service = RadarService(
        collector,
        store,
        notifier,
        logger,
        DEFAULT_RELEVANCE_RULES,
        DEFAULT_MINIMUM_SCORE,
    )

    summary = service.run((), False)

    assert summary.failed_notifications == 1
    assert summary.failed_sources == 1
    assert store.state.fingerprints == frozenset()
    assert logger.events[0][1] == "notification_failed"
