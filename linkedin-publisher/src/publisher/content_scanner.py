"""
Scans Hugo blog content for posts queued for LinkedIn publishing.

Author: Steve Bartimote
© Steve Bartimote. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import frontmatter

logger = logging.getLogger(__name__)


@dataclass
class BlogPost:
    """Represents a Hugo blog post with LinkedIn publishing metadata."""

    slug: str
    title: str
    description: str
    date: datetime
    tags: list[str]
    path: Path
    linkedin_queue: bool = False
    linkedin_posted: bool = False
    linkedin_posted_at: str = ""
    content: str = field(default="", repr=False)

    @property
    def site_url(self) -> str:
        """Constructs the expected public URL for this post."""
        return f"https://pwnagebybutchy.me/blog/{self.slug}/"

    @property
    def linkedin_preview(self) -> str:
        """Returns a formatted preview suitable for LinkedIn vetting."""
        tag_str = ", ".join(self.tags) if self.tags else "none"
        content_preview = self.content[:500].strip()
        if len(self.content) > 500:
            content_preview += "…"
        return "\n".join([
            f"Title:       {self.title}",
            f"Date:        {self.date.strftime('%d %B %Y')}",
            f"Tags:        {tag_str}",
            f"URL:         {self.site_url}",
            "",
            "--- Description ---",
            self.description or "(no description set)",
            "",
            "--- Content preview (first 500 chars) ---",
            content_preview,
        ])


class ContentScanner:
    """Scans Hugo content directory for posts queued for LinkedIn publishing."""

    def __init__(self, content_dir: Path) -> None:
        """Initialise the scanner with the Hugo blog content directory."""
        if not content_dir.is_dir():
            raise ValueError(f"Content directory does not exist: {content_dir}")
        self._content_dir = content_dir

    def scan_queued(self) -> list[BlogPost]:
        """Return all posts with linkedin_queue=true and linkedin_posted=false, newest first."""
        queued: list[BlogPost] = []
        for md_file in self._content_dir.glob("*.md"):
            if md_file.name.startswith("_"):
                continue  # skip section index files
            try:
                raw = frontmatter.load(str(md_file))
                post = self._parse(md_file, raw)
                if post.linkedin_queue and not post.linkedin_posted:
                    queued.append(post)
            except Exception:
                logger.warning("Failed to parse %s", md_file, exc_info=True)
        return sorted(queued, key=lambda p: p.date, reverse=True)

    def get_post(self, slug: str) -> BlogPost | None:
        """Return the parsed BlogPost for the given slug, or None if not found."""
        try:
            return self._parse(*self._open_or_raise(slug))
        except FileNotFoundError:
            return None

    def mark_posted(self, slug: str, posted_at: datetime | None = None) -> None:
        """Update front matter to record that a post has been published to LinkedIn.

        Raises FileNotFoundError if the post file does not exist.
        """
        path, post = self._open_or_raise(slug)
        post["linkedin_posted"] = True
        post["linkedin_queue"] = False
        post["linkedin_posted_at"] = (posted_at or datetime.now(timezone.utc)).isoformat()
        with path.open("w", encoding="utf-8") as fh:
            fh.write(frontmatter.dumps(post))
        logger.info("Marked %s as posted to LinkedIn", slug)

    def _open_or_raise(self, slug: str) -> tuple[Path, frontmatter.Post]:
        """Resolve a slug to its path and loaded frontmatter, raising FileNotFoundError if absent."""
        path = self._content_dir / f"{slug}.md"
        if not path.exists():
            raise FileNotFoundError(f"Post not found: {path}")
        return path, frontmatter.load(str(path))

    def _parse(self, md_file: Path, post: frontmatter.Post) -> BlogPost:
        """Build a BlogPost from a pre-loaded frontmatter Post and its source path."""
        meta = post.metadata
        raw_date = meta.get("date", datetime.now(timezone.utc))
        if isinstance(raw_date, str):
            raw_date = datetime.fromisoformat(raw_date)
        if raw_date.tzinfo is None:
            raw_date = raw_date.replace(tzinfo=timezone.utc)
        return BlogPost(
            slug=md_file.stem,
            title=str(meta.get("title", md_file.stem)),
            description=str(meta.get("description", "")),
            date=raw_date,
            tags=list(meta.get("tags", [])),
            path=md_file,
            linkedin_queue=bool(meta.get("linkedin_queue", False)),
            linkedin_posted=bool(meta.get("linkedin_posted", False)),
            linkedin_posted_at=str(meta.get("linkedin_posted_at", "")),
            content=post.content,
        )
