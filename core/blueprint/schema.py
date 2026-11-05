"""
Universal Custom AI-Voice Receptionist Blueprint — Domain Schema.
Enables plug-and-play multi-tenant support for any appointment-based vertical:
Salons, Spas, Dental Clinics, Auto Repair, Medical Offices, and Professional Services.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class OmniChannelType(str, Enum):
    VOICE_CALL = "voice"
    WEBSITE_CHAT = "website_chat"
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"
    INSTAGRAM = "instagram"
    TELEGRAM = "telegram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    THREADS = "threads"
    REDDIT = "reddit"


class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"


class BusinessHours(BaseModel):
    open_time: str = "09:00 AM"
    close_time: str = "06:00 PM"


class BusinessRules(BaseModel):
    min_lead_time_hours: int = 2
    cancellation_window_hours: int = 24
    buffer_minutes: int = 15
    deposit_required: bool = False
    auto_confirm: bool = True


class ServiceItem(BaseModel):
    id: str
    name: str
    category: str
    duration_minutes: int
    price: float
    description: str
    add_ons: List[str] = Field(default_factory=list)
    intake_questions: List[str] = Field(default_factory=list)
    required_qualifications: List[str] = Field(default_factory=list)


class StaffMember(BaseModel):
    id: str
    name: str
    role: str
    skills: List[str] = Field(default_factory=list)
    qualified_services: List[str] = Field(default_factory=list)
    available_days: List[str] = Field(default_factory=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
    start_hour: int = 9   # 9:00 AM
    end_hour: int = 18    # 6:00 PM
    calendar_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_skills(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "qualified_services" in values and not values.get("skills"):
                values["skills"] = values["qualified_services"]
            elif "skills" in values and not values.get("qualified_services"):
                values["qualified_services"] = values["skills"]
        return values


class FAQItem(BaseModel):
    id: Optional[str] = "faq-1"
    question: str
    answer: str
    category: str = "General"
    tags: List[str] = Field(default_factory=list)


class AccentProfile(BaseModel):
    key: str = "red_american"
    accent_id: Optional[str] = None
    name: str
    flag: str = "🗣️"
    locale: str = "en-US"
    tts_voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    openai_voice: str = "nova"
    pitch: float = 1.15
    speaking_rate: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.8
    greeting_template: str = "Hello, how can I help you today?"
    conversational_style: str = "Warm and professional"
    sample_phrase: str = "We look forward to seeing you!"
    description: str = "Standard Female Accent"

    @model_validator(mode="before")
    @classmethod
    def sync_keys(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "accent_id" in values and "key" not in values:
                values["key"] = values["accent_id"]
            elif "key" in values and "accent_id" not in values:
                values["accent_id"] = values["key"]
            if "tts_voice_id" in values and "elevenlabs_voice_id" not in values:
                values["elevenlabs_voice_id"] = values["tts_voice_id"]
            elif "elevenlabs_voice_id" in values and "tts_voice_id" not in values:
                values["tts_voice_id"] = values["elevenlabs_voice_id"]
        return values


class BusinessProfile(BaseModel):
    id: str = "salon"
    tenant_id: Optional[str] = None
    name: str = "Luxe Salon & Spa"
    business_name: Optional[str] = None
    industry: str = "salon"
    vertical: Optional[str] = None
    tagline: str = "Elevate Your Style"
    phone: str = "+16175550100"
    phone_number: Optional[str] = None
    address: str = "450 Newbury Street, Boston, MA"
    timezone: str = "America/New_York"
    currency: str = "USD"
    lead_time_hours: int = 2
    booking_horizon_days: int = 30
    cancellation_window_hours: int = 24
    buffer_minutes: int = 15
    google_calendar_id: Optional[str] = None

    business_hours: BusinessHours = Field(default_factory=BusinessHours)
    business_rules: BusinessRules = Field(default_factory=BusinessRules)

    services: List[ServiceItem] = Field(default_factory=list)
    staff: List[StaffMember] = Field(default_factory=list)
    faqs: List[FAQItem] = Field(default_factory=list)
    accent_profiles: Dict[str, AccentProfile] = Field(default_factory=dict)
    default_accent: str = "red_american"

    @model_validator(mode="before")
    @classmethod
    def sync_tenant_attrs(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "tenant_id" in values and "id" not in values:
                values["id"] = values["tenant_id"]
            elif "id" in values and "tenant_id" not in values:
                values["tenant_id"] = values["id"]

            if "business_name" in values and "name" not in values:
                values["name"] = values["business_name"]
            elif "name" in values and "business_name" not in values:
                values["business_name"] = values["name"]

            if "vertical" in values and "industry" not in values:
                values["industry"] = values["vertical"]
            elif "industry" in values and "vertical" not in values:
                values["vertical"] = values["industry"]

            if "phone_number" in values and "phone" not in values:
                values["phone"] = values["phone_number"]
            elif "phone" in values and "phone_number" not in values:
                values["phone_number"] = values["phone"]
        return values

    def to_system_prompt_context(self) -> str:
        """Assembles unified context string for ultra-fast RAGless execution."""
        services_summary = "\n".join([
            f"- {s.name} (${s.price:.2f}, {s.duration_minutes} min): {s.description}"
            for s in self.services
        ])
        staff_summary = "\n".join([
            f"- {st.name} ({st.role}): Specialties [{', '.join(st.skills)}]"
            for st in self.staff
        ])
        faqs_summary = "\n".join([
            f"Q: {faq.question}\nA: {faq.answer}"
            for faq in self.faqs
        ])

        return f"""Business Profile:
Name: {self.name}
Industry: {self.industry}
Address: {self.address}
Phone: {self.phone}
Hours: {self.business_hours.open_time} - {self.business_hours.close_time}
Lead Time Policy: {self.business_rules.min_lead_time_hours} hours minimum before booking.
Cancellation Window: {self.business_rules.cancellation_window_hours} hours.

Services Offered:
{services_summary}

Specialists / Staff:
{staff_summary}

Knowledge Base FAQs:
{faqs_summary}
"""


class AppointmentRequest(BaseModel):
    caller_name: str
    caller_phone: str
    service_name: str
    stylist_name: Optional[str] = "Elena"
    appointment_datetime: str
    notes: Optional[str] = ""
    channel: OmniChannelType = OmniChannelType.WEBSITE_CHAT
    accent: str = "red_american"
