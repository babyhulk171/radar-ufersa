from collections.abc import Callable
from typing import Mapping, Protocol

import requests

from radar_ufersa.errors import ExternalServiceError


class ResponseLike(Protocol):
    text: str

    def raise_for_status(self) -> None: ...


class SessionLike(Protocol):
    def get(
        self, url: str, timeout: float, headers: Mapping[str, str]
    ) -> ResponseLike: ...

    def post(
        self,
        url: str,
        data: Mapping[str, str],
        timeout: float,
        headers: Mapping[str, str],
    ) -> ResponseLike: ...


class RequestsHttpClient:
    def __init__(self, session: SessionLike, timeout_seconds: float = 20.0) -> None:
        self._session = session
        self._timeout_seconds = timeout_seconds
        self._headers = {
            "User-Agent": "radar-ufersa/1.0 (+personal opportunity monitor)"
        }

    def get_text(self, url: str) -> str:
        """Fetches one HTTP resource as text using a bounded timeout.

        Example: ``client.get_text('https://example.org')`` returns response text.
        """
        request_call = lambda: self._session.get(
            url, timeout=self._timeout_seconds, headers=self._headers
        )
        return self._execute_http_request("GET", url, request_call)

    def post_form(self, url: str, form: Mapping[str, str]) -> str:
        """Posts URL-encoded form fields and returns the response text.

        Example: ``client.post_form(url, {'chat_id': '1', 'text': 'oi'})``.
        """
        request_call = lambda: self._session.post(
            url, data=form, timeout=self._timeout_seconds, headers=self._headers
        )
        return self._execute_http_request("POST", url, request_call)

    def _execute_http_request(
        self,
        method: str,
        url: str,
        request_call: Callable[[], ResponseLike],
    ) -> str:
        try:
            response = request_call()
            response.raise_for_status()
            return response.text
        except requests.RequestException as exception:
            raise ExternalServiceError(
                f"HTTP {method} failed for url={url!r}; "
                "expected a successful 2xx response."
            ) from exception
