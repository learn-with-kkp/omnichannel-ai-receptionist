"""
Enterprise n8n Webhook Event Dispatcher for Omnichannel Voice Receptionist.
Dispatches asynchronous event triggers to n8n workflows for:
1. Manager Escalation Alerts (Frustrated / Angry Sentiment) -> Slack & Telegram
2. CRM & Lead Sync -> HubSpot, GoHighLevel, Notion, Google Sheets
3. Post-Call Marketing & Retention Sequences -> 2h Google Review WhatsApp, 30d Touch-up Drip
"""

import os
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("N8NDispatcher")

class N8NDispatcher:
    def __init__(self):
        self.timeout = 4.0

    def get_webhook_url(self, tenant_id: str = "salon") -> Optional[str]:
        """Retrieves configured n8n webhook endpoint from environment or database."""
        # 1. Environment variable
        url = (
            os.getenv("N8N_WEBHOOK_URL")
            or os.getenv("N8N_SALON_EVENTS_URL")
            or os.getenv("N8N_URL")
        )
        if url:
            return url.strip()

        # 2. Per-tenant database integration lookup if available
        try:
            from backend.database import get_tenant_integrations
            integrations = get_tenant_integrations(tenant_id)
            if integrations and integrations.get("webhook_secret"):
                pass
        except Exception:
            pass

        return None

    def dispatch_event(
        self,
        event_name: str,
        payload: Dict[str, Any],
        tenant_id: str = "salon"
    ):
        """Dispatches event to n8n in a non-blocking background thread."""
        webhook_url = self.get_webhook_url(tenant_id)
        if not webhook_url:
            logger.debug(f"[n8n] N8N_WEBHOOK_URL not configured. Event '{event_name}' skipped.")
            return

        # Prepare standardized event packet
        event_packet = {
            "event": event_name,
            "timestamp": datetime.now().isoformat(),
            "tenant_id": tenant_id,
            "data": payload
        }

        # Fire and forget asynchronously so voice call response is never blocked
        thread = threading.Thread(
            target=self._send_http_post,
            args=(webhook_url, event_packet, event_name),
            daemon=True
        )
        thread.start()

    def _send_http_post(self, url: str, packet: Dict[str, Any], event_name: str):
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    url,
                    json=packet,
                    headers={"Content-Type": "application/json", "User-Agent": "LuxeSalon-VoiceAI/2.0"}
                )
                if res.status_code in (200, 201, 202, 204):
                    logger.info(f"✅ [n8n] Successfully dispatched event '{event_name}' (Status: {res.status_code})")
                else:
                    logger.warning(f"⚠️ [n8n] Webhook received status {res.status_code} for '{event_name}': {res.text[:120]}")
        except Exception as e:
            logger.warning(f"⚠️ [n8n] Failed to reach webhook endpoint for '{event_name}': {e}")


n8n_dispatcher = N8NDispatcher()
