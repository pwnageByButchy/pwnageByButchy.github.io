"""Tests for publisher.linkedin_client — OAuth client and API calls."""
# Author: Steve Bartimote
# © Steve Bartimote. All rights reserved.
from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from publisher.linkedin_client import LinkedInAPIError, LinkedInAuthError, LinkedInClient, LinkedInError


@pytest.fixture
def client() -> LinkedInClient:
    return LinkedInClient("test_id", "test_secret", "http://localhost:8080/callback")


def test_error_hierarchy() -> None:
    assert issubclass(LinkedInAuthError, LinkedInError)
    assert issubclass(LinkedInAPIError, LinkedInError)


def test_load_tokens_false_when_no_file(client: LinkedInClient, tmp_path: Path) -> None:
    with patch("publisher.linkedin_client._TOKENS_FILE", tmp_path / "no.json"):
        assert client.load_tokens() is False


def test_load_tokens_true_with_valid_token(client: LinkedInClient, tmp_path: Path) -> None:
    (tmp_path / "tokens.json").write_text('{"access_token": "tok123"}')
    with patch("publisher.linkedin_client._TOKENS_FILE", tmp_path / "tokens.json"):
        assert client.load_tokens() is True


def test_load_tokens_false_on_bad_json(client: LinkedInClient, tmp_path: Path) -> None:
    (tmp_path / "tokens.json").write_text("not json")
    with patch("publisher.linkedin_client._TOKENS_FILE", tmp_path / "tokens.json"):
        assert client.load_tokens() is False


def test_ensure_valid_token_raises_without_token(client: LinkedInClient) -> None:
    with pytest.raises(LinkedInAuthError):
        client._ensure_valid_token()


def test_handle_token_response_raises_on_non_200(client: LinkedInClient) -> None:
    mock_resp = MagicMock(status_code=400, text="Bad request")
    with pytest.raises(LinkedInAuthError):
        client._handle_token_response(mock_resp)


def test_handle_token_response_saves_tokens(client: LinkedInClient, tmp_path: Path) -> None:
    token_file = tmp_path / "t.json"
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"access_token": "new_tok", "expires_in": 3600}
    with patch("publisher.linkedin_client._TOKENS_FILE", token_file):
        client._handle_token_response(mock_resp)
    data = json.loads(token_file.read_text())
    assert data["access_token"] == "new_tok"
    assert "expires_at" in data


def test_get_person_urn_caches_result(client: LinkedInClient) -> None:
    client._tokens = {"access_token": "tok"}
    mock_resp = MagicMock(ok=True)
    mock_resp.json.return_value = {"sub": "abc123"}
    with patch("requests.get", return_value=mock_resp) as mock_get:
        client._get_person_urn()
        client._get_person_urn()
    assert mock_get.call_count == 1


def test_create_post_returns_post_id(client: LinkedInClient) -> None:
    client._tokens = {"access_token": "tok"}
    client._person_urn = "urn:li:person:123"
    mock_resp = MagicMock(ok=True)
    mock_resp.json.return_value = {"id": "urn:li:ugcPost:456"}
    with patch("requests.post", return_value=mock_resp) as mock_post:
        post_id = client.create_post(text="Hello LinkedIn", article_url="https://example.com")
    assert post_id == "urn:li:ugcPost:456"
    assert mock_post.called


def test_ensure_valid_token_refreshes_when_expired(client: LinkedInClient, tmp_path: Path) -> None:
    expired = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    client._tokens = {"access_token": "old", "refresh_token": "ref", "expires_at": expired}
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"access_token": "new_tok", "expires_in": 3600}
    with patch("requests.post", return_value=mock_resp), \
         patch("publisher.linkedin_client._TOKENS_FILE", tmp_path / "t.json"):
        client._ensure_valid_token()
    assert client._tokens["access_token"] == "new_tok"
