"""Tests for the chat API endpoint.

These tests require mocking the app infrastructure (Firebase, DB, Settings)
since we're testing in isolation without the full environment.
"""
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Pre-mock external dependencies before any app imports
firebase_admin_mock = MagicMock()
sys.modules.setdefault("firebase_admin", firebase_admin_mock)
sys.modules.setdefault("firebase_admin.auth", MagicMock())
sys.modules.setdefault("firebase_admin.credentials", MagicMock())
sys.modules.setdefault("asyncpg", MagicMock())

# Set env vars before Settings is imported
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/test")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("FIREBASE_CREDENTIALS_PATH", __file__)
os.environ.setdefault("OPENAI_API_KEY", "test-key")

# Now we can safely import app modules
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.security import get_firebase_claims  # noqa: E402
from app.api.chat import router as chat_router  # noqa: E402
from app.schema.chat import ChatMessageResponse, SourceReference  # noqa: E402
from app.services.chat.prompts import DISCLAIMER_PT  # noqa: E402


def _create_test_app() -> FastAPI:
    """Create a minimal FastAPI app with just the chat router for testing."""
    app = FastAPI()
    app.include_router(chat_router)
    return app


@pytest.fixture
def mock_response():
    return ChatMessageResponse(
        answer="A dengue e causada pelo virus DENV.",
        sources=[SourceReference(type="general_knowledge", detail="Modelo GPT")],
        disclaimer=DISCLAIMER_PT,
    )


@pytest.fixture
def client(mock_response):
    """Create test client with mocked dependencies."""
    app = _create_test_app()

    app.dependency_overrides[get_firebase_claims] = lambda: {
        "uid": "test-user-123",
        "email": "test@example.com",
    }

    with patch("app.api.chat.run_agent", new_callable=AsyncMock) as mock_run, \
         patch("app.api.chat._get_agent") as mock_get:

        mock_get.return_value = MagicMock()
        mock_run.return_value = mock_response

        with TestClient(app) as c:
            yield c


class TestChatEndpoint:
    def test_authenticated_request(self, client):
        response = client.post(
            "/chat/message",
            json={"message": "O que causa dengue?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "disclaimer" in data

    def test_empty_message_returns_422(self, client):
        response = client.post(
            "/chat/message",
            json={"message": ""},
        )
        assert response.status_code == 422

    def test_missing_message_field_returns_422(self, client):
        response = client.post(
            "/chat/message",
            json={},
        )
        assert response.status_code == 422

    def test_response_structure(self, client):
        response = client.post(
            "/chat/message",
            json={"message": "Qual a previsao de dengue?"},
        )
        data = response.json()
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["disclaimer"], str)
        assert len(data["disclaimer"]) > 0


class TestChatEndpointUnauthenticated:
    def test_no_token_returns_401_or_403(self):
        """Without valid token, request is rejected."""
        app = _create_test_app()

        with TestClient(app) as c:
            response = c.post(
                "/chat/message",
                json={"message": "O que causa dengue?"},
            )
            # 403 if no credentials header, 401 if invalid token
            assert response.status_code in (401, 403)
