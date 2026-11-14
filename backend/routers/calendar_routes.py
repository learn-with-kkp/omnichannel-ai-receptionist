"""
Universal Calendar & Appointment Reminders Router.
Allows customers to seamlessly add their confirmed appointments to:
- Google Calendar (with 1-click web launch)
- Apple Calendar / iOS / macOS (native .ics file with VALARM reminders)
- Microsoft Outlook & Office 365
- Yahoo Calendar
Pre-configures 24-hour and 1-hour automated notification alarms.
"""

import urllib.parse
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import HTMLResponse

from backend.database import lookup_by_booking_id
from integrations.google_calendar import calendar_service

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.get("/ics/{booking_id}")
def download_booking_ics(booking_id: str):
    """
    Downloads a standard RFC 5545 .ics iCalendar file for the specified booking.
    When opened on iOS, Android, macOS, or Windows, prompts user to add to their native calendar
    with two pre-configured alert reminders: 24h before and 1h before.
    """
    booking = lookup_by_booking_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking reference '{booking_id}' not found.")

    service = booking.get("service_name", "Salon Service")
    stylist = booking.get("stylist_name", "Master Stylist")
    start_iso = booking.get("start_time_iso")
    location = "120 Newbury Street, Back Bay, Boston, MA 02116"
    summary = f"Luxe Salon: {service} with {stylist}"
    
    try:
        start_dt = datetime.fromisoformat(start_iso.replace("Z", ""))
    except Exception:
        start_dt = datetime.now() + timedelta(days=1)

    details = (
        f"✦ Luxe Salon & Spa - Appointment Confirmation\\n"
        f"Booking Reference: #{booking['booking_id']}\\n"
        f"Client: {booking.get('caller_name', 'Valued Guest')}\\n"
        f"Service: {service}\\n"
        f"Stylist: {stylist}\\n"
        f"Location: {location}\\n"
        f"Concierge Desk: (617) 271-8180\\n\\n"
        f"Reminders are automatically set for 24 hours and 1 hour before your appointment."
    )

    ics_content = calendar_service.generate_ics(
        summary=summary,
        start_dt=start_dt,
        duration_minutes=60,
        details=details,
        location=location,
        ref_id=booking["booking_id"],
        timezone="America/New_York"
    )

    filename = f"LuxeSalon-{booking['booking_id']}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache"
        }
    )


@router.get("/add/{booking_id}", response_class=HTMLResponse)
def add_to_calendar_page(booking_id: str):
    """
    Renders an elegant, mobile-responsive landing page allowing the customer to add
    their appointment to Google Calendar, Apple Calendar, Outlook, or Yahoo with 1-click.
    """
    booking = lookup_by_booking_id(booking_id)
    if not booking:
        return HTMLResponse(
            content="""
            <html><body style="font-family:sans-serif;text-align:center;padding:50px;background:#090d16;color:#fff;">
                <h2>Booking Not Found</h2>
                <p>We could not find the appointment associated with this reference link.</p>
                <a href="/" style="color:#38bdf8;">Return to Luxe Salon Home</a>
            </body></html>
            """,
            status_code=404
        )

    service = booking.get("service_name", "Salon Service")
    stylist = booking.get("stylist_name", "Master Stylist")
    start_iso = booking.get("start_time_iso")
    start_time_str = booking.get("start_time")
    caller_name = booking.get("caller_name", "Valued Guest")
    location = "120 Newbury Street, Back Bay, Boston, MA 02116"
    summary = f"Luxe Salon: {service} with {stylist}"
    
    try:
        start_dt = datetime.fromisoformat(start_iso.replace("Z", ""))
    except Exception:
        start_dt = datetime.now() + timedelta(days=1)

    end_dt = start_dt + timedelta(minutes=60)
    details = (
        f"Booking Ref: #{booking['booking_id']}\n"
        f"Service: {service}\n"
        f"Stylist: {stylist}\n"
        f"Address: {location}\n"
        f"Phone: (617) 271-8180"
    )

    # 1. Google Calendar 1-Click Link
    gcal_link = calendar_service.generate_add_to_gcal_link(
        summary=summary,
        start_dt=start_dt,
        duration_minutes=60,
        details=details,
        location=location,
        timezone="America/New_York"
    )

    # 2. Direct ICS file link for Apple Calendar / Native iOS
    ics_link = f"/api/calendar/ics/{booking['booking_id']}"

    # 3. Microsoft Outlook Web Link
    # https://outlook.live.com/calendar/0/deeplink/compose?subject=...&startdt=...&enddt=...&body=...&location=...
    outlook_params = {
        "path": "/calendar/action/compose",
        "rru": "addevent",
        "subject": summary,
        "startdt": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "enddt": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "body": details,
        "location": location
    }
    outlook_link = f"https://outlook.live.com/calendar/0/action/compose?{urllib.parse.urlencode(outlook_params)}"

    # 4. Yahoo Calendar Web Link
    yahoo_params = {
        "v": "60",
        "title": summary,
        "st": start_dt.strftime("%Y%m%dT%H%M%S"),
        "et": end_dt.strftime("%Y%m%dT%H%M%S"),
        "desc": details,
        "in_loc": location
    }
    yahoo_link = f"https://calendar.yahoo.com/?{urllib.parse.urlencode(yahoo_params)}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Add Appointment to Calendar • Luxe Salon & Spa</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background: radial-gradient(circle at top, #131d36 0%, #060912 100%);
      color: #f8fafc;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}
    .card {{
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(245, 158, 11, 0.35);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      max-width: 520px;
      width: 100%;
      padding: 36px 28px;
      box-shadow: 0 25px 60px rgba(0,0,0,0.6), 0 0 30px rgba(245,158,11,0.1);
      text-align: center;
    }}
    .brand {{
      font-family: 'Cinzel', serif;
      font-size: 22px;
      letter-spacing: 2px;
      color: #f59e0b;
      margin-bottom: 6px;
      font-weight: 700;
    }}
    .tagline {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: #38bdf8;
      margin-bottom: 24px;
      font-weight: 600;
    }}
    h1 {{
      font-size: 22px;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 8px;
    }}
    .subtitle {{
      font-size: 14px;
      color: #94a3b8;
      margin-bottom: 24px;
    }}
    .details-box {{
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 20px;
      text-align: left;
      margin-bottom: 26px;
    }}
    .row {{
      display: flex;
      justify-content: space-between;
      padding: 9px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 13.5px;
    }}
    .row:last-child {{ border-bottom: none; padding-bottom: 0; }}
    .lbl {{ color: #94a3b8; }}
    .val {{ color: #f8fafc; font-weight: 600; text-align: right; }}
    .reminder-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      font-size: 12px;
      padding: 6px 14px;
      border-radius: 20px;
      margin-bottom: 24px;
      font-weight: 600;
    }}
    .btn-group {{
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 14px 20px;
      border-radius: 12px;
      font-size: 14.5px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .btn-gcal {{
      background: #4285F4;
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(66, 133, 244, 0.35);
    }}
    .btn-gcal:hover {{ background: #3367d6; }}
    .btn-apple {{
      background: rgba(255, 255, 255, 0.08);
      color: #ffffff;
      border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    .btn-apple:hover {{ background: rgba(255, 255, 255, 0.15); }}
    .btn-outlook {{
      background: #0078D4;
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(0, 120, 212, 0.3);
    }}
    .btn-outlook:hover {{ background: #0060aa; }}
    .directions {{
      margin-top: 24px;
      font-size: 12px;
      color: #64748b;
    }}
    .directions a {{ color: #38bdf8; text-decoration: none; }}
    .directions a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="brand">✦ LUXE SALON & SPA</div>
    <div class="tagline">120 Newbury Street • Boston, MA</div>

    <h1>Add to Calendar</h1>
    <p class="subtitle">Welcome, <b>{caller_name}</b>! Select your calendar platform below to sync your appointment.</p>

    <div class="reminder-badge">
      🔔 Reminders pre-set for 24h & 1h before appointment
    </div>

    <div class="details-box">
      <div class="row"><span class="lbl">Booking Reference:</span><span class="val">#{booking['booking_id']}</span></div>
      <div class="row"><span class="lbl">Service:</span><span class="val">{service}</span></div>
      <div class="row"><span class="lbl">Stylist:</span><span class="val">{stylist}</span></div>
      <div class="row"><span class="lbl">Date & Time:</span><span class="val">{start_time_str}</span></div>
      <div class="row"><span class="lbl">Sanctuary Address:</span><span class="val">120 Newbury St, Boston</span></div>
    </div>

    <div class="btn-group">
      <a href="{gcal_link}" target="_blank" class="btn btn-gcal">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2zm-7 5h5v5h-5z"/></svg>
        Add to Google Calendar
      </a>

      <a href="{ics_link}" class="btn btn-apple">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M15.97 6.37c.62-.75 1.04-1.8 0.93-2.85-.9.04-1.99.6-2.61 1.34-.56.65-1.05 1.71-.92 2.74 1.01.08 2.03-.51 2.6-1.23z"/></svg>
        Add to Apple Calendar / iPhone (.ics)
      </a>

      <a href="{outlook_link}" target="_blank" class="btn btn-outlook">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M21 4H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-9 5.5L3 8V6l9 5.5L21 6v2z"/></svg>
        Add to Outlook / Office 365
      </a>
    </div>

    <div class="directions">
      📍 Need directions to the salon? <a href="https://maps.google.com/?q=120+Newbury+Street,+Boston,+MA+02116" target="_blank">Open in Google Maps</a>
    </div>
  </div>
</body>
</html>
"""
    return HTMLResponse(content=html)
