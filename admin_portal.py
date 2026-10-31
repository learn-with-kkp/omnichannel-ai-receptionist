import streamlit as st
import pandas as pd
import sqlite3
import os
import requests
from datetime import datetime
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title="Luxe AI Voice Receptionist - Salon Portal",
    page_icon="💇‍♀️",
    layout="wide"
)

DB_PATH = os.getenv("SALON_DB_PATH", "salon_bookings.db")
EXCEL_PATH = os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Custom Styling ---
st.markdown("""
<style>
    .metric-card {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #1F4E79;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .status-confirmed { color: #16A34A; font-weight: bold; }
    .status-cancelled { color: #DC2626; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Title & Header
st.title("💇‍♀️ AI Voice Receptionist - Command Center")
st.caption("Multi-Tenant Salon Booking Platform with Real-Time Voice Telephony, WhatsApp Automation, and Excel Sync.")

# Check Backend Status
col_h1, col_h2 = st.columns([3, 1])
with col_h2:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        if r.status_code == 200:
            st.success("🟢 Voice Backend: Connected")
        else:
            st.warning("🟡 Voice Backend: Warning")
    except Exception:
        st.error("🔴 Voice Backend: Offline")

# Sidebar: Salon Tenant Selector
st.sidebar.header("🏪 Salon Tenant")
conn = get_db()
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS tenants (id TEXT PRIMARY KEY, name TEXT, phone_number TEXT, address TEXT, currency TEXT, created_at TEXT)")
c.execute("SELECT id, name FROM tenants ORDER BY created_at DESC")
tenants = c.fetchall()
conn.close()

tenant_options = {t["name"]: t["id"] for t in tenants} if tenants else {"Luxe Salon": "default_salon"}
selected_tenant_name = st.sidebar.selectbox("Select Active Salon:", list(tenant_options.keys()))
active_tenant_id = tenant_options[selected_tenant_name]

# Navigation Tabs
tab_overview, tab_appointments, tab_services, tab_onboard, tab_telephony = st.tabs([
    "📈 Performance & Metrics",
    "📅 Live Appointments",
    "✂️ Stylists & Services",
    "🚀 Onboard New Salon",
    "📞 Telephony & Reminders"
])

# --- TAB 1: OVERVIEW & KPIS ---
with tab_overview:
    # Minimal 1-Click Testing Action Bar
    test_col1, test_col2 = st.columns([2, 3])
    with test_col1:
        if st.button("⚡ 1-Click Minimal Test: Create Booking Now", type="primary"):
            try:
                res = requests.post(f"{API_BASE}/test/quick-booking", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"🎉 {data.get('message')}")
                    st.toast("✅ Synced to SQLite, Excel & Google Sheets!", icon="🚀")
                    st.rerun()
                else:
                    st.error("Failed to execute test booking.")
            except Exception as e:
                st.error(f"Test error: {e}")
    with test_col2:
        st.caption("👈 Click to instantly simulate a voice booking. Watch it appear live below and inside your Google Sheet!")

    st.markdown("---")

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM appointments WHERE tenant_id = ?", (active_tenant_id,))
    appts = [dict(r) for r in c.fetchall()]
    conn.close()

    total_bookings = len(appts)
    confirmed_bookings = len([a for a in appts if a["status"] == "CONFIRMED"])
    wa_sent = len([a for a in appts if a.get("whatsapp_24h_sent") == 1])
    calls_done = len([a for a in appts if a.get("call_1h_sent") == 1])
    est_revenue = sum([75 for a in appts if a["status"] == "CONFIRMED"])  # conservative baseline

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Bookings", total_bookings)
    kpi2.metric("Confirmed Slots", confirmed_bookings)
    kpi3.metric("Est. Revenue", f"${est_revenue:,}")
    kpi4.metric("24h WhatsApp Sent", wa_sent)
    kpi5.metric("1h Voice Calls", calls_done)

    st.markdown("---")
    st.subheader("💡 Salon Business Impact")
    st.info(f"**{selected_tenant_name}** has saved an estimated **{total_bookings * 4.5:.1f} hours** of front-desk manual phone tag and captured **${est_revenue:,}** in appointments through autonomous voice handling.")

# --- TAB 2: LIVE APPOINTMENTS ---
with tab_appointments:
    st.subheader(f"📅 Appointments for {selected_tenant_name}")
    
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT id as 'Booking ID', caller_name as 'Client', caller_phone as 'Phone',
               service_name as 'Service', stylist_name as 'Stylist', start_time as 'Time',
               status as 'Status', whatsapp_24h_sent as '24h WA', call_1h_sent as '1h Call'
        FROM appointments WHERE tenant_id = ?
        ORDER BY start_time DESC
    """, (active_tenant_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
    else:
        st.write("No appointments booked yet for this salon.")

    col_d1, col_d2 = st.columns([2, 2])
    with col_d1:
        if os.path.exists(EXCEL_PATH):
            with open(EXCEL_PATH, "rb") as f:
                st.download_button(
                    label="📥 Download Master Excel Sheet (.xlsx)",
                    data=f.read(),
                    file_name="salon_appointments.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# --- TAB 3: SERVICES & STYLISTS ---
with tab_services:
    st.subheader("✂️ Configured Stylists & Services")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name, duration_minutes, price FROM services WHERE tenant_id = ?", (active_tenant_id,))
    services = [dict(r) for r in c.fetchall()]
    
    c.execute("SELECT name, active FROM stylists WHERE tenant_id = ?", (active_tenant_id,))
    stylists = [dict(r) for r in c.fetchall()]
    conn.close()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.write("### Services & Pricing")
        if services:
            st.table(pd.DataFrame(services))
        else:
            st.info("No custom services found. Default salon pricing active.")

    with col_s2:
        st.write("### Stylist Team")
        if stylists:
            st.table(pd.DataFrame(stylists))
        else:
            st.info("No stylists configured.")

# --- TAB 4: ONBOARD NEW SALON ---
with tab_onboard:
    st.subheader("🚀 Onboard a New Salon in 60 Seconds")
    st.write("Fill in the client's information to generate their dedicated tenant configuration.")

    with st.form("onboard_form"):
        new_name = st.text_input("Salon Business Name", placeholder="e.g. SOHO Hair & Color Studio")
        new_id = st.text_input("Unique Tenant Slug", placeholder="e.g. soho_nyc")
        new_phone = st.text_input("Assigned Inbound Phone Number (E.164)", placeholder="+12125550188")
        new_address = st.text_input("Salon Address", placeholder="128 Prince St, New York, NY")
        new_stylists = st.text_area("Stylists (comma-separated)", "Alexander, Maya, Jordan")
        
        submitted = st.form_submit_button("✨ Provision New Salon Client")
        if submitted:
            if not new_name or not new_id or not new_phone:
                st.error("Please provide Salon Name, Tenant Slug, and Inbound Phone Number.")
            else:
                stylist_list = [s.strip() for s in new_stylists.split(",") if s.strip()]
                default_srvs = [
                    ("Womens Haircut", 45, 85),
                    ("Mens Cut", 30, 50),
                    ("Balayage", 150, 220),
                    ("Blowout", 45, 65)
                ]
                try:
                    res = requests.post(f"{API_BASE}/admin/tenants", json={
                        "tenant_id": new_id.strip(),
                        "name": new_name.strip(),
                        "phone_number": new_phone.strip(),
                        "address": new_address.strip(),
                        "services": default_srvs,
                        "stylists": stylist_list
                    }, timeout=5)
                    if res.status_code == 200:
                        st.success(f"🎉 Successfully provisioned **{new_name}**! They are now live on the platform.")
                        st.balloons()
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

# --- TAB 5: TELEPHONY & REMINDERS ---
with tab_telephony:
    st.subheader("📞 Telephony & Automated Notification Controls")
    
    st.write("### Live Public Tunnel")
    tunnel_file = Path(".live_tunnel_url")
    if tunnel_file.exists():
        tunnel_url = tunnel_file.read_text().strip()
        st.code(f"Server URL: {tunnel_url}/webhook/vapi-tools")
    else:
        st.info("Run `./start_live_tunnel.sh` to initialize the public tunnel.")

    st.write("### Trigger Reminder Cycle Manually")
    st.caption("Scans for any appointments within 24h (WhatsApp) or 1h (Voice Call).")
    if st.button("⚡ Run Scan Cycle Now"):
        try:
            r = requests.post(f"{API_BASE}/admin/trigger-reminders", timeout=5)
            if r.status_code == 200:
                st.success("✅ Reminder cycle executed. Checked all 24h and 1h intervals.")
            else:
                st.error("Failed to trigger cycle.")
        except Exception as e:
            st.error(f"Error: {e}")

