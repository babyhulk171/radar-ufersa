from radar_ufersa.models import SourceDefinition

_STATIC_SOURCES: tuple[SourceDefinition, ...] = (
    SourceDefinition(
        "progepe-capacitacao",
        "PROGEPE - Capacitação",
        "https://progepe.ufersa.edu.br/editais-sca/",
    ),
    SourceDefinition(
        "unidade-correcional",
        "Unidade Correcional",
        "https://reitoria.ufersa.edu.br/unidade-correcional/",
    ),
    SourceDefinition(
        "assecom",
        "Assecom - Notícias",
        "https://assecom.ufersa.edu.br/",
    ),
    SourceDefinition(
        "cpps-concursos",
        "CPPS - Sistema de Concursos",
        "https://sistemas.ufersa.edu.br/concursos/publico",
    ),
)

_ANNUAL_SOURCE_TEMPLATES: tuple[tuple[str, str, str], ...] = (
    (
        "proppg-editais",
        "PROPPG - Editais",
        "https://proppg.ufersa.edu.br/editais-{year}/",
    ),
    (
        "proec-editais",
        "PROEC - Editais",
        "https://proec.ufersa.edu.br/editais-{year}/",
    ),
    (
        "portarias-reitoria",
        "Portarias da Reitoria",
        "https://documentos.ufersa.edu.br/inicio/reitoria/portarias/ano{year}/",
    ),
    (
        "portarias-prograd",
        "Portarias da PROGRAD",
        (
            "https://documentos.ufersa.edu.br/inicio/pro-reitorias/"
            "prograd/portarias-5-2/portarias-prograd-{year}/"
        ),
    ),
)


def build_source_catalog(year: int) -> tuple[SourceDefinition, ...]:
    """Builds the official UFERSA pages monitored for a given year.

    Example: ``build_source_catalog(2026)`` returns the 2026 annual pages.
    """
    if year < 2020:
        raise ValueError(f"Invalid year={year!r}; expected an integer >= 2020.")

    annual_sources = tuple(
        SourceDefinition(key, label, template.format(year=year))
        for key, label, template in _ANNUAL_SOURCE_TEMPLATES
    )
    return _STATIC_SOURCES + annual_sources
