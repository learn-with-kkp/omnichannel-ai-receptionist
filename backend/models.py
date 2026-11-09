import json
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
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
    arguments: Union[Dict[str, Any], str] = Field(default_factory=dict)

    @field_validator("arguments", mode="before")
    @classmethod
    def parse_arguments(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v or {}

class ToolCallItem(BaseModel):
    id: str
    type: str = "function"
    function: ToolFunctionCall

class VapiMessage(BaseModel):
    model_config = {"extra": "allow"}
    type: Optional[str] = None
    toolCalls: Optional[List[ToolCallItem]] = None
    call: Optional[Dict[str, Any]] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    recordingUrl: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    artifact: Optional[Dict[str, Any]] = None
    structuredData: Optional[Dict[str, Any]] = None
    successEvaluation: Optional[Union[str, bool]] = None
    durationSeconds: Optional[Union[int, float]] = None

class VapiWebhookPayload(BaseModel):
    model_config = {"extra": "allow"}
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

