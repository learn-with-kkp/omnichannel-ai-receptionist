"""
LinkedIn Messaging API Integration.
Handles:
- Direct messaging & InMail automation
- Webhook subscription handling
- Resilient message dispatching via https://api.linkedin.com/v2/messages
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse

logger = logging.getLogger("LinkedInIntegration")


class LinkedInClient:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN", "")

    def is_configured(self) -> bool:
        return bool(self.access_token and not self.access_token.startswith("your_"))

    def send_message(
        self,
        recipient_urn: str,
        text: str
    ) -> Dict[str, Any]:
        """Dispatches direct message via LinkedIn Messaging API."""
        clean_urn = str(recipient_urn).strip()
        if not clean_urn.startswith("urn:li:"):
            clean_urn = f"urn:li:person:{clean_urn}"

        if self.is_configured():
            try:
                url = "https://api.linkedin.com/v2/messages"
                payload = {
                    "recipients": [clean_urn],
                    "messageContent": {"body": text}
                }
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    resp_data = json.loads(resp.read().decode())
                    logger.info(f"✅ LinkedIn message sent to {clean_urn}")
                    return {"status": "sent", "channel": "linkedin", "response": resp_data}
            except Exception as e:
                logger.error(f"LinkedIn Messaging API failed: {e}")

        logger.info(f"💼 [SIMULATION LINKEDIN] To: {clean_urn} | Body: {text}")
        return {
            "status": "simulated",
            "channel": "linkedin",
            "recipient_urn": clean_urn,
            "text": text
        }

    @staticmethod
    def parse_incoming_message(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parses LinkedIn Webhook event."""
        # Handles standard LinkedIn webhook or simulated JSON
        sender = data.get("senderUrn") or data.get("sender", {}).get("id") or data.get("from", "")
        text = data.get("body") or data.get("message", {}).get("text") or data.get("text", "")
        if sender and text:
            return {"sender": str(sender), "text": str(text)}
        return None


linkedin_client = LinkedInClient()

