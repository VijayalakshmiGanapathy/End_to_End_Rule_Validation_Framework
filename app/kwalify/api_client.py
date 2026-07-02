"""
Reusable API client for Kwalify services.
"""

import time
from typing import Any, Optional

import requests

from app.kwalify.config import MAX_RETRIES, RETRY_DELAY


class APIClient:
    """Shared HTTP client for all API communication."""

    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def set_token(self, token: str) -> None:
        """Store JWT token and update session headers."""
        self.token = token

        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        })

    def clear_token(self) -> None:
        """Clear authentication."""
        self.token = None
        self.session.headers.pop("Authorization", None)

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> requests.Response:

        last_exception = None

        for attempt in range(1, MAX_RETRIES + 1):

            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=300,
                    **kwargs,
                )

                # response.raise_for_status()
                if not response.ok:
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.text}")
                    response.raise_for_status()

                return response

            except requests.RequestException as exc:

                last_exception = exc

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

        raise last_exception

    def get(
        self,
        url: str,
        params: Optional[dict] = None,
    ):
        return self.request("GET", url, params=params)

    def post(
        self,
        url: str,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        files=None,
        data=None,
    ):
        return self.request(
            "POST",
            url,
            params=params,
            json=json,
            files=files,
            data=data,
        )

    def put(self, url: str, **kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("DELETE", url, **kwargs)