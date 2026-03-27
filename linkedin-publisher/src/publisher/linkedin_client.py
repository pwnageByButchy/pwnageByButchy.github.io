"""
LinkedIn API client — OAuth 2.0 authentication and post creation.

Author: Steve Bartimote
© Steve Bartimote. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import secrets
import threading
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import requests
logger = logging.getLogger(__name__)

_AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
_API_BASE = "https://api.linkedin.com"
_SCOPES = ["w_member_social", "openid", "profile"]
_TOKENS_FILE = Path(__file__).parent.parent.parent / ".tokens.json"  # gitignored


class LinkedInError(Exception):
    """Base exception for all LinkedIn client errors."""
    # Use the more specific subclasses: LinkedInAuthError or LinkedInAPIError.


class LinkedInAuthError(LinkedInError):
    """Raised when OAuth authentication fails or no valid token exists."""
    # Run `linkedin-publisher auth` to obtain a fresh access token.


class LinkedInAPIError(LinkedInError):
    """Raised when a LinkedIn API call returns an error HTTP response."""
    # Inspect the exception message for the HTTP status code and body.


class LinkedInClient:
    """Handles OAuth authentication and post creation via the LinkedIn API."""
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        """Initialise the client with OAuth app credentials."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._tokens: dict = {}
        self._person_urn: str | None = None

    def authenticate(self) -> None:
        """Run the OAuth 2.0 authorisation code flow to obtain tokens.

        Opens a browser for the user to authorise the app, then exchanges
        the code for access and refresh tokens saved to .tokens.json.
        """
        state = secrets.token_urlsafe(16)
        auth_url = (
            f"{_AUTHORIZE_URL}?"
            + urlencode({
                "response_type": "code",
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "scope": " ".join(_SCOPES),
                "state": state,
            })
        )
        code = self._run_local_callback_server(auth_url, state)
        self._exchange_code(code)
        logger.info("Authentication successful — tokens saved to %s", _TOKENS_FILE)

    def load_tokens(self) -> bool:
        """Load saved tokens from disk. Returns True if a valid access token exists."""
        if not _TOKENS_FILE.exists():
            return False
        try:
            self._tokens = json.loads(_TOKENS_FILE.read_text())
            return bool(self._tokens.get("access_token"))
        except (json.JSONDecodeError, OSError):
            return False

    def create_post(self, text: str, article_url: str | None = None) -> str:
        """Publish a post to LinkedIn via the UGC Posts API and return the post URN.

        Uses /v2/ugcPosts which is available to individual developers with
        the w_member_social scope and requires no versioning header.
        Raises LinkedInAuthError if no valid token is available.
        Raises LinkedInAPIError if the API returns an error response.
        """
        self._ensure_valid_token()
        author_urn = self._get_person_urn()
        share_content: dict = {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "NONE",
        }
        if article_url:
            share_content["shareMediaCategory"] = "ARTICLE"
            share_content["media"] = [{"status": "READY", "originalUrl": article_url}]
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {"com.linkedin.ugc.ShareContent": share_content},
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        response = self._post("/v2/ugcPosts", payload)
        post_id = response.json().get("id", "")
        logger.info("Post created: %s", post_id)
        return post_id

    def _ensure_valid_token(self) -> None:
        """Refresh the access token if it is expired or within 5 minutes of expiry."""
        if not self._tokens.get("access_token"):
            raise LinkedInAuthError("No access token — run `linkedin-publisher auth` first.")
        expiry_str = self._tokens.get("expires_at")
        if expiry_str:
            expiry = datetime.fromisoformat(expiry_str)
            if datetime.now(timezone.utc) >= expiry - timedelta(minutes=5):
                self._refresh_token()

    def _refresh_token(self) -> None:
        """Exchange the saved refresh token for a new access token."""
        refresh_token = self._tokens.get("refresh_token")
        if not refresh_token:
            raise LinkedInAuthError("No refresh token available — run `linkedin-publisher auth` again.")
        response = requests.post(
            _TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=30,
        )
        self._handle_token_response(response)

    def _exchange_code(self, code: str) -> None:
        """Exchange an authorisation code for access and refresh tokens."""
        response = requests.post(
            _TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self._redirect_uri,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=30,
        )
        self._handle_token_response(response)

    def _handle_token_response(self, response: requests.Response) -> None:
        """Parse a token endpoint response and persist the tokens to disk."""
        if response.status_code != 200:
            raise LinkedInAuthError(
                f"Token request failed ({response.status_code}): {response.text}"
            )
        data = response.json()
        expires_in = data.get("expires_in", 3600)
        self._tokens = {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", ""),
            "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(),
        }
        _TOKENS_FILE.write_text(json.dumps(self._tokens, indent=2))

    def _get_person_urn(self) -> str:
        """Return the authenticated user's LinkedIn URN, fetching it on first call."""
        if self._person_urn:
            return self._person_urn
        data = self._get("/v2/userinfo").json()
        sub = data.get("sub")
        if not sub:
            raise LinkedInAPIError("Could not retrieve LinkedIn user ID from /v2/userinfo")
        self._person_urn = f"urn:li:person:{sub}"
        return self._person_urn

    def _get(self, path: str) -> requests.Response:
        """Perform an authenticated GET request against the LinkedIn API."""
        response = requests.get(
            f"{_API_BASE}{path}",
            headers={"Authorization": f"Bearer {self._tokens['access_token']}"},
            timeout=30,
        )
        if not response.ok:
            raise LinkedInAPIError(f"GET {path} failed ({response.status_code}): {response.text}")
        return response

    def _post(self, path: str, payload: dict, api_version: str | None = None) -> requests.Response:
        """Perform an authenticated POST request against the LinkedIn API."""
        headers: dict = {
            "Authorization": f"Bearer {self._tokens['access_token']}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        if api_version:
            headers["LinkedIn-Version"] = api_version
        response = requests.post(
            f"{_API_BASE}{path}",
            json=payload,
            headers=headers,
            timeout=30,
        )
        if not response.ok:
            raise LinkedInAPIError(f"POST {path} failed ({response.status_code}): {response.text}")
        return response

    def _run_local_callback_server(self, auth_url: str, expected_state: str) -> str:
        """Attempt to capture the OAuth callback via a local HTTP server.

        Falls back to manual code entry if the local server cannot be reached
        (e.g. Wayland/sandbox environments where the browser cannot connect to
        localhost). Returns the authorisation code string.
        """
        code_holder: dict = {}

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                params = parse_qs(urlparse(self.path).query)
                if params.get("state", [""])[0] == expected_state:
                    code_holder["code"] = params.get("code", [""])[0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Authorisation complete \xe2\x80\x94 you may close this tab.")

            def log_message(self, *args: object) -> None:
                pass

        port = int(urlparse(self._redirect_uri).port or 8080)
        server = HTTPServer(("127.0.0.1", port), _Handler)
        server.timeout = 60

        thread = threading.Thread(target=server.handle_request, daemon=True)
        thread.start()

        print(f"\n1. Open this URL in your browser:\n\n   {auth_url}\n")
        print("2. Approve the LinkedIn authorisation request.")
        print("3. Your browser will redirect to localhost:8080 — it may show an error.")
        print("   If it connects automatically, you're done.")
        print("   If not, copy the full redirect URL from the address bar and paste it below.\n")
        webbrowser.open(auth_url)

        thread.join(timeout=70)
        server.server_close()

        if code_holder.get("code"):
            return code_holder["code"]
        redirect_url = input("Paste the full redirect URL here (or press Enter to cancel): ").strip()
        if not redirect_url:
            raise LinkedInAuthError("Authentication cancelled.")
        return self._parse_redirect_code(redirect_url, expected_state)

    def _parse_redirect_code(self, redirect_url: str, expected_state: str) -> str:
        """Extract and validate the auth code from a manually pasted redirect URL."""
        params = parse_qs(urlparse(redirect_url).query)
        if params.get("state", [""])[0] != expected_state:
            raise LinkedInAuthError("State mismatch — possible CSRF. Please re-run auth.")
        code = params.get("code", [""])[0]
        if not code:
            raise LinkedInAuthError("No authorisation code found in the pasted URL.")
        return code
