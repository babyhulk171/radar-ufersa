from radar_ufersa.models import OpportunityCandidate, OpportunityCategory
from radar_ufersa.relevance import (
    DEFAULT_MINIMUM_SCORE,
    DEFAULT_RELEVANCE_RULES,
    score_candidate,
)


def test_score_candidate_handles_accents_and_prefers_commission_category() -> None:
    candidate = OpportunityCandidate(
        "correcional",
        "Unidade Correcional",
        "Edital para Formação de Banco de Servidores para Comissão Correcional",
        "https://example.test/edital",
    )

    scored = score_candidate(candidate, DEFAULT_RELEVANCE_RULES, DEFAULT_MINIMUM_SCORE)

    assert scored is not None
    assert scored.score >= 10
    assert scored.category == OpportunityCategory.COMMISSION
    assert "banco de servidores" in scored.matched_terms


def test_score_candidate_rejects_student_or_external_selection_noise() -> None:
    candidate = OpportunityCandidate(
        "noticias",
        "Notícias",
        "Edital de processo seletivo para Professor Substituto",
        "https://example.test/professor",
    )

    scored = score_candidate(candidate, DEFAULT_RELEVANCE_RULES, DEFAULT_MINIMUM_SCORE)

    assert scored is None


def test_score_candidate_detects_formador_opportunity() -> None:
    candidate = OpportunityCandidate(
        "progepe",
        "PROGEPE",
        "Edital para Seleção de Formadores internos da UFERSA",
        "https://example.test/formadores",
    )

    scored = score_candidate(candidate, DEFAULT_RELEVANCE_RULES, DEFAULT_MINIMUM_SCORE)

    assert scored is not None
    assert scored.category == OpportunityCategory.TEACHING
