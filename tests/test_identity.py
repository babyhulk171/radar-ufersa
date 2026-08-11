from radar_ufersa.identity import build_candidate_fingerprint
from radar_ufersa.models import OpportunityCandidate


def test_build_candidate_fingerprint_is_stable_across_sources() -> None:
    first = OpportunityCandidate("a", "Fonte A", " Edital X ", "https://x.test/1")
    second = OpportunityCandidate("b", "Fonte B", "Edital X", "https://x.test/1")

    assert build_candidate_fingerprint(first) == build_candidate_fingerprint(second)


def test_build_candidate_fingerprint_changes_with_visible_identity() -> None:
    first = OpportunityCandidate("a", "Fonte", "Edital X", "https://x.test/1")
    second = OpportunityCandidate("a", "Fonte", "Edital Y", "https://x.test/1")

    assert build_candidate_fingerprint(first) != build_candidate_fingerprint(second)
