"""
LinkedIn Publisher CLI — review and publish Hugo blog posts to LinkedIn.

Author: Steve Bartimote
© Steve Bartimote. All rights reserved.
Usage:
    linkedin-publisher configure         Save LinkedIn app credentials to the system keyring
    linkedin-publisher auth              Authenticate with LinkedIn (OAuth)
    linkedin-publisher list              List blog posts queued for LinkedIn
    linkedin-publisher review <slug>     Preview a queued post before publishing
    linkedin-publisher publish <slug>    Publish a vetted post to LinkedIn
"""

from __future__ import annotations
import logging
import os
import sys
from pathlib import Path

import click
import keyring
from publisher.content_scanner import ContentScanner
from publisher.linkedin_client import LinkedInAuthError, LinkedInClient

_KEYRING_SERVICE = "linkedin-publisher"

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def _content_dir() -> Path:
    """Resolve Hugo blog content directory from env or default path."""
    raw = os.getenv("HUGO_CONTENT_PATH", "../site/content/blog")
    path = Path(raw).resolve()
    if not path.is_dir():
        click.echo(f"Error: content directory not found: {path}", err=True)
        sys.exit(1)
    return path


def _client() -> LinkedInClient:
    """Build a LinkedInClient from the system keyring, falling back to env vars."""
    client_id = keyring.get_password(_KEYRING_SERVICE, "client_id") or os.getenv("LINKEDIN_CLIENT_ID", "")
    client_secret = keyring.get_password(_KEYRING_SERVICE, "client_secret") or os.getenv("LINKEDIN_CLIENT_SECRET", "")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
    if not client_id or not client_secret:
        click.echo(
            "Error: LinkedIn credentials not found.\n"
            "Run `linkedin-publisher configure` to store them in the system keyring.",
            err=True,
        )
        sys.exit(1)
    return LinkedInClient(client_id, client_secret, redirect_uri)


@click.group()
def main() -> None:
    """Publish Hugo blog posts to LinkedIn with a mandatory review step."""


@main.command()
def configure() -> None:
    """Save LinkedIn app credentials to the system keyring (run once after creating your app)."""
    client_id = click.prompt("LinkedIn Client ID")
    client_secret = click.prompt("LinkedIn Client Secret", hide_input=True)
    keyring.set_password(_KEYRING_SERVICE, "client_id", client_id)
    keyring.set_password(_KEYRING_SERVICE, "client_secret", client_secret)
    click.echo("Credentials saved to the system keyring.")


@main.command()
def auth() -> None:
    """Authenticate with LinkedIn via OAuth and save tokens to .tokens.json."""
    client = _client()
    try:
        client.authenticate()
        click.echo("Authentication successful. You can now use `list` and `publish`.")
    except LinkedInAuthError as exc:
        click.echo(f"Authentication failed: {exc}", err=True)
        sys.exit(1)


@main.command(name="list")
def list_queued() -> None:
    """List all blog posts with linkedin_queue: true that have not been posted."""
    scanner = ContentScanner(_content_dir())
    posts = scanner.scan_queued()
    if not posts:
        click.echo("No posts are currently queued for LinkedIn.")
        return
    click.echo(f"{'Slug':<45} {'Date':<14} Title")
    click.echo("-" * 90)
    for post in posts:
        click.echo(f"{post.slug:<45} {post.date.strftime('%d %b %Y'):<14} {post.title}")


@main.command()
@click.argument("slug")
def review(slug: str) -> None:
    """Preview a queued post — shows title, URL, description, and content excerpt."""
    scanner = ContentScanner(_content_dir())
    post = scanner.get_post(slug)
    if post is None:
        click.echo(f"Error: post '{slug}' not found.", err=True)
        sys.exit(1)
    if not post.linkedin_queue:
        click.echo(f"Warning: '{slug}' does not have linkedin_queue: true.")
    if post.linkedin_posted:
        click.echo(f"Note: '{slug}' has already been posted to LinkedIn.")
    click.echo("\n" + "=" * 60)
    click.echo(post.linkedin_preview)
    click.echo("=" * 60 + "\n")


@main.command()
@click.argument("slug")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt.")
def publish(slug: str, yes: bool) -> None:
    """Publish a queued post to LinkedIn after manual review and confirmation."""
    scanner = ContentScanner(_content_dir())
    post = scanner.get_post(slug)
    if post is None:
        click.echo(f"Error: post '{slug}' not found.", err=True)
        sys.exit(1)
    if post.linkedin_posted:
        click.echo(f"Error: '{slug}' has already been posted to LinkedIn.", err=True)
        sys.exit(1)
    if not post.linkedin_queue:
        click.echo(
            f"Error: '{slug}' does not have linkedin_queue: true. "
            "Set it in the post's front matter first.",
            err=True,
        )
        sys.exit(1)
    click.echo("\n" + "=" * 60)
    click.echo(post.linkedin_preview)
    click.echo("=" * 60 + "\n")
    if not yes and not click.confirm("Publish this post to LinkedIn?"):
        click.echo("Cancelled.")
        return

    client = _client()
    if not client.load_tokens():
        click.echo("Error: no saved tokens. Run `linkedin-publisher auth` first.", err=True)
        sys.exit(1)

    try:
        post_id = client.create_post(
            text=_build_post_text(post.title, post.description, post.site_url),
            article_url=post.site_url,
        )
        scanner.mark_posted(slug)
        click.echo(f"Published successfully. LinkedIn post ID: {post_id}")
    except LinkedInAuthError as exc:
        click.echo(f"Auth error: {exc}", err=True)
        sys.exit(1)


def _build_post_text(title: str, description: str, url: str) -> str:
    """Compose the LinkedIn post body from a post's metadata."""
    parts = [title]
    if description:
        parts.append(f"\n{description}")
    parts.append(f"\nRead more: {url}")
    return "\n".join(parts)
