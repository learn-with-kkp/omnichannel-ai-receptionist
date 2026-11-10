# 📅 Calendar Sync Adapter (`calendar-sync-adapter`)

[![PyPI version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/KishorKumarParoi/omnichannel-voice-chat-ai-receptionist)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Two-way enterprise scheduling and calendar synchronization engine for AI receptionists. Computes real-time free/busy slots, prevents double bookings, and manages event lifecycles.

## 🚀 Features

- **Free/Busy Availability Calculation**: Live Google Calendar `freeBusy.query` with multi-specialist slot alignment.
- **Service Duration Buffers**: Dynamic block scheduling (30 min - 180 min) with setup/cleanup buffer support.
- **Full Event Lifecycle**: Seamless `create`, `reschedule`, `cancel`, and reminder dispatching.
- **Zero Double-Bookings**: Atomic slot reservation locks with transactional safety.

## 💻 Usage

```python
from calendar_sync_adapter import CalendarSyncService

cal = CalendarSyncService()

# Query available slots for tomorrow
slots = cal.query_live_availability(target_date="2026-11-08", duration_minutes=45)
print("Available Booking Slots:", slots)
```
