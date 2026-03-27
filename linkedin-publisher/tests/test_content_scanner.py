"""Tests for publisher.content_scanner — ContentScanner and BlogPost."""
# Author: Steve Bartimote
# © Steve Bartimote. All rights reserved.
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import pytest

from publisher.content_scanner import BlogPost, ContentScanner

SAMPLE_FM = """\
---
title: Test Post
description: A test post.
date: 2024-01-15T00:00:00+00:00
tags: [security, ctf]
linkedin_queue: true
linkedin_posted: false
---
This is the post body.
"""

OLDER_FM = SAMPLE_FM.replace("2024-01-15", "2023-06-01")
NOT_QUEUED_FM = SAMPLE_FM.replace("linkedin_queue: true", "linkedin_queue: false")
POSTED_FM = SAMPLE_FM.replace("linkedin_posted: false", "linkedin_posted: true")


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def scanner(content_dir: Path) -> ContentScanner:
    (content_dir / "queued-post.md").write_text(SAMPLE_FM)
    return ContentScanner(content_dir)


def test_init_rejects_missing_dir() -> None:
    with pytest.raises(ValueError, match="does not exist"):
        ContentScanner(Path("/nonexistent/path/that/cannot/exist"))


def test_scan_queued_empty(content_dir: Path) -> None:
    result = ContentScanner(content_dir).scan_queued()
    assert result == []


def test_scan_queued_returns_matching_post(scanner: ContentScanner) -> None:
    posts = scanner.scan_queued()
    assert len(posts) == 1
    assert posts[0].slug == "queued-post"


def test_scan_queued_skips_posted(content_dir: Path) -> None:
    (content_dir / "p.md").write_text(POSTED_FM)
    assert ContentScanner(content_dir).scan_queued() == []


def test_scan_queued_skips_not_queued(content_dir: Path) -> None:
    (content_dir / "p.md").write_text(NOT_QUEUED_FM)
    assert ContentScanner(content_dir).scan_queued() == []


def test_scan_queued_sorted_newest_first(content_dir: Path) -> None:
    (content_dir / "old.md").write_text(OLDER_FM)
    (content_dir / "new.md").write_text(SAMPLE_FM)
    assert [p.slug for p in ContentScanner(content_dir).scan_queued()] == ["new", "old"]


def test_scan_queued_skips_index_files(content_dir: Path) -> None:
    (content_dir / "_index.md").write_text(SAMPLE_FM)
    scanner = ContentScanner(content_dir)
    assert scanner.scan_queued() == []


def test_get_post_missing_returns_none(content_dir: Path) -> None:
    assert ContentScanner(content_dir).get_post("missing") is None


def test_get_post_returns_blog_post(scanner: ContentScanner) -> None:
    post = scanner.get_post("queued-post")
    assert post is not None
    assert post.title == "Test Post"


def test_mark_posted_sets_posted_true(content_dir: Path) -> None:
    (content_dir / "p.md").write_text(SAMPLE_FM)
    ContentScanner(content_dir).mark_posted("p")
    assert frontmatter.load(str(content_dir / "p.md"))["linkedin_posted"] is True


def test_mark_posted_clears_queue_flag(content_dir: Path) -> None:
    (content_dir / "p.md").write_text(SAMPLE_FM)
    ContentScanner(content_dir).mark_posted("p")
    assert frontmatter.load(str(content_dir / "p.md"))["linkedin_queue"] is False


def test_mark_posted_raises_when_missing(content_dir: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ContentScanner(content_dir).mark_posted("missing")


def test_site_url_format() -> None:
    post = BlogPost(
        slug="hello-world",
        title="Hello",
        description="",
        date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        tags=[],
        path=Path("/tmp/x.md"),
    )
    assert post.site_url == "https://pwnagebybutchy.me/blog/hello-world/"


def test_linkedin_preview_contains_metadata() -> None:
    post = BlogPost(
        slug="s",
        title="My Post",
        description="A description.",
        date=datetime(2024, 1, 15, tzinfo=timezone.utc),
        tags=["ctf"],
        path=Path("/tmp/s.md"),
        content="Post body text.",
    )
    preview = post.linkedin_preview
    assert "My Post" in preview
    assert "A description." in preview
    assert "ctf" in preview
    assert "Post body text." in preview


def test_linkedin_preview_truncates_long_content() -> None:
    post = BlogPost(
        slug="s",
        title="T",
        description="",
        date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        tags=[],
        path=Path("/tmp/s.md"),
        content="x" * 600,
    )
    assert "…" in post.linkedin_preview


def test_naive_date_gets_utc(content_dir: Path) -> None:
    fm = SAMPLE_FM.replace("2024-01-15T00:00:00+00:00", "2024-01-15T00:00:00")
    (content_dir / "naive.md").write_text(fm)
    post = ContentScanner(content_dir).get_post("naive")
    assert post is not None and post.date.tzinfo is not None
