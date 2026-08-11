import hashlib

from radar_ufersa.models import OpportunityCandidate


def build_candidate_fingerprint(candidate: OpportunityCandidate) -> str:
    """Creates a stable identifier from the visible title and canonical URL.

    Example: ``build_candidate_fingerprint(candidate)`` can be stored in state.json.
    """
    identity_text = f"{candidate.title.strip()}\n{candidate.url.strip()}"
    encoded_identity = identity_text.encode("utf-8")
    return hashlib.sha256(encoded_identity).hexdigest()
