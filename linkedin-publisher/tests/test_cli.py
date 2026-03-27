"""Tests for publisher.cli — Click CLI commands and _build_post_text helper."""
# Author: Steve Bartimote
# © Steve Bartimote. All rights reserved.
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner
from publisher.cli import _build_post_text, main
from publisher.content_scanner import BlogPost
from publisher.linkedin_client import LinkedInAuthError


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_scanner(monkeypatch, tmp_path: Path):
    """Provide a mock ContentScanner for CLI tests, with a valid content dir set."""
    monkeypatch.setenv("HUGO_CONTENT_PATH", str(tmp_path))
    with patch("publisher.cli.ContentScanner") as mock_cs:
        mock_cs.return_value.scan_queued.return_value = []
        mock_cs.return_value.get_post.return_value = None
        mock_cs.return_value.mark_posted.return_value = None
        yield mock_cs.return_value


@pytest.fixture
def mock_post() -> BlogPost:
    return BlogPost(
        slug="test-post",
        title="Test Post",
        description="A test description.",
        date=datetime(2024, 1, 15, tzinfo=timezone.utc),
        tags=["ctf", "security"],
        path=Path("/tmp/test-post.md"),
        linkedin_queue=True,
        linkedin_posted=False,
        content="Test content here.",
    )


def test_auth_success(runner: CliRunner) -> None:
    with patch("publisher.cli._client"):
        result = runner.invoke(main, ["auth"])
    assert result.exit_code == 0


def test_auth_failure(runner: CliRunner) -> None:
    with patch("publisher.cli._client") as m:
        m.return_value.authenticate.side_effect = LinkedInAuthError("bad creds")
        result = runner.invoke(main, ["auth"])
    assert result.exit_code == 1
    assert "Authentication failed" in result.output
    assert "bad creds" in result.output
    assert m.called


def test_list_no_queued(runner: CliRunner, mock_scanner) -> None:
    mock_scanner.scan_queued.return_value = []
    result = runner.invoke(main, ["list"])
    assert "No posts" in result.output


def test_list_with_posts(runner: CliRunner, mock_scanner, mock_post: BlogPost) -> None:
    mock_scanner.scan_queued.return_value = [mock_post]
    result = runner.invoke(main, ["list"])
    assert "test-post" in result.output


def test_review_missing_slug(runner: CliRunner, mock_scanner) -> None:
    mock_scanner.get_post.return_value = None
    result = runner.invoke(main, ["review", "missing"])
    assert result.exit_code == 1


def test_review_shows_preview(runner: CliRunner, mock_scanner, mock_post: BlogPost) -> None:
    mock_scanner.get_post.return_value = mock_post
    result = runner.invoke(main, ["review", "test-post"])
    assert "Test Post" in result.output


def test_publish_missing_post_exits(runner: CliRunner, mock_scanner) -> None:
    mock_scanner.get_post.return_value = None
    result = runner.invoke(main, ["publish", "missing"])
    assert result.exit_code == 1


def test_publish_already_posted_exits(runner: CliRunner, mock_scanner) -> None:
    mock_scanner.get_post.return_value = MagicMock(linkedin_posted=True)
    result = runner.invoke(main, ["publish", "test-post"])
    assert result.exit_code == 1


def test_publish_not_queued_exits(runner: CliRunner, mock_scanner) -> None:
    mock_scanner.get_post.return_value = MagicMock(linkedin_posted=False, linkedin_queue=False)
    result = runner.invoke(main, ["publish", "test-post"])
    assert result.exit_code == 1


def test_publish_success_with_yes_flag(runner: CliRunner, mock_scanner, mock_post: BlogPost) -> None:
    mock_scanner.get_post.return_value = mock_post
    with patch("publisher.cli._client") as mock_c:
        mock_c.return_value.load_tokens.return_value = True
        mock_c.return_value.create_post.return_value = "urn:li:share:456"
        result = runner.invoke(main, ["publish", "--yes", "test-post"])
    assert result.exit_code == 0
    assert "Published successfully" in result.output
    assert "urn:li:share:456" in result.output


def test_publish_no_tokens_exits(runner: CliRunner, mock_scanner, mock_post: BlogPost) -> None:
    mock_scanner.get_post.return_value = mock_post
    with patch("publisher.cli._client") as mock_c:
        mock_c.return_value.load_tokens.return_value = False
        result = runner.invoke(main, ["publish", "--yes", "test-post"])
    assert result.exit_code == 1
    assert "no saved tokens" in result.output
    assert "auth" in result.output


def test_publish_cancelled_on_no(runner: CliRunner, mock_scanner, mock_post: BlogPost) -> None:
    mock_scanner.get_post.return_value = mock_post
    result = runner.invoke(main, ["publish", "test-post"], input="n\n")
    assert "Cancelled" in result.output


def test_build_post_text_includes_description() -> None:
    result = _build_post_text("Title", "Desc", "https://example.com")
    assert "Title" in result
    assert "Desc" in result


def test_build_post_text_no_description() -> None:
    result = _build_post_text("Title", "", "https://example.com")
    assert "Title" in result
    assert "https://example.com" in result
