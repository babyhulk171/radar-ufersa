from dataclasses import dataclass
from enum import StrEnum


class OpportunityCategory(StrEnum):
    COMMISSION = "Comissões e grupos de trabalho"
    SCHOLARSHIP = "Bolsas"
    PROJECT = "Projetos, pesquisa e extensão"
    TRAINING = "Capacitação e eventos"
    TEACHING = "Tutoria, instrutoria e formação"
    SELECTION = "Processos seletivos e chamadas internas"
    OVERSIGHT = "Fiscalização e gestão"


@dataclass(frozen=True, slots=True)
class SourceDefinition:
    key: str
    label: str
    url: str


@dataclass(frozen=True, slots=True)
class PageAnchor:
    title: str
    url: str


@dataclass(frozen=True, slots=True)
class OpportunityCandidate:
    source_key: str
    source_label: str
    title: str
    url: str


@dataclass(frozen=True, slots=True)
class RelevanceRule:
    term: str
    points: int
    category: OpportunityCategory | None


@dataclass(frozen=True, slots=True)
class ScoredOpportunity:
    candidate: OpportunityCandidate
    score: int
    category: OpportunityCategory
    matched_terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SeenState:
    initialized: bool
    fingerprints: frozenset[str]


@dataclass(frozen=True, slots=True)
class CollectionResult:
    candidates: tuple[OpportunityCandidate, ...]
    failed_sources: int


@dataclass(frozen=True, slots=True)
class RunSummary:
    scanned_candidates: int
    relevant_candidates: int
    sent_notifications: int
    failed_notifications: int
    failed_sources: int
    bootstrapped: bool
