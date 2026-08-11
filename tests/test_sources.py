import pytest

from radar_ufersa.sources import build_source_catalog


def test_build_source_catalog_uses_requested_year() -> None:
    sources = build_source_catalog(2026)

    urls = {source.key: source.url for source in sources}
    assert len(sources) == 8
    assert urls["proppg-editais"].endswith("/editais-2026/")
    assert urls["proec-editais"].endswith("/editais-2026/")
    assert urls["portarias-reitoria"].endswith("/ano2026/")
    assert "portarias-prograd-2026" in urls["portarias-prograd"]


def test_build_source_catalog_rejects_implausible_year() -> None:
    with pytest.raises(ValueError, match="year=2019.*integer >= 2020"):
        build_source_catalog(2019)
