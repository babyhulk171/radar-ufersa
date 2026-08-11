from radar_ufersa.collector import OpportunityCollector
from radar_ufersa.models import PageAnchor, SourceDefinition
from tests.fakes import FakeAnchorExtractor, FakeHttpClient, FakeRadarLogger


def test_collect_all_converts_anchors_to_candidates() -> None:
    source = SourceDefinition("progepe", "PROGEPE", "https://example.test/progepe")
    http_client = FakeHttpClient()
    http_client.pages[source.url] = "<html></html>"
    extractor = FakeAnchorExtractor()
    extractor.anchors_by_url[source.url] = (
        PageAnchor("Edital para servidores", "https://example.test/edital"),
    )
    logger = FakeRadarLogger()
    collector = OpportunityCollector(http_client, extractor, logger)

    result = collector.collect_all((source,))

    assert result.failed_sources == 0
    assert result.candidates[0].source_key == "progepe"
    assert result.candidates[0].title == "Edital para servidores"


def test_collect_all_isolates_source_fetch_failure() -> None:
    failing = SourceDefinition("a", "Fonte A", "https://example.test/a")
    healthy = SourceDefinition("b", "Fonte B", "https://example.test/b")
    http_client = FakeHttpClient()
    http_client.failing_get_urls.add(failing.url)
    http_client.pages[healthy.url] = "<html></html>"
    extractor = FakeAnchorExtractor()
    extractor.anchors_by_url[healthy.url] = (
        PageAnchor("Projeto de extensão", "https://example.test/projeto"),
    )
    logger = FakeRadarLogger()
    collector = OpportunityCollector(http_client, extractor, logger)

    result = collector.collect_all((failing, healthy))

    assert result.failed_sources == 1
    assert len(result.candidates) == 1
    assert logger.events[0][1] == "source_fetch_failed"
