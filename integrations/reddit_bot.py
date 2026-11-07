"""
Reddit API & Bot Integration.
Handles:
- OAuth2 token authentication (script/web application flow)
- Direct private messaging (/api/compose)
- Subreddit comment replies (/api/comment)
- Unread message polling & parsing (/message/unread)
"""

import os
import time
import base64
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("RedditIntegration")


class RedditClient:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET", "")
        self.username = username or os.getenv("REDDIT_USERNAME", "")
        self.password = password or os.getenv("REDDIT_PASSWORD", "")
        self.user_agent = user_agent or os.getenv("REDDIT_USER_AGENT", "OmniReceptionistBot/1.0.0 by /u/AIEngineer")

        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def is_configured(self) -> bool:
        return bool(
            self.client_id
            and not self.client_id.startswith("your_")
            and self.client_secret
            and not self.client_secret.startswith("your_")
        )

    def get_access_token(self) -> Optional[str]:
        """Obtains or refreshes OAuth2 token via Reddit password/script grant."""
        if not self.is_configured():
            return None

        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        try:
            auth_str = f"{self.client_id}:{self.client_secret}"
            auth_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

            if self.username and self.password and not self.password.startswith("your_"):
                data = urllib.parse.urlencode({
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password
                }).encode("utf-8")
            else:
                data = urllib.parse.urlencode({
                    "grant_type": "client_credentials"
                }).encode("utf-8")

            req = urllib.request.Request(
                "https://www.reddit.com/api/v1/access_token",
                data=data,
                headers={
                    "Authorization": f"Basic {auth_b64}",
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode())
                self._access_token = res_data.get("access_token")
                expires_in = res_data.get("expires_in", 3600)
                self._token_expires_at = time.time() + float(expires_in)
                return self._access_token
        except Exception as e:
            logger.error(f"Failed to authenticate with Reddit OAuth: {e}")
            return None

    def send_private_message(
        self,
        recipient_username: str,
        subject: str,
        text: str
    ) -> Dict[str, Any]:
        """Sends a private message to a Reddit user."""
        token = self.get_access_token()
        clean_user = recipient_username.lstrip("u/").strip()

        if not token:
            logger.info(f"[SIMULATION] Reddit PM to u/{clean_user} | Subject: '{subject}': {text}")
            return {
                "status": "simulated",
                "message_id": f"rd_sim_{os.urandom(4).hex()}",
                "recipient": clean_user,
                "text": text,
                "channel": "reddit"
            }

        try:
            payload = urllib.parse.urlencode({
                "to": clean_user,
                "subject": subject or "Appointment Confirmation",
                "text": text,
                "api_type": "json"
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://oauth.reddit.com/api/compose",
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                return {
                    "status": "sent",
                    "channel": "reddit",
                    "recipient": clean_user,
                    "reddit_response": result
                }
        except Exception as e:
            logger.error(f"Failed to send Reddit PM to u/{clean_user}: {e}")
            return {"status": "failed", "error": str(e), "channel": "reddit"}

    def reply_to_comment(
        self,
        thing_id: str,
        text: str
    ) -> Dict[str, Any]:
        """Replies to a comment or submission (parent thing ID e.g. t1_xyz or t3_xyz)."""
        token = self.get_access_token()
        if not token:
            logger.info(f"[SIMULATION] Reddit Comment Reply to {thing_id}: {text}")
            return {
                "status": "simulated",
                "comment_id": f"rd_cmt_{os.urandom(4).hex()}",
                "parent_id": thing_id,
                "text": text,
                "channel": "reddit"
            }

        try:
            payload = urllib.parse.urlencode({
                "thing_id": thing_id,
                "text": text,
                "api_type": "json"
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://oauth.reddit.com/api/comment",
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                return {
                    "status": "sent",
                    "channel": "reddit",
                    "parent_id": thing_id,
                    "reddit_response": result
                }
        except Exception as e:
            logger.error(f"Failed to reply to Reddit comment {thing_id}: {e}")
            return {"status": "failed", "error": str(e), "channel": "reddit"}

    def get_unread_messages(self, mark_read: bool = True) -> List[Dict[str, Any]]:
        """Polls unread messages from Reddit inbox."""
        token = self.get_access_token()
        if not token:
            return []

        try:
            req = urllib.request.Request(
                "https://oauth.reddit.com/message/unread?mark=" + ("true" if mark_read else "false"),
                headers={
                    "Authorization": f"Bearer {token}",
                    "User-Agent": self.user_agent
                },
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                items = data.get("data", {}).get("children", [])
                messages = []
                for item in items:
                    msg_data = item.get("data", {})
                    messages.append({
                        "name": msg_data.get("name"),
                        "author": msg_data.get("author"),
                        "subject": msg_data.get("subject"),
                        "body": msg_data.get("body"),
                        "created_utc": msg_data.get("created_utc")
                    })
                return messages
        except Exception as e:
            logger.error(f"Failed to fetch Reddit unread messages: {e}")
            return []


reddit_client = RedditClient()

