import pytest

from radar_ufersa.errors import ExternalServiceError
from radar_ufersa.models import (
    OpportunityCandidate,
    OpportunityCategory,
    ScoredOpportunity,
)
from radar_ufersa.notification import (
    TelegramOpportunityNotifier,
    build_telegram_message,
)
from tests.fakes import FakeHttpClient


def test_build_telegram_message_contains_decision_context() -> None:
    candidate = OpportunityCandidate(
        "correcional",
        "Unidade Correcional",
        "Banco de servidores para comissão",
        "https://example.test/edital",
    )
    opportunity = ScoredOpportunity(
        candidate,
        17,
        OpportunityCategory.COMMISSION,
        ("banco de servidores", "comissao"),
    )

    message = build_telegram_message(opportunity)

    assert "Banco de servidores para comissão" in message
    assert "Comissões e grupos de trabalho" in message
    assert "Relevância: 17" in message
    assert "https://example.test/edital" in message


def test_telegram_notifier_posts_send_message_form() -> None:
    client = FakeHttpClient()
    notifier = TelegramOpportunityNotifier(client, "token123", "chat456")
    candidate = OpportunityCandidate(
        "x", "Fonte", "Projeto de extensão", "https://x.test"
    )
    opportunity = ScoredOpportunity(
        candidate, 9, OpportunityCategory.PROJECT, ("projeto", "extensao")
    )

    notifier.send(opportunity)

    endpoint, form = client.posts[0]
    assert endpoint.endswith("/bottoken123/sendMessage")
    assert form["chat_id"] == "chat456"
    assert "Projeto de extensão" in form["text"]
    assert form["link_preview_options"] == '{"is_disabled": true}'


def test_telegram_notifier_redacts_token_from_raised_error() -> None:
    client = FakeHttpClient()
    client.fail_posts = True
    notifier = TelegramOpportunityNotifier(client, "secret-token", "chat456")
    candidate = OpportunityCandidate(
        "x", "Fonte", "Projeto de extensão", "https://x.test"
    )
    opportunity = ScoredOpportunity(
        candidate, 9, OpportunityCategory.PROJECT, ("projeto", "extensao")
    )

    with pytest.raises(ExternalServiceError) as captured:
        notifier.send(opportunity)

    assert "secret-token" not in str(captured.value)
    assert "chat456" in str(captured.value)
