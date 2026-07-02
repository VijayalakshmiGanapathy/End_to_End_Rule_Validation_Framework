"""
Authentication manager.
"""

import os

from dotenv import load_dotenv

from app.kwalify.constants import (
    AUTH_BASE_URL,
    LOGIN_ENDPOINT,
)

from app.kwalify.config import (
    
    FRONTEND_USERNAME,
    FRONTEND_PASSWORD,
)

load_dotenv(override=True)


class AuthManager:
    """Handles authentication."""

    def __init__(self, client):
        self.client = client

    def login(self):

        payload = {
            "username": FRONTEND_USERNAME,
            "password": FRONTEND_PASSWORD,
        }

        print("Username:", FRONTEND_USERNAME)
        print("Password:", FRONTEND_PASSWORD)

        response = self.client.post(
            AUTH_BASE_URL + LOGIN_ENDPOINT,
            json=payload,
        )

        response_json = response.json()

        token = response_json["access_token"]

        self.client.set_token(token)

        return token