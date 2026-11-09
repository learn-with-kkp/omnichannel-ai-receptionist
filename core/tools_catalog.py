"""
Categorized Tool Manifest & Schema Registry.
Organizes all conversational AI voice tools into enterprise operational categories:
1. Scheduling & Calendar Operations
2. Omnichannel Communications & Notifications
3. Knowledge Base & Salon Intelligence
4. Team Routing, Handoffs & Escalation
5. Synchronization & Data Lakehouse Integrations
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    category: str
    description: str
    vapi_type: str = "function"
    execution_timeout_ms: int = 4000
    cache_ttl_seconds: int = 0
    idempotent: bool = False
    parameters: Dict[str, Any]
    required: List[str]


CATEGORIZED_TOOLS_CATALOG: Dict[str, Any] = {
    "version": "2.1.0",
    "categories": [
        {
            "id": "scheduling_and_calendar",
            "name": "Scheduling & Calendar Operations",
            "description": "Real-time Google Calendar slot discovery, appointment booking, rescheduling, and cancellation with sub-500ms latency.",
            "tools": [
                {
                    "name": "check_availability",
                    "description": "Checks real-time open appointment slots against Google Calendar and stylist schedules.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 3000,
                    "cache_ttl_seconds": 30,
                    "idempotent": True,
                    "parameters": {
                        "service_name": {
                            "type": "string",
                            "description": "Selected salon service (e.g. Signature Balayage, Precision Cut, Deluxe HydraFacial)."
                        },
                        "preferred_datetime": {
                            "type": "string",
                            "description": "ISO 8601 requested date/time (e.g. 2026-11-10T14:00:00)."
                        },
                        "stylist_name": {
                            "type": "string",
                            "description": "Stylist preference (Marcus Vance, Sofia Alston, Elena Rostova, Chloe Laurent, or Any)."
                        }
                    },
                    "required": ["service_name"]
                },
                {
                    "name": "book_appointment",
                    "description": "Commits an appointment directly to Google Calendar, Neon PostgreSQL database, live Google Sheets, and dispatches instant luxury email and WhatsApp confirmations with dual 24h and 1h reminders.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 4000,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "caller_name": {
                            "type": "string",
                            "description": "Full name of the guest."
                        },
                        "caller_phone": {
                            "type": "string",
                            "description": "Caller mobile/WhatsApp phone number in standard international format (e.g. +16175550199 or national format)."
                        },
                        "caller_email": {
                            "type": "string",
                            "description": "Guest email address to receive immediate luxury HTML confirmation, 1-click Google Calendar add link, and .ics calendar invite."
                        },
                        "service_name": {
                            "type": "string",
                            "description": "Selected salon service."
                        },
                        "stylist_name": {
                            "type": "string",
                            "description": "Assigned stylist or aesthetician."
                        },
                        "appointment_datetime": {
                            "type": "string",
                            "description": "ISO 8601 formatted datetime string (e.g. 2026-11-10T14:00:00)."
                        }
                    },
                    "required": ["caller_name", "caller_phone", "caller_email", "service_name", "appointment_datetime"]
                },
                {
                    "name": "lookup_appointment",
                    "description": "Looks up existing appointment details for a client using their phone number or booking reference.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 2500,
                    "cache_ttl_seconds": 15,
                    "idempotent": True,
                    "parameters": {
                        "booking_id": {
                            "type": "string",
                            "description": "Reservation code (e.g. LUXE-1110-101)."
                        },
                        "caller_phone": {
                            "type": "string",
                            "description": "Guest phone number to look up existing appointments."
                        }
                    },
                    "required": []
                },
                {
                    "name": "reschedule_appointment",
                    "description": "Reschedules an existing confirmed appointment to a new date and time.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 4000,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "booking_id": {
                            "type": "string",
                            "description": "Existing booking ID or confirmation reference."
                        },
                        "new_datetime": {
                            "type": "string",
                            "description": "New target appointment date and time in ISO 8601 format."
                        },
                        "caller_phone": {
                            "type": "string",
                            "description": "Caller phone number for verification."
                        }
                    },
                    "required": ["new_datetime"]
                },
                {
                    "name": "cancel_appointment",
                    "description": "Cancels an existing appointment, releases the Google Calendar slot, and updates database & sheets.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 3500,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "booking_id": {
                            "type": "string",
                            "description": "Booking reference ID to cancel."
                        },
                        "reason": {
                            "type": "string",
                            "description": "Cancellation reason provided by the client."
                        },
                        "caller_phone": {
                            "type": "string",
                            "description": "Phone number of caller."
                        }
                    },
                    "required": []
                }
            ]
        },
        {
            "id": "omnichannel_communications",
            "name": "Omnichannel Messaging & Notifications",
            "description": "Automated SMS, WhatsApp luxury templates, and operational staff Slack alerts.",
            "tools": [
                {
                    "name": "send_text",
                    "description": "Sends an instant SMS or WhatsApp confirmation message with booking links or directions to the caller's phone.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 3000,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "message_text": {
                            "type": "string",
                            "description": "Text message content to send."
                        },
                        "recipient_phone": {
                            "type": "string",
                            "description": "Target mobile number in E.164 format."
                        }
                    },
                    "required": ["message_text"]
                },
                {
                    "name": "slack_notification",
                    "description": "Dispatches an urgent alert to the salon staff Slack channel.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 2500,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "message": {
                            "type": "string",
                            "description": "Urgent alert message text."
                        },
                        "channel": {
                            "type": "string",
                            "description": "Slack channel (e.g. #appointments, #escalations)."
                        }
                    },
                    "required": ["message"]
                }
            ]
        },
        {
            "id": "knowledge_and_intelligence",
            "name": "Knowledge Base & Salon Intelligence",
            "description": "Fast semantic FAQ lookup over treatments, pricing, parking, directions, and salon policies.",
            "tools": [
                {
                    "name": "query_knowledge_base",
                    "description": "Queries the salon knowledge base for treatments, pricing, parking, directions, and policies.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 2500,
                    "cache_ttl_seconds": 300,
                    "idempotent": True,
                    "parameters": {
                        "query": {
                            "type": "string",
                            "description": "Caller question regarding services, stylists, pricing, location, or salon policies."
                        }
                    },
                    "required": ["query"]
                }
            ]
        },
        {
            "id": "team_routing_and_escalations",
            "name": "Team Routing, Handoffs & Escalation",
            "description": "Intelligent squad transfers to Marcus, Kishor, Tasnim, Raiyan, manager escalation, and call closure.",
            "tools": [
                {
                    "name": "transferCall",
                    "description": "Transfers the call to another specialist assistant in the Luxe Squad.",
                    "vapi_type": "transferCall",
                    "execution_timeout_ms": 2000,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "destination": {
                            "type": "string",
                            "description": "Target squad member: Marcus, Sophia, Kishor, Tasnim, or Raiyan."
                        }
                    },
                    "required": ["destination"]
                },
                {
                    "name": "transfer_to_manager",
                    "description": "Warmly escalates and transfers the caller to our human salon manager or front desk supervisor for complex requests, VIP disputes, custom requests, or when explicitly requested.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 3000,
                    "cache_ttl_seconds": 0,
                    "idempotent": False,
                    "parameters": {
                        "reason": {
                            "type": "string",
                            "description": "Reason for human escalation."
                        },
                        "caller_name": {
                            "type": "string",
                            "description": "Name of the caller if provided."
                        },
                        "caller_phone": {
                            "type": "string",
                            "description": "Phone number of caller."
                        }
                    },
                    "required": ["reason"]
                },
                {
                    "name": "end_call",
                    "description": "Gracefully concludes the voice call with a polite salon sign-off.",
                    "vapi_type": "endCall",
                    "execution_timeout_ms": 1500,
                    "cache_ttl_seconds": 0,
                    "idempotent": True,
                    "parameters": {
                        "closing_message": {
                            "type": "string",
                            "description": "Polite farewell message to speak before hanging up."
                        }
                    },
                    "required": []
                },
                {
                    "name": "leave_voicemail",
                    "description": "Leaves a polite concierge voicemail if an outbound call goes to an answering machine.",
                    "vapi_type": "function",
                    "execution_timeout_ms": 2500,
                    "cache_ttl_seconds": 0,
                    "idempotent": True,
                    "parameters": {
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name for personalized voicemail."
                        },
                        "message": {
                            "type": "string",
                            "description": "Core voicemail message to deliver."
                        }
                    },
                    "required": ["message"]
                }
            ]
        }
    ]
}


def get_tools_by_category(category_id: str) -> List[Dict[str, Any]]:
    """Returns all tools belonging to a specific category."""
    for cat in CATEGORIZED_TOOLS_CATALOG["categories"]:
        if cat["id"] == category_id:
            return cat["tools"]
    return []


def get_all_tool_names() -> List[str]:
    """Returns a flat list of all registered tool names."""
    names = []
    for cat in CATEGORIZED_TOOLS_CATALOG["categories"]:
        for tool in cat["tools"]:
            names.append(tool["name"])
    return names
