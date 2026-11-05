"""
Meta Threads API Integration.
Handles:
- Webhook Hub Challenge Verification
- Incoming Threads webhook mention/reply parsing
- Thread creation and replies via Meta Threads Graph API v1.0 (https://graph.threads.net/v1.0)
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("ThreadsIntegration")


class ThreadsClient:
    def __init__(
        self,
        user_id: Optional[str] = None,
        access_token: Optional[str] = None,
        verify_token: Optional[str] = None
    ):
        self.user_id = user_id or os.getenv("THREADS_USER_ID", "")
        self.access_token = access_token or os.getenv("THREADS_ACCESS_TOKEN", "")
        self.verify_token = verify_token or os.getenv("THREADS_VERIFY_TOKEN", os.getenv("META_VERIFY_TOKEN", "omnichannel_threads_token_123"))
        self.api_base = "https://graph.threads.net/v1.0"

    def is_configured(self) -> bool:
        return bool(
            self.access_token
            and not self.access_token.startswith("your_")
            and self.user_id
            and not self.user_id.startswith("your_")
        )

    def verify_webhook(self, mode: Optional[str], token: Optional[str], challenge: Optional[str]) -> Optional[str]:
        """Verifies Meta Webhook challenge for Threads subscription."""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Meta Threads webhook verified successfully.")
            return challenge
        logger.warning("Meta Threads webhook challenge rejected due to token mismatch.")
        return None

    def send_reply(
        self,
        reply_to_id: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Publishes a reply to an existing Threads post.
        Threads publishing is a 2-step process:
        Step 1: POST /{threads-user-id}/threads?media_type=TEXT&text=...&reply_to_id=...
        Step 2: POST /{threads-user-id}/threads_publish?creation_id=...
        """
        if not self.is_configured():
            logger.info(f"[SIMULATION] Threads reply to '{reply_to_id}': {text}")
            return {
                "status": "simulated",
                "threads_id": f"th_sim_{os.urandom(4).hex()}",
                "reply_to_id": reply_to_id,
                "text": text,
                "channel": "threads"
            }

        try:
            # Step 1: Create Container
            create_url = f"{self.api_base}/{self.user_id}/threads"
            create_payload = urllib.parse.urlencode({
                "media_type": "TEXT",
                "text": text,
                "reply_to_id": reply_to_id,
                "access_token": self.access_token
            }).encode("utf-8")

            req = urllib.request.Request(
                create_url,
                data=create_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                create_res = json.loads(response.read().decode())
                container_id = create_res.get("id")

            if not container_id:
                return {"status": "error", "error": "No creation_id returned from Threads API"}

            # Step 2: Publish Container
            publish_url = f"{self.api_base}/{self.user_id}/threads_publish"
            publish_payload = urllib.parse.urlencode({
                "creation_id": container_id,
                "access_token": self.access_token
            }).encode("utf-8")

            pub_req = urllib.request.Request(
                publish_url,
                data=publish_payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST"
            )
            with urllib.request.urlopen(pub_req, timeout=10) as pub_response:
                pub_res = json.loads(pub_response.read().decode())
                return {
                    "status": "sent",
                    "threads_id": pub_res.get("id"),
                    "container_id": container_id,
                    "channel": "threads"
                }

        except Exception as e:
            logger.error(f"Threads API call failed: {e}")
            return {"status": "failed", "error": str(e), "channel": "threads"}

    def parse_incoming_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parses an incoming webhook from Meta Graph API for Threads."""
        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            val = changes.get("value", {})
            post_id = val.get("id")
            text = val.get("text", "")
            from_user = val.get("from", {})
            user_id = from_user.get("id", val.get("sender_id", "unknown_user"))
            user_name = from_user.get("username", "Threads User")

            if not post_id or not text:
                return None

            return {
                "post_id": post_id,
                "user_id": user_id,
                "username": user_name,
                "text": text
            }
        except Exception as e:
            logger.warning(f"Failed to parse Threads webhook payload: {e}")
            return None


threads_client = ThreadsClient()
