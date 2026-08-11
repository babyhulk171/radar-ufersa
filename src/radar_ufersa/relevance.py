import re
import unicodedata

from radar_ufersa.models import (
    OpportunityCandidate,
    OpportunityCategory,
    RelevanceRule,
    ScoredOpportunity,
)

DEFAULT_MINIMUM_SCORE = 5

DEFAULT_RELEVANCE_RULES: tuple[RelevanceRule, ...] = (
    RelevanceRule("banco de servidores", 10, OpportunityCategory.COMMISSION),
    RelevanceRule("comissao", 7, OpportunityCategory.COMMISSION),
    RelevanceRule("grupo de trabalho", 7, OpportunityCategory.COMMISSION),
    RelevanceRule("comite", 5, OpportunityCategory.COMMISSION),
    RelevanceRule("tecnico administrativo", 8, OpportunityCategory.SELECTION),
    RelevanceRule("servidor", 4, OpportunityCategory.SELECTION),
    RelevanceRule("selecao interna", 6, OpportunityCategory.SELECTION),
    RelevanceRule("chamada interna", 6, OpportunityCategory.SELECTION),
    RelevanceRule("processo seletivo", 3, OpportunityCategory.SELECTION),
    RelevanceRule("credenciamento", 4, OpportunityCategory.SELECTION),
    RelevanceRule("edital", 2, OpportunityCategory.SELECTION),
    RelevanceRule("bolsa", 7, OpportunityCategory.SCHOLARSHIP),
    RelevanceRule("bolsista", 6, OpportunityCategory.SCHOLARSHIP),
    RelevanceRule("projeto", 4, OpportunityCategory.PROJECT),
    RelevanceRule("extensao", 5, OpportunityCategory.PROJECT),
    RelevanceRule("pesquisa", 4, OpportunityCategory.PROJECT),
    RelevanceRule("programa institucional", 3, OpportunityCategory.PROJECT),
    RelevanceRule("tutor", 7, OpportunityCategory.TEACHING),
    RelevanceRule("instrutor", 7, OpportunityCategory.TEACHING),
    RelevanceRule("formador", 7, OpportunityCategory.TEACHING),
    RelevanceRule("fiscal de contrato", 8, OpportunityCategory.OVERSIGHT),
    RelevanceRule("fiscalizacao", 5, OpportunityCategory.OVERSIGHT),
    RelevanceRule("capacitacao", 4, OpportunityCategory.TRAINING),
    RelevanceRule("curso", 2, OpportunityCategory.TRAINING),
    RelevanceRule("evento", 2, OpportunityCategory.TRAINING),
    RelevanceRule("resultado final", -7, None),
    RelevanceRule("resultado preliminar", -6, None),
    RelevanceRule("homologacao", -5, None),
    RelevanceRule("retificacao", -2, None),
    RelevanceRule("discente", -4, None),
    RelevanceRule("aluno", -4, None),
    RelevanceRule("professor substituto", -10, None),
    RelevanceRule("professor visitante", -10, None),
    RelevanceRule("reingresso", -10, None),
    RelevanceRule("reopcao", -10, None),
    RelevanceRule("transferencia", -8, None),
    RelevanceRule("portador de diploma", -10, None),
    RelevanceRule("concurso publico", -8, None),
    RelevanceRule("estagio", -6, None),
)


def score_candidate(
    candidate: OpportunityCandidate,
    rules: tuple[RelevanceRule, ...],
    minimum_score: int,
) -> ScoredOpportunity | None:
    """Scores a publication title and returns it only when it reaches the threshold.

    Example: ``score_candidate(candidate, DEFAULT_RELEVANCE_RULES, 5)``.
    """
    normalized_title = _normalize_search_text(candidate.title)
    matched_rules = tuple(rule for rule in rules if rule.term in normalized_title)
    total_score = sum(rule.points for rule in matched_rules)
    category = _pick_primary_category(matched_rules)
    if total_score < minimum_score or category is None:
        return None

    matched_terms = tuple(rule.term for rule in matched_rules if rule.points > 0)
    return ScoredOpportunity(candidate, total_score, category, matched_terms)


def _normalize_search_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.lower())
    without_marks = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    words_only = re.sub(r"[^a-z0-9]+", " ", without_marks)
    return " ".join(words_only.split())


def _pick_primary_category(
    matched_rules: tuple[RelevanceRule, ...],
) -> OpportunityCategory | None:
    category_scores: dict[OpportunityCategory, int] = {}
    for rule in matched_rules:
        if rule.category is None or rule.points <= 0:
            continue
        previous_score = category_scores.get(rule.category, 0)
        category_scores[rule.category] = previous_score + rule.points

    if not category_scores:
        return None
    return max(category_scores, key=lambda category: category_scores[category])
