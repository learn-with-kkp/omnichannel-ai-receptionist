"""
Twitter / X Direct Message & Account Activity API Integration.
Handles:
- CRC Challenge Verification (HMAC-SHA256 signature)
- Incoming DM webhook event parsing
- Direct Message dispatching via Twitter API v2
"""

import os
import hmac
import hashlib
import base64
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("TwitterIntegration")


class TwitterClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        bearer_token: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("TWITTER_API_KEY", "")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET", "")
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN", "")

    def is_configured(self) -> bool:
        return bool(self.bearer_token and not self.bearer_token.startswith("your_"))

    def compute_crc_response(self, crc_token: str) -> str:
        """
        Creates HMAC-SHA256 hash using the Twitter API consumer secret.
        Required for the Twitter Webhook CRC Challenge:
        https://developer.x.com/en/docs/x-api/enterprise/account-activity-api/guides/securing-webhooks
        """
        secret_bytes = self.api_secret.encode("utf-8")
        token_bytes = crc_token.encode("utf-8")
        sha256_hash = hmac.new(secret_bytes, token_bytes, hashlib.sha256).digest()
        return "sha256=" + base64.b64encode(sha256_hash).decode("utf-8")

    def send_direct_message(
        self,
        recipient_id: str,
        text: str,
        quick_replies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Dispatches a direct message to a user on X / Twitter."""
        clean_recipient = str(recipient_id).strip()

        payload: Dict[str, Any] = {
            "conversation_type": "one_to_one",
            "participant_id": clean_recipient,
            "body": text
        }
        if quick_replies:
            payload["quick_reply_options"] = [
                {"label": opt[:20], "metadata": opt} for opt in quick_replies[:5]
            ]

        if self.is_configured():
            try:
                url = f"https://api.twitter.com/2/dm_conversations/with/{clean_recipient}/messages"
                data = json.dumps({"text": text}).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        "Authorization": f"Bearer {self.bearer_token}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ Twitter DM dispatched to {clean_recipient}")
                    return {"status": "sent", "channel": "twitter", "response": resp_data}
            except Exception as e:
                logger.error(f"Twitter API dispatch failed: {e}")

        logger.info(f"🐦 [SIMULATION TWITTER / X] To: @{clean_recipient} | Body: {text}")
        return {
            "status": "simulated",
            "channel": "twitter",
            "recipient_id": clean_recipient,
            "text": text,
            "quick_replies": quick_replies or []
        }

    @staticmethod
    def parse_incoming_dm(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parses Twitter Account Activity API webhook payload."""
        events = data.get("direct_message_events", [])
        if events:
            event = events[0]
            msg_data = event.get("message_create", {})
            sender_id = msg_data.get("sender_id", "")
            text = msg_data.get("message_data", {}).get("text", "")
            return {"sender_id": sender_id, "text": text}
        return None


twitter_client = TwitterClient()

