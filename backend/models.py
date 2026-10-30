from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ServiceType(str, Enum):
    WOMENS_HAIRCUT = "Womens Haircut"
    MENS_CUT = "Mens Cut"
    BALAYAGE = "Balayage"
    FULL_HIGHLIGHTS = "Full Highlights"
    KERATIN = "Keratin Treatment"
    MANI_PEDI = "Mani Pedi"

class StylistName(str, Enum):
    ELENA = "Elena"
    MARCUS = "Marcus"
    CHLOE = "Chloe"
    ANY = "any"

# Vapi Inbound Tool Call Models
class ToolFunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ToolCallItem(BaseModel):
    id: str
    type: str = "function"
    function: ToolFunctionCall

class VapiMessage(BaseModel):
    type: Optional[str] = None
    toolCalls: Optional[List[ToolCallItem]] = None
    call: Optional[Dict[str, Any]] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recordingUrl: Optional[str] = None

class VapiWebhookPayload(BaseModel):
    message: VapiMessage

# Outbound Vapi Tool Response
class ToolResult(BaseModel):
    toolCallId: str
    result: str

class VapiToolResponse(BaseModel):
    results: List[ToolResult]

# Salon Domain Models
class AppointmentCreate(BaseModel):
    caller_name: str
    caller_phone: str
    service_name: str
    stylist_name: Optional[str] = "Elena"
    appointment_datetime: str
    special_notes: Optional[str] = ""

class AppointmentRecord(BaseModel):
    id: str
    caller_name: str
    caller_phone: str
    service_name: str
    stylist_name: str
    start_time: str
    end_time: str
    status: str = "CONFIRMED"
    created_at: str

