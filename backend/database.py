"""
Universal Database Access Layer.
Supports:
1. Neon Cloud PostgreSQL (DATABASE_URL / NEON_DATABASE_URL / POSTGRES_URL) in production.
2. Local & In-Memory SQLite fallback for development and automated test suites.
3. Vercel serverless persistence with reconnect resilience and connection lifecycle management.
"""

import os
import re
import sqlite3
import hashlib
import secrets
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger("UniversalDatabase")

try:
    from backend.excel_manager import (
        get_or_create_workbook,
        append_appointment_to_excel,
        update_excel_reminders
    )
    from backend.google_sheets_sync import sync_appointment_to_google_sheets
except ImportError:
    try:
        from excel_manager import (
            get_or_create_workbook,
            append_appointment_to_excel,
            update_excel_reminders
        )
        from google_sheets_sync import sync_appointment_to_google_sheets
    except Exception:
        get_or_create_workbook = lambda p: None
        append_appointment_to_excel = lambda r, filepath=None: None
        update_excel_reminders = lambda b, **kw: None
        sync_appointment_to_google_sheets = lambda r, tenant_id=None: None

try:
    from integrations.google_calendar import calendar_service
except ImportError:
    try:
        from ..integrations.google_calendar import calendar_service
    except Exception:
        calendar_service = None

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "salon")

def get_database_url() -> Optional[str]:
    """Retrieves Neon / PostgreSQL connection string from environment."""
    url = (
        os.getenv("DATABASE_URL")
        or os.getenv("NEON_POSTGRES_CONNECTION_URL")
        or os.getenv("NEON_DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRESQL_URL")
    )
    if url and ("postgres://" in url or "postgresql://" in url):
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url
    return None

def is_serverless() -> bool:
    """Detect if running in a serverless environment (Vercel, AWS Lambda, read-only FS)."""
    return bool(
        os.getenv("VERCEL")
        or os.getenv("VERCEL_ENV")
        or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
        or os.getenv("LAMBDA_TASK_ROOT")
        or not os.access(".", os.W_OK)
    )

def is_postgres() -> bool:
    """True if configured to connect to PostgreSQL / Neon (safely falls back to SQLite for test databases)."""
    custom_db = os.getenv("SALON_DB_PATH", "")
    if custom_db.startswith("test_") or "test_" in custom_db:
        return False
    return bool(PSYCOPG2_AVAILABLE and get_database_url())

def get_sqlite_path() -> str:
    """Safe SQLite path, avoiding read-only filesystem errors on Vercel/Lambda."""
    if is_serverless():
        custom = os.getenv("SALON_DB_PATH")
        if custom and (custom.startswith("/tmp") or custom == ":memory:"):
            return custom
        return "/tmp/salon_bookings.db"
    return os.getenv("SALON_DB_PATH", "salon_bookings.db")

def get_excel_path() -> str:
    """Safe Excel path for local or serverless environments."""
    if is_serverless():
        custom = os.getenv("SALON_EXCEL_PATH")
        if custom and custom.startswith("/tmp"):
            return custom
        return "/tmp/salon_appointments.xlsx"
    return os.getenv("SALON_EXCEL_PATH", "salon_appointments.xlsx")


class DBConnectionContext:
    """
    Context manager providing uniform interface across SQLite and Neon PostgreSQL.
    Automatically handles parameter translation (? -> %s), transaction commit,
    and dictionary row serialization.
    """
    def __init__(self):
        self.is_pg = is_postgres()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        if self.is_pg:
            url = get_database_url()
            # Ensure sslmode=require for Neon if not already present
            if "?" not in url:
                url += "?sslmode=require"
            elif "sslmode=" not in url:
                url += "&sslmode=require"
            self.conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
            self.cursor = self.conn.cursor()
        else:
            db_path = get_sqlite_path()
            self.conn = sqlite3.connect(db_path, timeout=10.0)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            try:
                self.cursor.execute("PRAGMA journal_mode = WAL;")
                self.cursor.execute("PRAGMA synchronous = NORMAL;")
            except Exception:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            finally:
                if self.cursor:
                    try:
                        self.cursor.close()
                    except Exception:
                        pass
                try:
                    self.conn.close()
                except Exception:
                    pass

    def execute(self, query: str, params: tuple = ()):
        """Executes query with automatic placeholder translation (? -> %s for Postgres)."""
        if self.is_pg:
            # Substitute '?' placeholders with '%s' for PostgreSQL
            pg_query = query.replace("?", "%s")
            self.cursor.execute(pg_query, params)
        else:
            self.cursor.execute(query, params)
        return self.cursor

    def fetchone(self) -> Optional[Dict[str, Any]]:
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self) -> List[Dict[str, Any]]:
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    @property
    def rowcount(self) -> int:
        return self.cursor.rowcount


def get_db_connection():
    """Backward-compatible raw connection provider for legacy scripts and test fixtures."""
    if is_postgres():
        url = get_database_url()
        if "?" not in url:
            url += "?sslmode=require"
        return psycopg2.connect(url, cursor_factory=RealDictCursor)
    conn = sqlite3.connect(get_sqlite_path(), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass
    return conn


# --- Schema Initialization & Automatic Migration ---

def init_db():
    """
    Initializes database tables in Neon PostgreSQL or SQLite.
    Creates tables, migrates missing columns, and seeds default records.
    """
    with DBConnectionContext() as db:
        if db.is_pg:
            _init_postgres_schema(db)
        else:
            _init_sqlite_schema(db)


def _init_postgres_schema(db: DBConnectionContext):
    """PostgreSQL DDL for Neon Cloud Database."""
    # 1. Tenants Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id VARCHAR(64) PRIMARY KEY,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            currency VARCHAR(10) DEFAULT 'USD',
            created_at TEXT NOT NULL
        )
    """)

    # 2. Services Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id VARCHAR(128) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL REFERENCES tenants (id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            price INTEGER NOT NULL
        )
    """)

    # 3. Stylists Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS stylists (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL REFERENCES tenants (id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )
    """)

    # 4. Appointments Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL DEFAULT 'default_salon',
            caller_name TEXT NOT NULL,
            caller_phone TEXT NOT NULL,
            service_name TEXT NOT NULL,
            stylist_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status VARCHAR(32) NOT NULL,
            created_at TEXT NOT NULL,
            whatsapp_24h_sent INTEGER DEFAULT 0,
            call_1h_sent INTEGER DEFAULT 0,
            google_calendar_event_id TEXT DEFAULT '',
            channel VARCHAR(32) DEFAULT 'voice',
            accent VARCHAR(64) DEFAULT 'red_american',
            notes TEXT DEFAULT ''
        )
    """)

    # 5. Users Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(64) PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            company_name TEXT NOT NULL,
            tenant_id VARCHAR(64) NOT NULL,
            plan VARCHAR(32) DEFAULT 'growth',
            created_at TEXT NOT NULL
        )
    """)

    # 5b. Customers & VIP Profiles Table (Clerk & Omnichannel Sync)
    db.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id VARCHAR(64) PRIMARY KEY,
            clerk_id VARCHAR(128),
            email VARCHAR(255),
            phone VARCHAR(64),
            full_name TEXT,
            tenant_id VARCHAR(64) DEFAULT 'salon',
            created_at TEXT NOT NULL
        )
    """)

    # 6. Tenant Integrations Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS tenant_integrations (
            tenant_id VARCHAR(64) PRIMARY KEY,
            whatsapp_phone_number_id TEXT DEFAULT '',
            whatsapp_business_account_id TEXT DEFAULT '',
            meta_page_id TEXT DEFAULT '',
            instagram_account_id TEXT DEFAULT '',
            google_calendar_id TEXT DEFAULT 'primary',
            telephony_provider VARCHAR(32) DEFAULT 'vapi',
            telephony_number TEXT DEFAULT '',
            vapi_phone_id TEXT DEFAULT '',
            vapi_assistant_id TEXT DEFAULT '',
            telegram_bot_token TEXT DEFAULT '',
            telegram_chat_id TEXT DEFAULT '',
            twitter_api_key TEXT DEFAULT '',
            twitter_bearer_token TEXT DEFAULT '',
            linkedin_client_id TEXT DEFAULT '',
            linkedin_access_token TEXT DEFAULT '',
            tiktok_client_key TEXT DEFAULT '',
            tiktok_access_token TEXT DEFAULT '',
            webhook_secret TEXT DEFAULT '',
            updated_at TEXT NOT NULL
        )
    """)

    # Dynamic migrations for omnichannel social channels
    for col in [
        "telegram_bot_token", "telegram_chat_id", "twitter_api_key",
        "twitter_bearer_token", "linkedin_client_id", "linkedin_access_token",
        "tiktok_client_key", "tiktok_access_token"
    ]:
        try:
            db.execute(f"ALTER TABLE tenant_integrations ADD COLUMN IF NOT EXISTS {col} TEXT DEFAULT ''")
        except Exception:
            pass

    # Seed Default Salon if not exists
    db.execute("SELECT COUNT(*) as count FROM tenants WHERE id = ?", (DEFAULT_TENANT_ID,))
    res = db.fetchone()
    if res and res.get("count", 0) == 0:
        now = datetime.now().isoformat()
        db.execute("""
            INSERT INTO tenants (id, name, phone_number, address, currency, created_at)
            VALUES (?, 'Luxe Hair & Wellness Salon', '+16175550100', '450 Newbury Street, Boston', 'USD', ?)
            ON CONFLICT (id) DO NOTHING
        """, (DEFAULT_TENANT_ID, now))

        default_services = [
            ("Womens Haircut", 45, 75),
            ("Mens Cut", 30, 45),
            ("Balayage", 150, 180),
            ("Full Highlights", 120, 160),
            ("Keratin Treatment", 120, 220),
            ("Mani Pedi", 60, 65)
        ]
        for s_name, dur, pr in default_services:
            s_id = f"{DEFAULT_TENANT_ID}_{s_name.replace(' ', '_').lower()}"
            db.execute("""
                INSERT INTO services (id, tenant_id, name, duration_minutes, price)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET duration_minutes = EXCLUDED.duration_minutes, price = EXCLUDED.price
            """, (s_id, DEFAULT_TENANT_ID, s_name, dur, pr))

        default_stylists = ["Elena", "Marcus", "Chloe"]
        for st_name in default_stylists:
            st_id = f"{DEFAULT_TENANT_ID}_{st_name.lower()}"
            db.execute("""
                INSERT INTO stylists (id, tenant_id, name, active)
                VALUES (?, ?, ?, 1)
                ON CONFLICT (id) DO UPDATE SET active = 1
            """, (st_id, DEFAULT_TENANT_ID, st_name))


def _init_sqlite_schema(db: DBConnectionContext):
    """SQLite DDL for local, testing and serverless fallback."""
    # 1. Tenants Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            currency TEXT DEFAULT 'USD',
            created_at TEXT NOT NULL
        )
    """)

    # 2. Salon Services Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            price INTEGER NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # 3. Salon Stylists Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS stylists (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            name TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # 4. Multi-Tenant Appointments Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL DEFAULT 'default_salon',
            caller_name TEXT NOT NULL,
            caller_phone TEXT NOT NULL,
            service_name TEXT NOT NULL,
            stylist_name TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            whatsapp_24h_sent INTEGER DEFAULT 0,
            call_1h_sent INTEGER DEFAULT 0,
            google_calendar_event_id TEXT DEFAULT '',
            channel TEXT DEFAULT 'voice',
            accent TEXT DEFAULT 'red_american',
            notes TEXT DEFAULT '',
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # Check and migrate columns if table already existed
    db.execute("PRAGMA table_info(appointments)")
    columns = [row["name"] for row in db.fetchall()]
    if "tenant_id" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN tenant_id TEXT DEFAULT 'default_salon'")
    if "whatsapp_24h_sent" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN whatsapp_24h_sent INTEGER DEFAULT 0")
    if "call_1h_sent" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN call_1h_sent INTEGER DEFAULT 0")
    if "google_calendar_event_id" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN google_calendar_event_id TEXT DEFAULT ''")
    if "channel" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN channel TEXT DEFAULT 'voice'")
    if "accent" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN accent TEXT DEFAULT 'red_american'")
    if "notes" not in columns:
        db.execute("ALTER TABLE appointments ADD COLUMN notes TEXT DEFAULT ''")

    # 5. Customer Users Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            company_name TEXT NOT NULL,
            tenant_id TEXT NOT NULL,
            plan TEXT DEFAULT 'growth',
            created_at TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # 5b. Customers & VIP Profiles Table (Clerk & Omnichannel Sync)
    db.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            clerk_id TEXT,
            email TEXT,
            phone TEXT,
            full_name TEXT,
            tenant_id TEXT DEFAULT 'salon',
            created_at TEXT NOT NULL
        )
    """)

    # 6. Tenant Omnichannel Integrations Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS tenant_integrations (
            tenant_id TEXT PRIMARY KEY,
            whatsapp_phone_number_id TEXT DEFAULT '',
            whatsapp_business_account_id TEXT DEFAULT '',
            meta_page_id TEXT DEFAULT '',
            instagram_account_id TEXT DEFAULT '',
            google_calendar_id TEXT DEFAULT 'primary',
            telephony_provider TEXT DEFAULT 'vapi',
            telephony_number TEXT DEFAULT '',
            vapi_phone_id TEXT DEFAULT '',
            vapi_assistant_id TEXT DEFAULT '',
            telegram_bot_token TEXT DEFAULT '',
            telegram_chat_id TEXT DEFAULT '',
            twitter_api_key TEXT DEFAULT '',
            twitter_bearer_token TEXT DEFAULT '',
            linkedin_client_id TEXT DEFAULT '',
            linkedin_access_token TEXT DEFAULT '',
            tiktok_client_key TEXT DEFAULT '',
            tiktok_access_token TEXT DEFAULT '',
            webhook_secret TEXT DEFAULT '',
            updated_at TEXT NOT NULL,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
    """)

    # Dynamic migrations for omnichannel social channels (SQLite fallback)
    for col in [
        "telegram_bot_token", "telegram_chat_id", "twitter_api_key",
        "twitter_bearer_token", "linkedin_client_id", "linkedin_access_token",
        "tiktok_client_key", "tiktok_access_token"
    ]:
        try:
            db.execute(f"ALTER TABLE tenant_integrations ADD COLUMN {col} TEXT DEFAULT ''")
        except Exception:
            pass

    # Seed Default Salon if not exists
    db.execute("SELECT COUNT(*) as count FROM tenants WHERE id = ?", (DEFAULT_TENANT_ID,))
    res = db.fetchone()
    if res and res.get("count", 0) == 0:
        now = datetime.now().isoformat()
        db.execute("""
            INSERT OR IGNORE INTO tenants (id, name, phone_number, address, currency, created_at)
            VALUES (?, 'Luxe Hair & Wellness Salon', '+16175550100', '450 Newbury Street, Boston', 'USD', ?)
        """, (DEFAULT_TENANT_ID, now))

        default_services = [
            ("Womens Haircut", 45, 75),
            ("Mens Cut", 30, 45),
            ("Balayage", 150, 180),
            ("Full Highlights", 120, 160),
            ("Keratin Treatment", 120, 220),
            ("Mani Pedi", 60, 65)
        ]
        for s_name, dur, pr in default_services:
            s_id = f"{DEFAULT_TENANT_ID}_{s_name.replace(' ', '_').lower()}"
            db.execute("""
                INSERT OR IGNORE INTO services (id, tenant_id, name, duration_minutes, price)
                VALUES (?, ?, ?, ?, ?)
            """, (s_id, DEFAULT_TENANT_ID, s_name, dur, pr))

        default_stylists = ["Elena", "Marcus", "Chloe"]
        for st_name in default_stylists:
            st_id = f"{DEFAULT_TENANT_ID}_{st_name.lower()}"
            db.execute("""
                INSERT OR IGNORE INTO stylists (id, tenant_id, name, active)
                VALUES (?, ?, ?, 1)
            """, (st_id, DEFAULT_TENANT_ID, st_name))

    excel_path = get_excel_path()
    try:
        get_or_create_workbook(excel_path)
    except Exception as e:
        logger.debug(f"Excel workbook init bypassed: {e}")


# --- Multi-Tenant Query & Mutation Functions ---

def get_tenant_by_inbound_phone(phone: str) -> Dict[str, Any]:
    """Finds tenant by dialed inbound phone number. Falls back to default if unmatched."""
    init_db()
    clean = "".join(filter(str.isdigit, phone))[-10:] if phone else ""
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenants WHERE phone_number LIKE ? LIMIT 1", (f"%{clean}%",))
        row = db.fetchone()
        if row:
            return row
    return get_tenant(DEFAULT_TENANT_ID)


def get_tenant(tenant_id: str) -> Dict[str, Any]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenants WHERE id = ? LIMIT 1", (tenant_id,))
        row = db.fetchone()
        if row:
            return row
    return {
        "id": DEFAULT_TENANT_ID,
        "name": "Luxe Hair & Wellness Salon",
        "phone_number": "+16175550100",
        "address": "450 Newbury Street, Boston",
        "currency": "USD"
    }


def get_all_tenants() -> List[Dict[str, Any]]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenants ORDER BY created_at DESC")
        return db.fetchall()


def create_tenant(
    tenant_id: str,
    name: str,
    phone: str,
    address: str, 
    services: List[Tuple[str, int, int]],
    stylists: List[str]
) -> Dict[str, Any]:
    init_db()
    now = datetime.now().isoformat()
    with DBConnectionContext() as db:
        if db.is_pg:
            db.execute("""
                INSERT INTO tenants (id, name, phone_number, address, currency, created_at)
                VALUES (?, ?, ?, ?, 'USD', ?)
                ON CONFLICT (id) DO UPDATE SET 
                    name = EXCLUDED.name, 
                    phone_number = EXCLUDED.phone_number, 
                    address = EXCLUDED.address
            """, (tenant_id, name, phone, address, now))

            for s_name, dur, pr in services:
                s_id = f"{tenant_id}_{s_name.replace(' ', '_').lower()}"
                db.execute("""
                    INSERT INTO services (id, tenant_id, name, duration_minutes, price)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (id) DO UPDATE SET duration_minutes = EXCLUDED.duration_minutes, price = EXCLUDED.price
                """, (s_id, tenant_id, s_name, dur, pr))

            for st_name in stylists:
                st_id = f"{tenant_id}_{st_name.lower()}"
                db.execute("""
                    INSERT INTO stylists (id, tenant_id, name, active)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT (id) DO UPDATE SET active = 1
                """, (st_id, tenant_id, st_name))
        else:
            db.execute("""
                INSERT OR REPLACE INTO tenants (id, name, phone_number, address, currency, created_at)
                VALUES (?, ?, ?, ?, 'USD', ?)
            """, (tenant_id, name, phone, address, now))

            for s_name, dur, pr in services:
                s_id = f"{tenant_id}_{s_name.replace(' ', '_').lower()}"
                db.execute("""
                    INSERT OR REPLACE INTO services (id, tenant_id, name, duration_minutes, price)
                    VALUES (?, ?, ?, ?, ?)
                """, (s_id, tenant_id, s_name, dur, pr))

            for st_name in stylists:
                st_id = f"{tenant_id}_{st_name.lower()}"
                db.execute("""
                    INSERT OR REPLACE INTO stylists (id, tenant_id, name, active)
                    VALUES (?, ?, ?, 1)
                """, (st_id, tenant_id, st_name))

    return get_tenant(tenant_id)


def get_tenant_services(tenant_id: str) -> List[Dict[str, Any]]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM services WHERE tenant_id = ?", (tenant_id,))
        return db.fetchall()


def get_tenant_stylists(tenant_id: str) -> List[str]:
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT name FROM stylists WHERE tenant_id = ? AND active = 1", (tenant_id,))
        rows = db.fetchall()
        return [r["name"] for r in rows] if rows else ["Elena", "Marcus", "Chloe"]


# --- Availability & Booking Engine ---

def check_slots_availability(
    target_date: str,
    service_name: str,
    preferred_stylist: str = "any",
    tenant_id: str = DEFAULT_TENANT_ID
) -> List[str]:
    init_db()
    with DBConnectionContext() as db:
        # Get service duration
        db.execute("SELECT duration_minutes FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
        srv = db.fetchone()
        duration = srv["duration_minutes"] if srv else 45

        # Query active appointments for target_date using prefix matching
        date_prefix = f"{target_date}%"
        db.execute("""
            SELECT stylist_name, start_time, end_time 
            FROM appointments 
            WHERE tenant_id = ? AND start_time LIKE ? AND status = 'CONFIRMED'
        """, (tenant_id, date_prefix))
        booked_slots = db.fetchall()

    # Query active stylists for this tenant
    stylists_pool = get_tenant_stylists(tenant_id)
    stylists = stylists_pool if preferred_stylist.lower() in ("any", "") else [preferred_stylist]

    available_times = []
    candidate_hours = [9, 10, 11, 13, 14, 15, 16]
    for hour in candidate_hours:
        for minute in [0, 30]:
            candidate_start = datetime.strptime(f"{target_date} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
            candidate_end = candidate_start + timedelta(minutes=duration)

            if candidate_end.hour > 18 or (candidate_end.hour == 18 and candidate_end.minute > 0):
                continue

            for stylist in stylists:
                has_conflict = False
                for b in booked_slots:
                    if b["stylist_name"].lower() == stylist.lower():
                        b_start = datetime.fromisoformat(b["start_time"].replace("Z", ""))
                        b_end = datetime.fromisoformat(b["end_time"].replace("Z", ""))
                        if candidate_start < b_end and candidate_end > b_start:
                            has_conflict = True
                            break
                if not has_conflict:
                    slot_str = candidate_start.strftime("%I:%M %p")
                    if slot_str not in available_times:
                        available_times.append(slot_str)
                    break

    return available_times[:4]


def book_new_appointment(
    caller_name: str,
    caller_phone: str,
    service_name: str, 
    appointment_datetime: str,
    stylist_name: str = "Elena",
    tenant_id: str = DEFAULT_TENANT_ID,
    channel: str = "voice",
    accent: str = "red_american",
    notes: str = "",
    caller_email: str = ""
) -> Dict[str, Any]:
    init_db()
    if not tenant_id or tenant_id in ("default_salon", "default"):
        tenant_id = "salon"
    
    # Auto-resolve customer email if not provided explicitly
    if not caller_email:
        cust = get_customer_by_phone_or_email(phone=caller_phone)
        if cust and cust.get("email"):
            caller_email = cust["email"]

    dt_clean = appointment_datetime.replace("Z", "")
    start_dt = datetime.fromisoformat(dt_clean)

    with DBConnectionContext() as db:
        db.execute("SELECT duration_minutes, price FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
        srv_row = db.fetchone()
        duration = srv_row["duration_minutes"] if srv_row else 45
        price = srv_row["price"] if srv_row else 75
        end_dt = start_dt + timedelta(minutes=duration)

        db.execute("SELECT COUNT(*) as cnt FROM appointments")
        cnt_row = db.fetchone()
        total_count = (cnt_row["cnt"] if cnt_row else 0) + 101

        booking_id = f"LUXE-{start_dt.strftime('%m%d')}-{total_count}"
        now_str = datetime.now().isoformat()

        # Sync with Google Calendar if enabled
        gcal_event_id = ""
        if calendar_service:
            try:
                tenant_info = get_tenant(tenant_id)
                tenant_display = tenant_info.get("name", "Salon")
                gcal_res = calendar_service.create_event(
                    summary=f"{tenant_display}: {service_name} - {caller_name}",
                    start_time_iso=start_dt.isoformat(),
                    duration_minutes=duration,
                    description=f"Staff: {stylist_name}\nChannel: {channel}\nAccent: {accent}\nNotes: {notes}",
                    location=tenant_info.get("address", ""),
                    attendee_phone=caller_phone,
                    attendee_email=caller_email
                )
                gcal_event_id = gcal_res.get("id", "")
            except Exception as e:
                logger.warning(f"Google Calendar event creation bypassed: {e}")

        db.execute("""
            INSERT INTO appointments (
                id, tenant_id, caller_name, caller_phone, service_name, stylist_name,
                start_time, end_time, status, created_at, whatsapp_24h_sent, call_1h_sent,
                google_calendar_event_id, channel, accent, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, 0, 0, ?, ?, ?, ?)
        """, (booking_id, tenant_id, caller_name, caller_phone, service_name, stylist_name, 
              start_dt.isoformat(), end_dt.isoformat(), now_str, gcal_event_id, channel, accent, notes))

    booking_record = {
        "booking_id": booking_id,
        "tenant_id": tenant_id,
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "service_name": service_name,
        "stylist_name": stylist_name,
        "start_time": start_dt.strftime("%Y-%m-%d %H:%M"),
        "duration_minutes": duration,
        "price": price,
        "status": "CONFIRMED",
        "google_calendar_event_id": gcal_event_id,
        "channel": channel,
        "accent": accent
    }

    # 1. Sync into Local/Serverless Excel Workbook
    try:
        excel_path = get_excel_path()
        append_appointment_to_excel(booking_record, filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel record append bypassed: {e}")

    # 2. Sync to Live Google Sheet
    try:
        sync_appointment_to_google_sheets(booking_record, tenant_id=tenant_id)
    except Exception as e:
        logger.error(f"❌ Google sheets sync failed: {e}", exc_info=True)

    # 3. Automatic Email Confirmation to Customer (Signup Email or Stated Email)
    if caller_email and "@" in caller_email:
        try:
            from core.notifications import notification_dispatcher
            notification_dispatcher.send_email(
                to_email=caller_email,
                subject=f"✨ Luxe Saloon & Spa Booking Confirmation (#{booking_id})",
                booking_data=booking_record
            )
            logger.info(f"✅ Dispatched automated confirmation email to {caller_email}")
        except Exception as mail_err:
            logger.warning(f"Email dispatch warning: {mail_err}")

    return {
        "booking_id": booking_id,
        "tenant_id": tenant_id,
        "caller_name": caller_name,
        "caller_phone": caller_phone,
        "service_name": service_name,
        "stylist_name": stylist_name,
        "start_time": start_dt.strftime("%A, %b %d at %I:%M %p"),
        "price": f"${price}",
        "google_calendar_event_id": gcal_event_id
    }


def lookup_by_phone(caller_phone: str, tenant_id: str = DEFAULT_TENANT_ID) -> Optional[Dict[str, Any]]:
    init_db()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]
    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
            ORDER BY start_time DESC LIMIT 1
        """, (tenant_id, f"%{phone_clean}%"))
        row = db.fetchone()
        if row:
            start_dt = datetime.fromisoformat(row["start_time"].replace("Z", ""))
            return {
                "booking_id": row["id"],
                "caller_name": row["caller_name"],
                "caller_phone": row["caller_phone"],
                "service_name": row["service_name"],
                "stylist_name": row["stylist_name"],
                "start_time": start_dt.strftime("%A, %b %d at %I:%M %p"),
                "start_time_iso": row["start_time"],
                "google_calendar_event_id": row.get("google_calendar_event_id", "")
            }
    return None


def lookup_by_booking_id(booking_id: str) -> Optional[Dict[str, Any]]:
    """Look up appointment details by unique booking reference (e.g. LUXE-1110-113)."""
    init_db()
    clean_id = booking_id.strip()
    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE id = ? OR id = ?
            LIMIT 1
        """, (clean_id, clean_id.upper()))
        row = db.fetchone()
        if row:
            start_dt = datetime.fromisoformat(row["start_time"].replace("Z", ""))
            return {
                "booking_id": row["id"],
                "tenant_id": row.get("tenant_id", "salon"),
                "caller_name": row["caller_name"],
                "caller_phone": row["caller_phone"],
                "service_name": row["service_name"],
                "stylist_name": row["stylist_name"],
                "start_time": start_dt.strftime("%A, %b %d at %I:%M %p"),
                "start_time_iso": row["start_time"],
                "google_calendar_event_id": row.get("google_calendar_event_id", "")
            }
    return None



def reschedule_existing_appointment(
    caller_phone: str,
    new_datetime: str,
    booking_id: Optional[str] = None,
    new_stylist_name: Optional[str] = None,
    tenant_id: str = DEFAULT_TENANT_ID
) -> Optional[Dict[str, Any]]:
    init_db()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]

    with DBConnectionContext() as db:
        if booking_id:
            db.execute("SELECT * FROM appointments WHERE id = ? AND tenant_id = ? LIMIT 1", (booking_id, tenant_id))
        else:
            db.execute("""
                SELECT * FROM appointments 
                WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
                ORDER BY start_time DESC LIMIT 1
            """, (tenant_id, f"%{phone_clean}%"))
        row = db.fetchone()

        if not row:
            return None

        actual_booking_id = row["id"]
        service_name = row["service_name"]
        stylist = new_stylist_name or row["stylist_name"]
        gcal_event_id = row.get("google_calendar_event_id", "")

        dt_clean = new_datetime.replace("Z", "")
        new_start_dt = datetime.fromisoformat(dt_clean)

        db.execute("SELECT duration_minutes, price FROM services WHERE tenant_id = ? AND name = ?", (tenant_id, service_name))
        srv_row = db.fetchone()
        duration = srv_row["duration_minutes"] if srv_row else 45
        price = srv_row["price"] if srv_row else 75
        new_end_dt = new_start_dt + timedelta(minutes=duration)

        db.execute("""
            UPDATE appointments 
            SET start_time = ?, end_time = ?, stylist_name = ?, whatsapp_24h_sent = 0, call_1h_sent = 0
            WHERE id = ?
        """, (new_start_dt.isoformat(), new_end_dt.isoformat(), stylist, actual_booking_id))

    # Sync with Google Calendar if event exists
    if calendar_service and gcal_event_id:
        try:
            tenant_info = get_tenant(tenant_id)
            calendar_service.update_event(
                event_id=gcal_event_id,
                summary=f"{tenant_info.get('name', 'Salon')}: {service_name} - {row['caller_name']}",
                start_time_iso=new_start_dt.isoformat(),
                duration_minutes=duration,
                description=f"Rescheduled. Staff: {stylist}"
            )
        except Exception as e:
            logger.warning(f"Google Calendar update bypassed: {e}")

    try:
        excel_path = get_excel_path()
        update_excel_reminders(actual_booking_id, status="CONFIRMED (RESCHEDULED)", filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel update bypassed: {e}")

    return {
        "booking_id": actual_booking_id,
        "caller_name": row["caller_name"],
        "caller_phone": row["caller_phone"],
        "service_name": service_name,
        "stylist_name": stylist,
        "start_time": new_start_dt.strftime("%A, %b %d at %I:%M %p"),
        "price": f"${price}",
        "google_calendar_event_id": gcal_event_id
    }


def cancel_existing_appointment(
    caller_phone: str,
    booking_id: Optional[str] = None,
    tenant_id: str = DEFAULT_TENANT_ID
) -> bool:
    init_db()
    phone_clean = "".join(filter(str.isdigit, caller_phone))[-7:]

    with DBConnectionContext() as db:
        if booking_id:
            db.execute("SELECT id, google_calendar_event_id FROM appointments WHERE id = ? AND tenant_id = ? LIMIT 1", (booking_id, tenant_id))
        else:
            db.execute("""
                SELECT id, google_calendar_event_id FROM appointments 
                WHERE tenant_id = ? AND caller_phone LIKE ? AND status = 'CONFIRMED'
                ORDER BY start_time DESC LIMIT 1
            """, (tenant_id, f"%{phone_clean}%"))
        row = db.fetchone()

        if not row:
            return False

        target_id = row["id"]
        gcal_event_id = row.get("google_calendar_event_id", "")

        db.execute("UPDATE appointments SET status = 'CANCELLED' WHERE id = ?", (target_id,))
        updated = db.rowcount > 0

    if updated:
        if calendar_service and gcal_event_id:
            try:
                calendar_service.delete_event(gcal_event_id)
            except Exception as e:
                logger.warning(f"Google Calendar delete bypassed: {e}")

        try:
            excel_path = get_excel_path()
            update_excel_reminders(target_id, status="CANCELLED", filepath=excel_path)
        except Exception as e:
            logger.debug(f"Excel cancel bypassed: {e}")

    return updated


def list_all_appointments(tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Universal appointments query across all or specific tenant."""
    init_db()
    with DBConnectionContext() as db:
        if tenant_id:
            db.execute("SELECT * FROM appointments WHERE tenant_id = ? ORDER BY start_time DESC", (tenant_id,))
        else:
            db.execute("SELECT * FROM appointments ORDER BY start_time DESC")
        return db.fetchall()


def get_pending_24h_reminders() -> List[Dict[str, Any]]:
    init_db()
    now = datetime.now()
    window_start = (now + timedelta(hours=23)).isoformat()
    window_end = (now + timedelta(hours=25)).isoformat()

    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE status = 'CONFIRMED' 
              AND whatsapp_24h_sent = 0
              AND start_time BETWEEN ? AND ?
        """, (window_start, window_end))
        return db.fetchall()


def mark_24h_reminder_sent(booking_id: str):
    init_db()
    with DBConnectionContext() as db:
        db.execute("UPDATE appointments SET whatsapp_24h_sent = 1 WHERE id = ?", (booking_id,))
    try:
        excel_path = get_excel_path()
        update_excel_reminders(booking_id, whatsapp_24h="SENT", filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel reminder bypassed: {e}")


def get_pending_1h_call_reminders() -> List[Dict[str, Any]]:
    init_db()
    now = datetime.now()
    window_start = (now + timedelta(minutes=50)).isoformat()
    window_end = (now + timedelta(minutes=70)).isoformat()

    with DBConnectionContext() as db:
        db.execute("""
            SELECT * FROM appointments 
            WHERE status = 'CONFIRMED' 
              AND call_1h_sent = 0
              AND start_time BETWEEN ? AND ?
        """, (window_start, window_end))
        return db.fetchall()


def mark_1h_call_sent(booking_id: str):
    init_db()
    with DBConnectionContext() as db:
        db.execute("UPDATE appointments SET call_1h_sent = 1 WHERE id = ?", (booking_id,))
    try:
        excel_path = get_excel_path()
        update_excel_reminders(booking_id, call_1h="CALLED", filepath=excel_path)
    except Exception as e:
        logger.debug(f"Excel reminder bypassed: {e}")


# --- User Authentication & Tenant Integrations Helpers ---

def hash_password(password: str) -> str:
    """Hashes a password with salt using SHA-256."""
    salt = secrets.token_hex(8)
    h = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a plain password against stored salt:hash."""
    try:
        salt, expected_hash = stored_hash.split(":")
        calc_hash = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
        return secrets.compare_digest(calc_hash, expected_hash)
    except Exception:
        return False


def create_user(
    email: str,
    password: str,
    company_name: str,
    tenant_id: str,
    plan: str = "growth"
) -> Dict[str, Any]:
    """Registers a new customer account bound to a tenant workspace."""
    init_db()
    user_id = f"usr_{secrets.token_hex(6)}"
    p_hash = hash_password(password)
    now = datetime.now().isoformat()

    with DBConnectionContext() as db:
        db.execute("""
            INSERT INTO users (id, email, password_hash, company_name, tenant_id, plan, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, email.lower().strip(), p_hash, company_name, tenant_id, plan, now))

    return {
        "id": user_id,
        "email": email.lower().strip(),
        "company_name": company_name,
        "tenant_id": tenant_id,
        "plan": plan,
        "created_at": now
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Look up customer account by email."""
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email.lower().strip(),))
        return db.fetchone()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Look up customer account by user id."""
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM users WHERE id = ? LIMIT 1", (user_id,))
        return db.fetchone()


def get_or_create_clerk_user(
    clerk_user_id: str,
    email: str,
    company_name: str = "My Business",
    plan: str = "growth"
) -> Dict[str, Any]:
    """Retrieves an existing user by email or provisions a new user and tenant workspace for a Clerk user."""
    init_db()
    clean_email = email.lower().strip()
    existing = get_user_by_email(clean_email)
    if existing:
        return existing

    # Generate safe tenant ID slug from email
    slug = clean_email.split("@")[0].replace(".", "_").replace("+", "_")
    tenant_id = f"tenant_{slug}"
    
    tenant = get_tenant(tenant_id)
    if not tenant:
        from core.blueprint.tenant_manager import tenant_registry
        try:
            tenant_registry.onboard_custom_tenant(
                tenant_id=tenant_id,
                business_name=company_name or f"{slug.replace('_', ' ').title()} Salon",
                vertical="salon",
                phone_number="+18005550199",
                address="450 Newbury Street, Boston, MA",
                primary_accent="general_american"
            )
        except Exception:
            create_tenant(
                tenant_id=tenant_id,
                name=company_name or f"{slug.replace('_', ' ').title()} Salon",
                phone="+18005550199",
                address="450 Newbury Street, Boston, MA",
                services=[("Womens Haircut", 45, 75), ("Mens Cut", 30, 45)],
                stylists=["Elena", "Marcus"]
            )

    user = create_user(
        email=clean_email,
        password=secrets.token_urlsafe(16),
        company_name=company_name or f"{slug.replace('_', ' ').title()} Salon",
        tenant_id=tenant_id,
        plan=plan
    )
    return user


def save_tenant_integrations(
    tenant_id: str,
    whatsapp_phone_number_id: str = "",
    whatsapp_business_account_id: str = "",
    meta_page_id: str = "",
    instagram_account_id: str = "",
    google_calendar_id: str = "primary",
    telephony_provider: str = "vapi",
    telephony_number: str = "",
    vapi_phone_id: str = "",
    vapi_assistant_id: str = "",
    telegram_bot_token: str = "",
    telegram_chat_id: str = "",
    twitter_api_key: str = "",
    twitter_bearer_token: str = "",
    linkedin_client_id: str = "",
    linkedin_access_token: str = "",
    tiktok_client_key: str = "",
    tiktok_access_token: str = ""
) -> Dict[str, Any]:
    """Saves or updates connected WhatsApp, Meta, Instagram, Telegram, Twitter, LinkedIn, TikTok, and telephony parameters."""
    init_db()
    now = datetime.now().isoformat()
    secret = secrets.token_hex(12)

    with DBConnectionContext() as db:
        if db.is_pg:
            db.execute("""
                INSERT INTO tenant_integrations (
                    tenant_id, whatsapp_phone_number_id, whatsapp_business_account_id,
                    meta_page_id, instagram_account_id, google_calendar_id,
                    telephony_provider, telephony_number, vapi_phone_id, vapi_assistant_id,
                    telegram_bot_token, telegram_chat_id,
                    twitter_api_key, twitter_bearer_token,
                    linkedin_client_id, linkedin_access_token,
                    tiktok_client_key, tiktok_access_token,
                    webhook_secret, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (tenant_id) DO UPDATE SET
                    whatsapp_phone_number_id = EXCLUDED.whatsapp_phone_number_id,
                    whatsapp_business_account_id = EXCLUDED.whatsapp_business_account_id,
                    meta_page_id = EXCLUDED.meta_page_id,
                    instagram_account_id = EXCLUDED.instagram_account_id,
                    google_calendar_id = EXCLUDED.google_calendar_id,
                    telephony_provider = EXCLUDED.telephony_provider,
                    telephony_number = EXCLUDED.telephony_number,
                    vapi_phone_id = EXCLUDED.vapi_phone_id,
                    vapi_assistant_id = EXCLUDED.vapi_assistant_id,
                    telegram_bot_token = EXCLUDED.telegram_bot_token,
                    telegram_chat_id = EXCLUDED.telegram_chat_id,
                    twitter_api_key = EXCLUDED.twitter_api_key,
                    twitter_bearer_token = EXCLUDED.twitter_bearer_token,
                    linkedin_client_id = EXCLUDED.linkedin_client_id,
                    linkedin_access_token = EXCLUDED.linkedin_access_token,
                    tiktok_client_key = EXCLUDED.tiktok_client_key,
                    tiktok_access_token = EXCLUDED.tiktok_access_token,
                    webhook_secret = EXCLUDED.webhook_secret,
                    updated_at = EXCLUDED.updated_at
            """, (
                tenant_id, whatsapp_phone_number_id, whatsapp_business_account_id,
                meta_page_id, instagram_account_id, google_calendar_id,
                telephony_provider, telephony_number, vapi_phone_id, vapi_assistant_id,
                telegram_bot_token, telegram_chat_id,
                twitter_api_key, twitter_bearer_token,
                linkedin_client_id, linkedin_access_token,
                tiktok_client_key, tiktok_access_token,
                secret, now
            ))
        else:
            db.execute("""
                INSERT OR REPLACE INTO tenant_integrations (
                    tenant_id, whatsapp_phone_number_id, whatsapp_business_account_id,
                    meta_page_id, instagram_account_id, google_calendar_id,
                    telephony_provider, telephony_number, vapi_phone_id, vapi_assistant_id,
                    telegram_bot_token, telegram_chat_id,
                    twitter_api_key, twitter_bearer_token,
                    linkedin_client_id, linkedin_access_token,
                    tiktok_client_key, tiktok_access_token,
                    webhook_secret, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tenant_id, whatsapp_phone_number_id, whatsapp_business_account_id,
                meta_page_id, instagram_account_id, google_calendar_id,
                telephony_provider, telephony_number, vapi_phone_id, vapi_assistant_id,
                telegram_bot_token, telegram_chat_id,
                twitter_api_key, twitter_bearer_token,
                linkedin_client_id, linkedin_access_token,
                tiktok_client_key, tiktok_access_token,
                secret, now
            ))

    return get_tenant_integrations(tenant_id)


def get_tenant_integrations(tenant_id: str) -> Dict[str, Any]:
    """Retrieves omnichannel integration credentials for a tenant."""
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT * FROM tenant_integrations WHERE tenant_id = ? LIMIT 1", (tenant_id,))
        row = db.fetchone()
        if row:
            return row
    return {
        "tenant_id": tenant_id,
        "whatsapp_phone_number_id": "",
        "whatsapp_business_account_id": "",
        "meta_page_id": "",
        "instagram_account_id": "",
        "google_calendar_id": "primary",
        "telephony_provider": "vapi",
        "telephony_number": "+18005550199",
        "vapi_phone_id": "",
        "vapi_assistant_id": "",
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "twitter_api_key": "",
        "twitter_bearer_token": "",
        "linkedin_client_id": "",
        "linkedin_access_token": "",
        "tiktok_client_key": "",
        "tiktok_access_token": ""
    }


def lookup_tenant_by_integration_id(field_name: str, field_value: str) -> str:
    """
    Dynamically maps an inbound social ID (WhatsApp phone ID, Meta Page ID, Instagram ID)
    to its corresponding business tenant_id for multi-tenant webhook routing.
    """
    if not field_value:
        return "salon"

    clean_val = str(field_value).strip()
    valid_fields = {
        "whatsapp_phone_number_id",
        "meta_page_id",
        "instagram_account_id",
        "threads_user_id"
    }
    if field_name not in valid_fields:
        return "salon"

    init_db()
    with DBConnectionContext() as db:
        query = f"SELECT tenant_id FROM tenant_integrations WHERE {field_name} = ? LIMIT 1"
        db.execute(query, (clean_val,))
        row = db.fetchone()
        if row and row.get("tenant_id"):
            return row["tenant_id"]

    # Fallback to default env mappings
    if field_name == "whatsapp_phone_number_id" and clean_val == os.getenv("WHATSAPP_PHONE_NUMBER_ID"):
        return "salon"
    if field_name == "meta_page_id" and clean_val in (os.getenv("META_PAGE_ID"), "61596010512285", "1429742393555082"):
        return "salon"
    if field_name == "instagram_account_id" and clean_val == os.getenv("INSTAGRAM_ACCOUNT_ID"):
        return "salon"

    return "salon"


def update_tenant_plan(tenant_id: str, new_plan: str) -> bool:
    """Updates customer subscription plan (starter, growth, enterprise)."""
    init_db()
    with DBConnectionContext() as db:
        db.execute("UPDATE users SET plan = ? WHERE tenant_id = ?", (new_plan, tenant_id))
        return db.rowcount > 0


def save_customer_profile(
    email: str = "",
    phone: str = "",
    full_name: str = "",
    clerk_id: str = "",
    tenant_id: str = "salon"
) -> Dict[str, Any]:
    """Saves or updates customer email, phone, and name into Neon PostgreSQL or SQLite."""
    init_db()
    clean_email = email.lower().strip() if email else ""
    clean_phone = phone.strip() if phone else ""
    now = datetime.now().isoformat()

    with DBConnectionContext() as db:
        existing = None
        if clerk_id:
            db.execute("SELECT * FROM customers WHERE clerk_id = ? LIMIT 1", (clerk_id,))
            existing = db.fetchone()
        if not existing and clean_email:
            db.execute("SELECT * FROM customers WHERE email = ? LIMIT 1", (clean_email,))
            existing = db.fetchone()
        if not existing and clean_phone:
            db.execute("SELECT * FROM customers WHERE phone = ? LIMIT 1", (clean_phone,))
            existing = db.fetchone()

        if existing:
            cust_id = existing["id"]
            db.execute(
                "UPDATE customers SET email = ?, phone = ?, full_name = ?, clerk_id = ? WHERE id = ?",
                (
                    clean_email or existing.get("email", ""),
                    clean_phone or existing.get("phone", ""),
                    full_name or existing.get("full_name", ""),
                    clerk_id or existing.get("clerk_id", ""),
                    cust_id
                )
            )
        else:
            cust_id = f"cust_{secrets.token_hex(8)}"
            db.execute(
                "INSERT INTO customers (id, clerk_id, email, phone, full_name, tenant_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cust_id, clerk_id, clean_email, clean_phone, full_name, tenant_id, now)
            )

    return {
        "id": cust_id,
        "clerk_id": clerk_id,
        "email": clean_email,
        "phone": clean_phone,
        "full_name": full_name,
        "tenant_id": tenant_id
    }


def get_customer_by_phone_or_email(phone: str = "", email: str = "") -> Optional[Dict[str, Any]]:
    """Look up customer by phone or email address with suffix matching."""
    init_db()
    with DBConnectionContext() as db:
        if phone:
            clean_digits = "".join(filter(str.isdigit, phone))[-10:]
            if clean_digits:
                db.execute("SELECT * FROM customers WHERE phone LIKE ? AND email IS NOT NULL AND email != '' LIMIT 1", (f"%{clean_digits}%",))
                row = db.fetchone()
                if row:
                    return row
            db.execute("SELECT * FROM customers WHERE phone = ? LIMIT 1", (phone.strip(),))
            row = db.fetchone()
            if row:
                return row
        if email:
            db.execute("SELECT * FROM customers WHERE email = ? LIMIT 1", (email.lower().strip(),))
            row = db.fetchone()
            if row:
                return row
    return None


def get_all_customer_phones(tenant_id: str = "salon") -> List[str]:
    """Retrieve distinct customer phone numbers for marketing broadcasts."""
    init_db()
    with DBConnectionContext() as db:
        db.execute("SELECT DISTINCT phone FROM customers WHERE phone IS NOT NULL AND phone != '' AND tenant_id = ?", (tenant_id,))
        rows = db.fetchall()
        return [r["phone"] for r in rows if r.get("phone")]

