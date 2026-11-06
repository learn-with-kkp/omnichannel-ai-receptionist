"""
Customer Authentication & Account Management Router.
Provides:
- Customer Signup (/api/auth/signup) with automatic Tenant creation
- Customer Login (/api/auth/login)
- Account Profile & Plan Status (/api/auth/me)
- Subscription Tier Upgrades (/api/auth/change-plan)
"""

import secrets
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel

from backend.database import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password,
    update_tenant_plan,
    get_tenant_integrations,
    save_tenant_integrations
)
from core.blueprint.tenant_manager import tenant_registry

logger = logging.getLogger("AuthRouter")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# In-memory session store mapping token -> user_id
ACTIVE_SESSIONS: Dict[str, str] = {}


class SignupRequest(BaseModel):
    email: str
    password: str
    company_name: str
    vertical: Optional[str] = "salon"
    phone_number: Optional[str] = "+18005550199"
    plan: Optional[str] = "growth"


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePlanRequest(BaseModel):
    tenant_id: str
    plan: str


class UpdateIntegrationsRequest(BaseModel):
    tenant_id: str
    whatsapp_phone_number_id: Optional[str] = ""
    whatsapp_business_account_id: Optional[str] = ""
    meta_page_id: Optional[str] = ""
    instagram_account_id: Optional[str] = ""
    google_calendar_id: Optional[str] = "primary"
    telegram_bot_token: Optional[str] = ""
    telegram_chat_id: Optional[str] = ""
    twitter_api_key: Optional[str] = ""
    twitter_bearer_token: Optional[str] = ""
    linkedin_client_id: Optional[str] = ""
    linkedin_access_token: Optional[str] = ""
    tiktok_client_key: Optional[str] = ""
    tiktok_access_token: Optional[str] = ""


def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    user_id = ACTIVE_SESSIONS.get(token)
    if user_id:
        return get_user_by_id(user_id)
    return None


@router.post("/signup")
@router.post("/register")
def customer_signup(payload: SignupRequest):
    """
    Registers a new business customer, creates their tenant workspace,
    and returns an authenticated session.
    """
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")

    existing = get_user_by_email(str(payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    # Generate clean tenant ID
    clean_tenant_id = payload.company_name.lower().replace(" ", "_").replace("&", "and")
    clean_tenant_id = "".join(c for c in clean_tenant_id if c.isalnum() or c == "_")[:32]
    if not clean_tenant_id:
        clean_tenant_id = f"tenant_{secrets.token_hex(4)}"

    # Auto-provision tenant manifest
    tenant = tenant_registry.onboard_custom_tenant(
        tenant_id=clean_tenant_id,
        business_name=payload.company_name,
        vertical=payload.vertical or "salon",
        phone_number=payload.phone_number or "+18005550199",
        address="Commercial Center",
        primary_accent="general_american"
    )

    # Create user
    user = create_user(
        email=str(payload.email),
        password=payload.password,
        company_name=payload.company_name,
        tenant_id=clean_tenant_id,
        plan=payload.plan or "growth"
    )

    # Issue session token
    token = f"tok_{secrets.token_hex(16)}"
    ACTIVE_SESSIONS[token] = user["id"]

    return {
        "status": "success",
        "message": f"Account created for {payload.company_name}!",
        "token": token,
        "tenant_id": clean_tenant_id,
        "user": user,
        "tenant": tenant.model_dump()
    }


@router.post("/login")
def customer_login(payload: LoginRequest):
    """Authenticates existing business customer."""
    user = get_user_by_email(str(payload.email))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = f"tok_{secrets.token_hex(16)}"
    ACTIVE_SESSIONS[token] = user["id"]

    tenant = tenant_registry.get_tenant(user["tenant_id"])
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}

    return {
        "status": "success",
        "message": "Welcome back!",
        "token": token,
        "user": safe_user,
        "tenant": tenant.model_dump()
    }


@router.get("/me")
def get_current_user_profile(user: Optional[Dict[str, Any]] = Depends(get_current_user_from_token)):
    """Retrieves authenticated customer profile and connected omnichannel channels."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required.")

    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    tenant_id = user.get("tenant_id", "salon")
    tenant = tenant_registry.get_tenant(tenant_id)
    return {
        "authenticated": True,
        "user": safe_user,
        "tenant": tenant.model_dump() if tenant else {},
        "integrations": get_tenant_integrations(tenant_id)
    }


@router.post("/change-plan")
def update_subscription_plan(payload: ChangePlanRequest):
    """Changes customer subscription tier: starter ($99/mo), growth ($249/mo), enterprise ($599/mo)."""
    valid_plans = {
        "starter": "$99/mo",
        "growth": "$249/mo",
        "enterprise": "$599/mo"
    }
    plan_key = payload.plan.lower()
    if plan_key not in valid_plans:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Must be one of {list(valid_plans.keys())}")

    updated = update_tenant_plan(payload.tenant_id, plan_key)
    return {
        "status": "success",
        "tenant_id": payload.tenant_id,
        "plan": plan_key,
        "monthly_fee": valid_plans[plan_key],
        "updated": updated
    }


@router.post("/integrations")
def update_tenant_integrations_endpoint(payload: UpdateIntegrationsRequest):
    """Updates connected omnichannel social accounts for a tenant."""
    saved = save_tenant_integrations(
        tenant_id=payload.tenant_id,
        whatsapp_phone_number_id=payload.whatsapp_phone_number_id or "",
        whatsapp_business_account_id=payload.whatsapp_business_account_id or "",
        meta_page_id=payload.meta_page_id or "",
        instagram_account_id=payload.instagram_account_id or "",
        google_calendar_id=payload.google_calendar_id or "primary",
        telegram_bot_token=payload.telegram_bot_token or "",
        telegram_chat_id=payload.telegram_chat_id or "",
        twitter_api_key=payload.twitter_api_key or "",
        twitter_bearer_token=payload.twitter_bearer_token or "",
        linkedin_client_id=payload.linkedin_client_id or "",
        linkedin_access_token=payload.linkedin_access_token or "",
        tiktok_client_key=payload.tiktok_client_key or "",
        tiktok_access_token=payload.tiktok_access_token or ""
    )
    return {"status": "success", "integrations": saved}
