from typing import Mapping

import pytest
import requests

from radar_ufersa.adapters.http_requests import RequestsHttpClient
from radar_ufersa.errors import ExternalServiceError


class FakeRequestsResponse:
    def __init__(self, text: str, should_fail: bool = False) -> None:
        self.text = text
        self.should_fail = should_fail

    def raise_for_status(self) -> None:
        if self.should_fail:
            raise requests.HTTPError("fake status failure")


class FakeRequestsSession:
    def __init__(self, response: FakeRequestsResponse) -> None:
        self.response = response
        self.get_calls: list[str] = []
        self.post_calls: list[tuple[str, Mapping[str, str]]] = []

    def get(
        self, url: str, timeout: float, headers: Mapping[str, str]
    ) -> FakeRequestsResponse:
        assert timeout > 0
        assert "User-Agent" in headers
        self.get_calls.append(url)
        return self.response

    def post(
        self,
        url: str,
        data: Mapping[str, str],
        timeout: float,
        headers: Mapping[str, str],
    ) -> FakeRequestsResponse:
        assert timeout > 0
        assert "User-Agent" in headers
        self.post_calls.append((url, data))
        return self.response


def test_get_text_returns_response_body() -> None:
    session = FakeRequestsSession(FakeRequestsResponse("conteúdo"))
    client = RequestsHttpClient(session)

    result = client.get_text("https://example.test/page")

    assert result == "conteúdo"
    assert session.get_calls == ["https://example.test/page"]


def test_post_form_sends_injected_fields() -> None:
    session = FakeRequestsSession(FakeRequestsResponse('{"ok":true}'))
    client = RequestsHttpClient(session)

    result = client.post_form("https://example.test/post", {"text": "oi"})

    assert result == '{"ok":true}'
    assert session.post_calls[0][1] == {"text": "oi"}


def test_get_text_wraps_http_error_with_expected_shape() -> None:
    session = FakeRequestsSession(FakeRequestsResponse("erro", should_fail=True))
    client = RequestsHttpClient(session)

    with pytest.raises(
        ExternalServiceError, match="expected a successful 2xx response"
    ):
        client.get_text("https://example.test/fail")


def test_post_form_wraps_http_error_with_expected_shape() -> None:
    session = FakeRequestsSession(FakeRequestsResponse("erro", should_fail=True))
    client = RequestsHttpClient(session)

    with pytest.raises(
        ExternalServiceError, match="expected a successful 2xx response"
    ):
        client.post_form("https://example.test/fail", {"text": "oi"})
