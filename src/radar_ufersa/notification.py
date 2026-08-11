import json

from radar_ufersa.errors import ExternalServiceError
from radar_ufersa.models import ScoredOpportunity
from radar_ufersa.ports import HttpClient


def build_telegram_message(opportunity: ScoredOpportunity) -> str:
    """Builds the concise Telegram alert shown for a newly detected opportunity.

    Example: ``build_telegram_message(opportunity)`` returns ready-to-send text.
    """
    candidate = opportunity.candidate
    terms = ", ".join(opportunity.matched_terms[:5])
    return "\n".join(
        (
            "🚨 Nova oportunidade UFERSA",
            "",
            f"📌 {candidate.title}",
            f"🏢 {candidate.source_label}",
            f"🏷 {opportunity.category.value}",
            f"⭐ Relevância: {opportunity.score}",
            f"🔎 Termos: {terms}",
            "",
            f"🔗 {candidate.url}",
        )
    )


class TelegramOpportunityNotifier:
    def __init__(self, http_client: HttpClient, token: str, chat_id: str) -> None:
        self._http_client = http_client
        self._token = token
        self._chat_id = chat_id

    def send(self, opportunity: ScoredOpportunity) -> None:
        """Sends one scored opportunity through Telegram's sendMessage endpoint.

        Example: ``notifier.send(opportunity)`` posts a single Telegram message.
        """
        endpoint = f"https://api.telegram.org/bot{self._token}/sendMessage"
        form = {
            "chat_id": self._chat_id,
            "text": build_telegram_message(opportunity),
            "link_preview_options": json.dumps({"is_disabled": True}),
        }
        try:
            self._http_client.post_form(endpoint, form)
        except ExternalServiceError as exception:
            raise ExternalServiceError(
                f"Telegram send failed for chat_id={self._chat_id!r}; "
                f"cause={exception}; "
                "expected Bot API sendMessage success."
            ) from exception
