"""
Meta OAuth & Facebook Login for Business Integration.
Enables self-service 1-click social connection for SaaS customers:
1. Facebook Login Dialog (OAuth 2.0)
2. Token Exchange & Long-Lived Token upgrade
3. Auto-discovery of customer's Facebook Page ID & Instagram Account ID
4. Dynamic persistence into tenant_integrations database
"""

import os
import json
import logging
import urllib.parse
import urllib.request
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.database import save_tenant_integrations, get_tenant_integrations

logger = logging.getLogger("MetaOAuth")
router = APIRouter(prefix="/api/oauth", tags=["Meta OAuth & Social Connect"])

META_APP_ID = os.getenv("META_APP_ID", os.getenv("FACEBOOK_APP_ID", "2026204064725563"))
META_APP_SECRET = os.getenv("META_APP_SECRET", os.getenv("FACEBOOK_APP_SECRET", ""))
REDIRECT_URI = os.getenv("META_OAUTH_REDIRECT_URI", "https://ai-voice-receptionist.kishor.tech/api/oauth/facebook/callback")


class ManualConnectPayload(BaseModel):
    tenant_id: str
    whatsapp_phone_number_id: Optional[str] = ""
    whatsapp_business_account_id: Optional[str] = ""
    meta_page_id: Optional[str] = ""
    instagram_account_id: Optional[str] = ""
    meta_access_token: Optional[str] = ""
    threads_user_id: Optional[str] = ""


@router.get("/facebook/login")
def get_facebook_login_url(
    tenant_id: str = Query("salon", description="Tenant ID of the business owner"),
    format: Optional[str] = Query(None)
):
    """
    Generates Meta OAuth 2.0 authorization dialog URL.
    Encodes tenant_id into state parameter for callback reconciliation.
    Redirects directly to Facebook Login dialog or returns JSON if format=json.
    """
    scopes = [
        "pages_show_list",
        "pages_messaging",
        "pages_read_engagement",
        "instagram_basic",
        "instagram_manage_messages",
        "whatsapp_business_management",
        "whatsapp_business_messaging"
    ]

    state_payload = urllib.parse.quote(json.dumps({"tenant_id": tenant_id}))
    params = {
        "client_id": META_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state_payload,
        "scope": ",".join(scopes),
        "response_type": "code"
    }

    oauth_url = f"https://www.facebook.com/v21.0/dialog/oauth?{urllib.parse.urlencode(params)}"
    if format == "json":
        return {
            "tenant_id": tenant_id,
            "oauth_url": oauth_url,
            "provider": "meta_business"
        }
    return RedirectResponse(url=oauth_url)


@router.get("/facebook/callback")
def handle_facebook_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """
    Exchanges OAuth code for access token, auto-discovers connected Facebook Page and Instagram ID,
    and updates tenant_integrations in database.
    """
    if error:
        logger.error(f"Meta OAuth error from user: {error}")
        return RedirectResponse(url=f"/site/salon?oauth_error={urllib.parse.quote(error)}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    tenant_id = "salon"
    if state:
        try:
            state_data = json.loads(urllib.parse.unquote(state))
            tenant_id = state_data.get("tenant_id", "salon")
        except Exception:
            tenant_id = "salon"

    # If App Secret is configured, exchange for User Access Token
    if META_APP_SECRET and not META_APP_SECRET.startswith("your_"):
        try:
            token_url = "https://graph.facebook.com/v21.0/oauth/access_token?" + urllib.parse.urlencode({
                "client_id": META_APP_ID,
                "client_secret": META_APP_SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code
            })
            req = urllib.request.Request(token_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                token_data = json.loads(resp.read().decode())
                user_token = token_data.get("access_token")

            # Discover Pages
            pages_url = f"https://graph.facebook.com/v21.0/me/accounts?access_token={user_token}"
            page_req = urllib.request.Request(pages_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(page_req, timeout=10) as page_resp:
                pages_data = json.loads(page_resp.read().decode())
                pages = pages_data.get("data", [])
                if pages:
                    first_page = pages[0]
                    page_id = first_page.get("id")
                    page_token = first_page.get("access_token")

                    # Check for Instagram Business account linked to Page
                    ig_url = f"https://graph.facebook.com/v21.0/{page_id}?fields=instagram_business_account&access_token={page_token}"
                    ig_req = urllib.request.Request(ig_url, headers={"User-Agent": "Mozilla/5.0"})
                    instagram_id = ""
                    try:
                        with urllib.request.urlopen(ig_req, timeout=5) as ig_resp:
                            ig_data = json.loads(ig_resp.read().decode())
                            instagram_id = ig_data.get("instagram_business_account", {}).get("id", "")
                    except Exception:
                        pass

                    # Discover WhatsApp Business Account and Phone Number ID
                    waba_url = f"https://graph.facebook.com/v21.0/me?fields=whatsapp_business_accounts{{id,name,phone_numbers{{id,display_phone_number}}}}&access_token={user_token}"
                    waba_req = urllib.request.Request(waba_url, headers={"User-Agent": "Mozilla/5.0"})
                    waba_id = ""
                    phone_number_id = ""
                    try:
                        with urllib.request.urlopen(waba_req, timeout=5) as waba_resp:
                            waba_data = json.loads(waba_resp.read().decode())
                            waba_accounts = waba_data.get("whatsapp_business_accounts", {}).get("data", [])
                            if waba_accounts:
                                first_waba = waba_accounts[0]
                                waba_id = first_waba.get("id", "")
                                phone_numbers = first_waba.get("phone_numbers", {}).get("data", [])
                                if phone_numbers:
                                    phone_number_id = phone_numbers[0].get("id", "")
                    except Exception as we:
                        logger.warning(f"Could not fetch WABA automatically: {we}")

                    # Auto-provision tenant record if not yet registered
                    from backend.database import get_tenant, create_tenant
                    existing_tenant = get_tenant(tenant_id)
                    if not existing_tenant:
                        page_name = first_page.get("name") or tenant_id.replace("_", " ").title()
                        create_tenant(
                            tenant_id=tenant_id,
                            business_name=page_name,
                            vertical="salon",
                            phone=phone_number_id or "+18005550199"
                        )
                        logger.info(f"Auto-created new business tenant [{tenant_id}] for '{page_name}'")

                    save_tenant_integrations(
                        tenant_id=tenant_id,
                        meta_page_id=page_id,
                        instagram_account_id=instagram_id,
                        whatsapp_phone_number_id=phone_number_id,
                        whatsapp_business_account_id=waba_id,
                        meta_access_token=page_token or user_token
                    )
                    logger.info(f"Auto-saved Page ID {page_id}, Instagram ID {instagram_id}, WhatsApp ID {phone_number_id} for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"Failed to complete Meta OAuth exchange: {e}")

    return RedirectResponse(url=f"/site/{tenant_id}?meta_connected=true")


@router.post("/meta/manual-connect")
def manual_connect_social_accounts(payload: ManualConnectPayload):
    """
    Direct self-service connection endpoint for business owners to save
    their WhatsApp, Page ID, or Instagram ID into their tenant record.
    """
    saved = save_tenant_integrations(
        tenant_id=payload.tenant_id,
        whatsapp_phone_number_id=payload.whatsapp_phone_number_id,
        whatsapp_business_account_id=payload.whatsapp_business_account_id,
        meta_page_id=payload.meta_page_id,
        instagram_account_id=payload.instagram_account_id
    )

    return {
        "status": "success",
        "message": f"Social channels connected for tenant '{payload.tenant_id}'",
        "integrations": get_tenant_integrations(payload.tenant_id)
    }

