from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import time
import os
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from backend.models import VapiWebhookPayload, VapiToolResponse, ToolResult
from backend.database import (
    init_db,
    check_slots_availability,
    book_new_appointment,
    lookup_by_phone,
    reschedule_existing_appointment,
    cancel_existing_appointment,
    get_tenant_by_inbound_phone,
    get_tenant,
    get_all_tenants,
    create_tenant,
    get_tenant_services,
    get_tenant_stylists,
    get_db_connection,
    list_all_appointments,
    get_excel_path,
    save_call_log,
    get_call_log,
    list_call_logs,
    get_call_analytics
)
from core.tools_catalog import CATEGORIZED_TOOLS_CATALOG
from core.notifications import notification_dispatcher
from backend.reminder_service import run_reminder_cycle

from backend.routers.voice import router as voice_router
from backend.routers.chat import router as chat_router
from backend.routers.messaging import router as messaging_router
from backend.routers.tenants import router as tenants_router
from backend.routers.streaming_voice import router as streaming_voice_router
from backend.routers.auth import router as auth_router
from backend.routers.testing_suite import router as testing_suite_router
from backend.routers.knowledge import router as knowledge_router
from backend.routers.oauth import router as oauth_router
from backend.routers.calendar_routes import router as calendar_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SalonVoiceReceptionist")

def is_serverless_runtime() -> bool:
    return bool(
        os.getenv("VERCEL")
        or os.getenv("VERCEL_ENV")
        or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        or os.getenv("LAMBDA_TASK_ROOT")
        or not os.access(".", os.W_OK)
    )

async def reminder_background_worker():
    logger.info("Starting background reminder worker (checking every 60s)...")
    while True:
        try:
            run_reminder_cycle()
        except Exception as e:
            logger.error(f"Error in background reminder worker: {e}")
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        logger.info("Salon Multi-Tenant Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database in lifespan: {e}")
    worker_task = None
    if not is_serverless_runtime():
        worker_task = asyncio.create_task(reminder_background_worker())
    yield
    if worker_task:
        worker_task.cancel()

app = FastAPI(
    title="Universal AI Voice & Chat Receptionist API",
    description="Enterprise Multi-Tenant Omnichannel Receptionist for Salon, Dental, Automotive, and Medical verticals",
    version="2.0.0",
    lifespan=None if is_serverless_runtime() else lifespan
)

@app.middleware("http")
async def vercel_path_rewrite_middleware(request: Request, call_next):
    try:
        matched_path = request.headers.get("x-matched-path")
        if matched_path and request.scope.get("path") in ("/api/index", "/api/index.py", "/api"):
            request.scope["path"] = matched_path
        return await call_next(request)
    except Exception as exc:
        import traceback
        return JSONResponse(status_code=500, content={"error": str(exc), "traceback": traceback.format_exc()})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(status_code=500, content={"error": str(exc), "traceback": traceback.format_exc()})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount Omnichannel Routers
app.include_router(voice_router)
app.include_router(chat_router)
app.include_router(messaging_router)
app.include_router(tenants_router)
app.include_router(streaming_voice_router)
app.include_router(auth_router)
app.include_router(testing_suite_router)
app.include_router(knowledge_router)
app.include_router(oauth_router)
app.include_router(calendar_router)

# Mount Static Web Studio Dashboard
web_dir = Path(__file__).resolve().parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")

    @app.get("/")
    def serve_index():
        index_path = web_dir / "index.html"
        if index_path.exists():
            return FileResponse(
                str(index_path),
                headers={"Cache-Control": "no-cache, must-revalidate"}
            )
        return {"service": "Universal AI Voice Receptionist", "status": "online"}

    @app.get("/site/{tenant_id}")
    @app.get("/tenant/{tenant_id}")
    def serve_tenant_site(tenant_id: str):
        """
        Renders custom customer-facing website embedded with Sofia voice receptionist,
        service catalog, pricing, and omnichannel launchers.
        """
        tenant_site_path = web_dir / "tenant_site.html"
        if tenant_site_path.exists():
            return FileResponse(
                str(tenant_site_path),
                headers={"Cache-Control": "no-cache, must-revalidate"}
            )
        return {"error": f"Tenant site template not found for {tenant_id}"}

    @app.get("/vapi-call")
    @app.get("/call")
    @app.get("/vapi-test")
    @app.get("/test-vapi")
    def serve_vapi_web_sdk_test():
        """
        Renders the dedicated Vapi Web SDK browser testing harness for WebRTC audio calls,
        transcription streaming, volume metering, and in-call message injection.
        """
        test_path = web_dir / "vapi_web_sdk_test.html"
        if test_path.exists():
            return FileResponse(
                str(test_path),
                headers={"Cache-Control": "no-cache, must-revalidate"}
            )
        return {"error": "Vapi Web SDK test page template not found"}

    @app.get("/widget.js")
    def serve_widget_script():
        """
        Serves the universal plug-and-play embeddable widget script.
        """
        widget_path = web_dir / "widget.js"
        if widget_path.exists():
            return FileResponse(
                str(widget_path),
                media_type="application/javascript",
                headers={"Cache-Control": "public, max-age=86400"}
            )
        return Response(content="console.warn('Widget script not found');", media_type="application/javascript")

    @app.get("/vapi-sdk.js")
    def serve_vapi_sdk_script():
        """
        Serves the self-hosted, resilient Vapi Web SDK script.
        """
        sdk_path = web_dir / "vapi-sdk.js"
        if sdk_path.exists():
            return FileResponse(
                str(sdk_path),
                media_type="application/javascript",
                headers={"Cache-Control": "public, max-age=86400"}
            )
        return Response(content="console.warn('Vapi SDK script not found');", media_type="application/javascript")

@app.get("/api/voice/vapi-config")
def get_vapi_web_sdk_config():
    """Returns public Vapi Web SDK configuration for browser calling."""
    public_key = (os.getenv("VAPI_PUBLIC_API_KEY") or os.getenv("VAPI_PUBLIC") or "").strip()
    assistant_id = (os.getenv("VAPI_SOPHIA_ASSISTANT_ID") or os.getenv("VAPI_ASSISTANT_ID") or "").strip()
    marcus_id = (os.getenv("VAPI_MARCUS_ASSISTANT_ID") or "").strip()
    squad_id = (os.getenv("VAPI_SQUAD_ID") or "").strip()
    return {
        "status": "success",
        "publicKey": public_key,
        "assistantId": assistant_id,
        "marcusId": marcus_id,
        "squadId": squad_id,
        "assistants": {
            "sophia": assistant_id,
            "marcus": marcus_id,
            "squad": squad_id
        },
        "sdkLoaded": bool(public_key and (assistant_id or squad_id))
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Universal AI Voice Receptionist",
        "version": "2.0.0",
        "timestamp": time.time()
    }

@app.post("/webhook/vapi-end-of-call")
async def handle_end_of_call(payload: Dict[str, Any]):
    """
    Asynchronous end-of-call webhook from Vapi.
    Parses structured data, summary, transcript, evaluation rubric, and call analytics for CRM synchronization.
    """
    message = payload.get("message") if isinstance(payload.get("message"), dict) else payload
    call_obj = message.get("call") or {}
    call_id = call_obj.get("id") or message.get("callId") or message.get("id") or payload.get("call_id") or f"call_{int(time.time())}"

    analysis = message.get("analysis") or {}
    structured_data = analysis.get("structuredData") or message.get("structuredData") or {}

    customer = call_obj.get("customer") or message.get("customer") or {}
    caller_name = structured_data.get("caller_name") or customer.get("name") or ""
    caller_phone = structured_data.get("caller_phone") or customer.get("number") or ""
    caller_email = structured_data.get("caller_email") or ""
    service_name = structured_data.get("service_name") or ""
    call_outcome = structured_data.get("call_outcome") or "general_inquiry"
    sentiment = structured_data.get("sentiment") or "neutral"
    action_items = structured_data.get("action_items") or []

    summary = analysis.get("summary") or message.get("summary") or "No summary available"
    transcript = message.get("transcript") or message.get("artifact", {}).get("transcript") or ""
    recording_url = message.get("recordingUrl") or message.get("artifact", {}).get("recordingUrl") or ""
    duration_seconds = int(message.get("durationSeconds") or call_obj.get("duration") or 0)
    eval_score = str(analysis.get("successEvaluation") or message.get("successEvaluation") or "Pass")

    log_entry = {
        "call_id": call_id,
        "tenant_id": payload.get("tenant_id") or "salon",
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "caller_email": caller_email,
        "service_name": service_name,
        "call_outcome": call_outcome,
        "sentiment": sentiment,
        "summary": summary,
        "transcript": transcript,
        "recording_url": recording_url,
        "duration_seconds": duration_seconds,
        "evaluation_score": eval_score,
        "action_items": action_items,
        "structured_data": structured_data
    }
    
    saved_res = save_call_log(log_entry)

    if caller_phone and (caller_name or caller_email):
        try:
            from backend.database import save_customer_profile
            save_customer_profile(phone=caller_phone, full_name=caller_name, email=caller_email, tenant_id=payload.get("tenant_id") or "salon")
        except Exception as e:
            logger.warning(f"Could not auto-save customer profile from call log: {e}")

    # =========================================================================
    # Sophia Salon Voice AI - Post-Call & Escalation Engine (n8n & Slack Integration)
    # =========================================================================
    escalation_result = {}
    sentiment_lower = str(sentiment).lower().strip()
    is_frustrated = (
        sentiment_lower in ("frustrated", "angry", "upset")
        or bool(structured_data.get("escalation_needed"))
        or call_outcome in ("escalated", "disputed")
    )

    if is_frustrated:
        # 1. Dispatch Instant Urgent Slack Alert to Marcus (U0A57CPCBRC)
        slack_target = os.getenv("SLACK_ESCALATION_USER_ID", "U0A57CPCBRC")
        slack_blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 Marcus Urgent Alert: Frustrated Caller", "emoji": True}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Customer:* {caller_name or 'Valued Guest'}\n*Phone:* {caller_phone}\n*Sentiment:* 🔴 {sentiment_lower}\n*Service:* {service_name or 'General Inquiry'}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Call Summary:*\n{summary}"
                }
            }
        ]
        slack_res = notification_dispatcher.send_slack_alert(
            channel=slack_target,
            title="🚨 Marcus Urgent Alert: Frustrated Caller",
            message=f"*Customer:* {caller_name or 'Valued Guest'}\n*Phone:* {caller_phone}\n*Sentiment:* 🔴 {sentiment_lower}\n*Call Summary:*\n{summary}",
            blocks=slack_blocks
        )
        escalation_result["slack_alert"] = slack_res
    else:
        # Happy / Neutral Customer Flow: Post-Call WhatsApp Review Request (after 2 hours simulation)
        if caller_phone:
            review_res = notification_dispatcher.send_post_call_review_whatsapp(
                to_phone=caller_phone,
                customer_name=caller_name or "Valued Guest"
            )
            escalation_result["whatsapp_review"] = review_res

    # 30-Day Retention Cold Email Follow-Up
    if caller_email:
        retention_res = notification_dispatcher.send_retention_cold_email(
            to_email=caller_email,
            customer_name=caller_name or "Valued Guest",
            days_since_visit=30
        )
        escalation_result["retention_email"] = retention_res

    # Forward event payload to n8n Webhook if configured
    n8n_post_call_url = os.getenv("N8N_POST_CALL_WEBHOOK_URL") or os.getenv("N8N_WEBHOOK_URL")
    if n8n_post_call_url and not n8n_post_call_url.startswith("your_") and not os.getenv("TESTING"):
        try:
            import httpx
            httpx.post(n8n_post_call_url, json=payload, timeout=4.0)
            escalation_result["n8n_forwarded"] = True
        except Exception as e:
            logger.warning(f"Could not forward post-call event to n8n: {e}")
            escalation_result["n8n_forwarded"] = False

    logger.info(f"✅ Call Log Archived: {call_id} | Outcome: {call_outcome} | Score: {eval_score} | Frustrated: {is_frustrated}")
    return {
        "status": "success",
        "message": "End-of-call metadata, escalation, and post-call workflows executed successfully",
        "call_id": call_id,
        "outcome": call_outcome,
        "evaluation": eval_score,
        "is_frustrated": is_frustrated,
        "escalation_engine": escalation_result
    }

@app.get("/admin/call-logs")
def get_admin_call_logs(tenant_id: Optional[str] = None, limit: int = 50):
    """Retrieve recorded call logs, evaluation rubrics, transcripts, and analytics."""
    logs = list_call_logs(tenant_id=tenant_id, limit=limit)
    analytics = get_call_analytics(tenant_id=tenant_id)
    return {
        "status": "success",
        "total_returned": len(logs),
        "analytics": analytics,
        "call_logs": logs
    }

@app.get("/admin/call-logs/{call_id}")
def get_single_call_log(call_id: str):
    """Fetch a specific call log by its unique call_id."""
    log = get_call_log(call_id)
    if not log:
        raise HTTPException(status_code=404, detail="Call log not found")
    return {"status": "success", "call_log": log}

@app.get("/api/tools/catalog")
def get_tools_catalog():
    """Returns the comprehensive categorized enterprise tool registry with parameter schemas."""
    return CATEGORIZED_TOOLS_CATALOG

@app.get("/admin/appointments/excel")
def download_excel_sheet():
    """Download the current live Excel spreadsheet containing all appointments and reminder statuses."""
    excel_path = get_excel_path()
    try:
        from backend.excel_manager import rebuild_real_user_excel_sheet
        rebuild_real_user_excel_sheet(excel_path)
    except Exception as e:
        logger.warning(f"Excel real user rebuild warning: {e}")
        if not os.path.exists(excel_path):
            init_db()

    return FileResponse(
        path=excel_path,
        filename="salon_appointments.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.get("/api/cron/reminders")
@app.post("/api/reminders/trigger")
@app.post("/admin/trigger-reminders")
def manual_trigger_reminders():
    """Manually or cron-triggered scanning cycle for 24h WhatsApp/SMS/Email reminders and 1h automated calls."""
    stats = run_reminder_cycle()
    return {
        "status": "success",
        "message": "Reminder cycle executed successfully",
        "stats": stats
    }

@app.post("/admin/sync-google-sheet")
def manual_sync_google_sheet():
    """Manually triggers real-user rebuild and styling on the connected Google Sheet."""
    from backend.google_sheets_sync import rebuild_real_user_google_sheet
    success = rebuild_real_user_google_sheet()
    if success:
        return {"status": "success", "message": "Google Sheet synchronized with real user appointments"}
    return {"status": "error", "message": "Failed to synchronize Google Sheet"}

@app.get("/admin/tenants")
def list_tenants():
    """List all onboarded salon tenants."""
    return {"tenants": get_all_tenants()}

@app.post("/admin/tenants")
def onboard_tenant(payload: Dict[str, Any]):
    """Onboard a new salon with services and stylists."""
    tenant_id = payload.get("tenant_id")
    name = payload.get("name")
    phone = payload.get("phone_number")
    address = payload.get("address", "")
    services = payload.get("services", [("Womens Haircut", 45, 75), ("Mens Cut", 30, 45)])
    stylists = payload.get("stylists", ["Elena", "Marcus"])

    if not tenant_id or not name or not phone:
        raise HTTPException(status_code=400, detail="tenant_id, name, and phone_number are required")

    tenant = create_tenant(tenant_id, name, phone, address, services, stylists)
    return {"status": "success", "tenant": tenant}

@app.get("/admin/appointments")
def list_appointments(tenant_id: Optional[str] = None):
    """Query appointments across all tenants or for a specific salon, surfacing only real user appointments."""
    all_appts = list_all_appointments(tenant_id)
    real_appts = [
        a for a in all_appts
        if a.get("caller_name", "").lower() not in (
            "sarah connor", "elena fisher", "automated verification test", "test client", "david beckham", "alexander hamilton", "grace hopper"
        )
    ]
    return {"appointments": real_appts}

@app.post("/test/quick-booking")
def quick_test_booking(
    name: str = "Test Client",
    service: str = "Womens Haircut",
    stylist: str = "Elena",
    phone: str = "+16673070119",
    tenant_id: str = "salon"
):
    """
    Minimal 1-click test booking endpoint.
    Instantly writes a booking to SQLite, Google Calendar, Excel, and live Google Sheets.
    """
    dt = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT15:00:00")
    booking = book_new_appointment(
        caller_name=name,
        caller_phone=phone,
        service_name=service,
        appointment_datetime=dt,
        stylist_name=stylist,
        tenant_id=tenant_id
    )
    logger.info(f"⚡ [MINIMAL TEST] Quick booking created: {booking['booking_id']}")
    return {
        "status": "success",
        "message": f"Appointment {booking['booking_id']} created and synced to Google Calendar, Excel & Google Sheets!",
        "booking": booking
    }


class DirectBookRequest(BaseModel):
    caller_name: str
    caller_phone: str
    service_name: str
    stylist_name: Optional[str] = "Marcus"
    appointment_datetime: Optional[str] = None
    tenant_id: Optional[str] = "salon"
    notes: Optional[str] = ""
    caller_email: Optional[str] = ""


@app.post("/api/appointments/book")
def direct_book_appointment(payload: DirectBookRequest):
    """Direct 1-click slot booking into Neon PostgreSQL, Google Calendar, and automated email confirmation."""
    dt = payload.appointment_datetime
    if not dt:
        dt = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT14:00:00")
    res = book_new_appointment(
        caller_name=payload.caller_name,
        caller_phone=payload.caller_phone,
        service_name=payload.service_name,
        appointment_datetime=dt,
        stylist_name=payload.stylist_name or "Marcus",
        tenant_id=payload.tenant_id or "salon",
        channel="web_portal",
        notes=payload.notes or "Booked via Luxe Saloon VIP Schedule",
        caller_email=payload.caller_email or ""
    )
    try:
        from backend.database import save_customer_profile
        save_customer_profile(phone=payload.caller_phone, full_name=payload.caller_name, email=payload.caller_email or "", tenant_id=payload.tenant_id or "salon")
    except Exception as e:
        logger.warning(f"Could not save customer profile: {e}")
    return {"status": "success", "booking": res}


@app.get("/api/schedule/availability")
def get_schedule_availability(tenant_id: str = "salon"):
    """Returns visual schedule matrix, hourly capacity metrics, and booked vs open slots."""
    appts = list_all_appointments(tenant_id)
    hours = ["09:00 AM", "10:30 AM", "12:00 PM", "01:30 PM", "03:00 PM", "04:30 PM", "06:00 PM"]
    stylists = [
        {"name": "Sofia Alston", "role": "Master Stylist & Director", "avatar": "💇‍♀️"},
        {"name": "Marcus Vance", "role": "Balayage & Color Director", "avatar": "🎨"},
        {"name": "Elena Rostova", "role": "Medical Aesthetician", "avatar": "✨"},
        {"name": "Chloe Laurent", "role": "Nail Artist & Spa Specialist", "avatar": "💅"}
    ]
    
    # Calculate occupancy stats
    total_slots = len(hours) * len(stylists)
    booked_count = len(appts)
    available_count = max(0, total_slots - min(booked_count, 14))

    return {
        "tenant_id": tenant_id,
        "hours": hours,
        "stylists": stylists,
        "metrics": {
            "total_slots": total_slots,
            "booked_appointments": booked_count,
            "open_slots": available_count,
            "occupancy_rate": f"{round((min(booked_count, 14) / total_slots) * 100)}%",
            "active_stylists": len(stylists)
        },
        "appointments": appts[:25]
    }

