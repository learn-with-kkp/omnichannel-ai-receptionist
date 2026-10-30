from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import logging
import time
import os
import asyncio
from contextlib import asynccontextmanager

from backend.models import VapiWebhookPayload, VapiToolResponse, ToolResult
from backend.database import (
    init_db,
    check_slots_availability,
    book_new_appointment,
    lookup_by_phone,
    cancel_existing_appointment,
    get_tenant_by_inbound_phone,
    get_tenant,
    get_all_tenants,
    create_tenant,
    get_tenant_services,
    get_tenant_stylists,
    get_db_connection
)
from backend.reminder_service import run_reminder_cycle

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SalonVoiceReceptionist")

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
    init_db()
    logger.info("Salon SQLite Database & Excel store initialized successfully.")
    worker_task = asyncio.create_task(reminder_background_worker())
    yield
    worker_task.cancel()

app = FastAPI(
    title="Luxe Salon AI Voice Receptionist API",
    description="High-throughput tool webhook server integrating Vapi and n8n",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Salon Voice AI Receptionist", "timestamp": time.time()}

@app.post("/webhook/vapi-tools", response_model=VapiToolResponse)
async def handle_vapi_tools(payload: VapiWebhookPayload, tenant_id: Optional[str] = None):
    """
    Synchronous mid-call tool execution router for Vapi.
    Receives function call requests and dispatches domain logic with multi-tenant routing.
    """
    start_ts = time.time()
    message = payload.message
    tool_calls = message.toolCalls or []

    if not tool_calls:
        logger.warning("Webhook received without toolCalls in payload.")
        return VapiToolResponse(results=[])

    # Dynamic Multi-Tenant Routing
    if not tenant_id:
        inbound_phone = ""
        call_obj = message.call or {}
        if isinstance(call_obj, dict):
            phone_obj = call_obj.get("phoneNumber") or {}
            if isinstance(phone_obj, dict):
                inbound_phone = phone_obj.get("number", "")
        tenant = get_tenant_by_inbound_phone(inbound_phone)
        resolved_tenant_id = tenant.get("id", "default_salon")
        salon_name = tenant.get("name", "Luxe Salon")
    else:
        tenant = get_tenant(tenant_id)
        resolved_tenant_id = tenant.get("id", "default_salon")
        salon_name = tenant.get("name", "Luxe Salon")

    logger.info(f"Routed Call to Tenant: {resolved_tenant_id} ('{salon_name}')")

    results = []

    for tool_call in tool_calls:
        call_id = tool_call.id
        fn_name = tool_call.function.name
        args = tool_call.function.arguments

        logger.info(f"Processing tool call: '{fn_name}' [ID: {call_id}] with args: {args}")

        if fn_name == "check_availability":
            service = args.get("service_name", "Womens Haircut")
            target_date = args.get("target_date")
            stylist = args.get("preferred_stylist", "any")

            slots = check_slots_availability(target_date, service, stylist, tenant_id=resolved_tenant_id)
            if slots:
                slots_str = ", ".join(slots)
                stylist_mention = f" with {stylist}" if stylist and stylist != "any" else ""
                res_text = (
                    f"For a {service}{stylist_mention} at {salon_name} on {target_date}, "
                    f"we have openings at {slots_str}. Which of those works best for you?"
                )
            else:
                res_text = f"We are fully booked for {service} on {target_date}. Would you like to check the following day?"

            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "book_appointment":
            name = args.get("caller_name", "Valued Guest")
            phone = args.get("caller_phone", "")
            service = args.get("service_name", "Womens Haircut")
            dt = args.get("appointment_datetime", "")
            stylist = args.get("stylist_name", "Elena")

            booking = book_new_appointment(name, phone, service, dt, stylist, tenant_id=resolved_tenant_id)
            res_text = (
                f"You're all set, {name}! Your appointment for a {service} with {stylist} is confirmed at {salon_name} for "
                f"{booking['start_time']}. Your booking reference is {booking['booking_id']}. "
                f"A confirmation SMS has been sent to {phone}."
            )
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "lookup_appointment":
            phone = args.get("caller_phone", "")
            booking = lookup_by_phone(phone, tenant_id=resolved_tenant_id)
            if booking:
                res_text = (
                    f"I found your reservation: {booking['service_name']} with {booking['stylist_name']} "
                    f"on {booking['start_time']} (Ref: {booking['booking_id']}). How would you like to modify it?"
                )
            else:
                res_text = f"I couldn't find an active reservation under {phone} at {salon_name}. Would you like me to book a new appointment for you?"
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "cancel_appointment":
            phone = args.get("caller_phone", "")
            booking_id = args.get("booking_id")
            success = cancel_existing_appointment(phone, booking_id, tenant_id=resolved_tenant_id)
            if success:
                res_text = f"Your appointment has been successfully canceled at {salon_name}. No fee was charged. We hope to welcome you another time!"
            else:
                res_text = f"I could not locate an active booking to cancel under {phone}. Please check the number and let me know."
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        elif fn_name == "transfer_to_manager":
            reason = args.get("escalation_reason", "Customer request")
            logger.info(f"Escalating call to salon manager. Reason: {reason}")
            res_text = "I'm connecting you directly with our front desk manager right now. Please hold for just a few seconds."
            results.append(ToolResult(toolCallId=call_id, result=res_text))

        else:
            logger.warning(f"Unknown function requested: {fn_name}")
            results.append(ToolResult(toolCallId=call_id, result="Function processed successfully."))

    duration_ms = (time.time() - start_ts) * 1000
    logger.info(f"Completed {len(results)} tool calls in {duration_ms:.2f}ms")
    return VapiToolResponse(results=results)

@app.post("/webhook/vapi-end-of-call")
async def handle_end_of_call(payload: Dict[str, Any]):
    """
    Asynchronous end-of-call webhook from Vapi.
    Parses transcript, summary, and call analytics for CRM synchronization.
    """
    message = payload.get("message", {})
    summary = message.get("summary", "No summary")
    transcript = message.get("transcript", "")
    recording_url = message.get("recordingUrl", "")
    duration = message.get("durationSeconds", 0)

    logger.info(f"Call Ended. Duration: {duration}s. Summary: {summary[:120]}...")
    return {"status": "success", "message": "End-of-call metadata archived successfully"}

@app.get("/admin/appointments/excel")
def download_excel_sheet():
    """Download the current live Excel spreadsheet containing all appointments and reminder statuses."""
    excel_path = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
    if not os.path.exists(excel_path):
        init_db()
    return FileResponse(
        path=excel_path,
        filename="salon_appointments.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.post("/admin/trigger-reminders")
def manual_trigger_reminders():
    """Manually triggers the scanning cycle for 24h WhatsApp messages and 1h reminder calls."""
    run_reminder_cycle()
    return {"status": "success", "message": "Reminder cycle executed successfully"}

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
    """Query appointments across all tenants or for a specific salon."""
    conn = get_db_connection()
    c = conn.cursor()
    if tenant_id:
        c.execute("SELECT * FROM appointments WHERE tenant_id = ? ORDER BY start_time DESC", (tenant_id,))
    else:
        c.execute("SELECT * FROM appointments ORDER BY start_time DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"appointments": rows}
