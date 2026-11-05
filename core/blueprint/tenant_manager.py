"""
Universal Multi-Tenant Business Registry & Vertical Configurations.
Pre-packages production manifests for Salon, Dental, Automotive, and Medical Clinic.
"""

from typing import Dict, List, Optional
from core.blueprint.schema import BusinessProfile, ServiceItem, StaffMember, FAQItem, AccentProfile

# 1. Standard Multi-Dialect Voice Profiles (Female Voice: Sofia)
DEFAULT_ACCENTS: Dict[str, AccentProfile] = {
    "red_american": AccentProfile(
        accent_id="red_american",
        name="Red American / Southern Warmth",
        flag="🇺🇸",
        locale="en-US",
        tts_voice_id="21m00Tcm4TlvDq8ikWAM",  # ElevenLabs Rachel / Sofia
        greeting_template="Hey there! Thanks for reaching out to {business_name}. My name is Sofia, your virtual receptionist. How can I help you today, darlin'?",
        conversational_style="Warm, hospitable, friendly southern colloquialisms ('sure thing', 'you bet', 'we'd love to have you').",
        sample_phrase="Sure thing! We'll get that all squared away for you right now."
    ),
    "indian_english": AccentProfile(
        accent_id="indian_english",
        name="Indian English (Clear & Courteous)",
        flag="🇮🇳",
        locale="en-IN",
        tts_voice_id="MF3mGyEYCl7XYWbV9V6O",  # ElevenLabs Priya / Aditi
        greeting_template="Namaste and a very good day to you! Thank you for contacting {business_name}. I am Sofia. Kindly let me know which booking slot or service you would like to arrange today.",
        conversational_style="Polite, respectful, articulated syllables, honorifics ('kindly', 'pleased to help', 'reconfirming your slot').",
        sample_phrase="Kindly share your preferred date and time, and I will check the live available slots right away."
    ),
    "african_english": AccentProfile(
        accent_id="african_english",
        name="African English (Warm Cadence)",
        flag="🌍",
        locale="en-ZA",
        tts_voice_id="EXAVITQu4vr4xnSDxMaL",  # ElevenLabs Bella / Zola
        greeting_template="Warm greetings! Welcome to {business_name}. My name is Sofia. You are most welcome, and I am here to assist you with your booking. How may I serve you today?",
        conversational_style="Measured, respectful, vibrant and warm hospitality, community-focused phrasing.",
        sample_phrase="You are most welcome! Let us secure this appointment time for you."
    ),
    "european_british": AccentProfile(
        accent_id="european_british",
        name="European / British English (Crisp RP)",
        flag="🇬🇧",
        locale="en-GB",
        tts_voice_id="ThT5KcBeYPX3keUQqHPh",  # ElevenLabs Dorothy / Freya
        greeting_template="Good day! Thank you for contacting {business_name}. My name is Sofia. Splendid of you to reach out. How may I be of assistance with your appointment today?",
        conversational_style="Polite Received Pronunciation, crisp diction, British idioms ('splendid', 'brilliant', 'half past', 'sorted').",
        sample_phrase="Splendid! I have reserved that time for you, and your details are perfectly sorted."
    ),
}

# 2. Industry Vertical Manifests

SALON_PROFILE = BusinessProfile(
    tenant_id="salon_luxe",
    vertical="salon",
    business_name="Luxe Salon & Spa",
    tagline="Bespoke Hair Styling, Luxury Color Treatments & Wellness",
    phone_number="+16673070119",
    address="450 Lexington Ave, Suite 12B, New York, NY 10017",
    timezone="America/New_York",
    currency="USD",
    lead_time_hours=2,
    cancellation_window_hours=24,
    google_calendar_id="primary",
    services=[
        ServiceItem(id="s1", name="Womens Haircut & Blowdry", category="Hair", duration_minutes=60, price=85.0, description="Custom consultation, scalp massage, precision cut and blowout.", add_ons=["Deep Conditioning Mask (+$25)", "Gloss Treatment (+$30)"]),
        ServiceItem(id="s2", name="Mens Precision Cut", category="Hair", duration_minutes=30, price=45.0, description="Tailored haircut, hot towel finish, and modern styling.", add_ons=["Beard Trim (+$15)"]),
        ServiceItem(id="s3", name="Balayage & Full Highlights", category="Color", duration_minutes=150, price=220.0, description="Hand-painted dimensional color with bonding treatment.", add_ons=["Olaplex Strengthening (+$40)", "Toner Refresh (+$35)"]),
        ServiceItem(id="s4", name="Brazilian Keratin Smoothing", category="Texture", duration_minutes=120, price=250.0, description="Frizz-free smoothing treatment lasting up to 4 months."),
        ServiceItem(id="s5", name="Signature Gel Manicure & Pedicure", category="Nails", duration_minutes=75, price=95.0, description="Exfoliating scrub, cuticle care, massage, and long-lasting gel polish."),
    ],
    staff=[
        StaffMember(id="st1", name="Elena Rostova", role="Master Stylist & Colorist", qualified_services=["Womens Haircut & Blowdry", "Balayage & Full Highlights", "Brazilian Keratin Smoothing"]),
        StaffMember(id="st2", name="Marcus Vance", role="Senior Barber & Stylist", qualified_services=["Mens Precision Cut", "Womens Haircut & Blowdry"]),
        StaffMember(id="st3", name="Chloe Dubois", role="Nail Specialist & Esthetician", qualified_services=["Signature Gel Manicure & Pedicure"]),
    ],
    faqs=[
        FAQItem(question="Where are you located?", answer="We are located at 450 Lexington Ave, Suite 12B, New York, NY, right near Grand Central Station."),
        FAQItem(question="What is your cancellation policy?", answer="Appointments may be rescheduled or canceled with at least 24 hours notice at no charge. Late cancellations incur a 50% service charge."),
        FAQItem(question="Is parking available?", answer="Valet parking is available at the building entrance, and parking garages are located on 44th and 45th Street."),
        FAQItem(question="What payment methods do you accept?", answer="We accept all major credit cards, Apple Pay, Google Pay, and cash."),
    ],
    accent_profiles=DEFAULT_ACCENTS,
    default_accent="red_american"
)

DENTAL_PROFILE = BusinessProfile(
    tenant_id="dental_apex",
    vertical="dental",
    business_name="Apex Dental Health Clinic",
    tagline="Modern Pain-Free Dentistry, Preventive Hygiene & Implants",
    phone_number="+18005553368",
    address="720 Michigan Ave, Suite 400, Chicago, IL 60611",
    timezone="America/Chicago",
    currency="USD",
    lead_time_hours=4,
    cancellation_window_hours=48,
    google_calendar_id="primary",
    services=[
        ServiceItem(id="d1", name="Comprehensive Dental Exam & Cleaning", category="Preventive", duration_minutes=60, price=150.0, description="Full mouth digital X-rays, ultrasonic scaling, polish, and dentist consultation."),
        ServiceItem(id="d2", name="In-Office Laser Teeth Whitening", category="Cosmetic", duration_minutes=60, price=350.0, description="Professional Philips Zoom laser whitening up to 8 shades brighter."),
        ServiceItem(id="d3", name="Root Canal & Restorative Consultation", category="Endodontics", duration_minutes=45, price=180.0, description="3D CBCT scan, diagnostic evaluation, and pain relief treatment plan."),
        ServiceItem(id="d4", name="Invisalign Orthodontic Assessment", category="Orthodontics", duration_minutes=45, price=95.0, description="Digital iTero 3D smile scan and aligner simulation."),
    ],
    staff=[
        StaffMember(id="dst1", name="Dr. Sarah Jenkins, DDS", role="Lead General & Cosmetic Dentist", qualified_services=["Comprehensive Dental Exam & Cleaning", "In-Office Laser Teeth Whitening", "Invisalign Orthodontic Assessment"]),
        StaffMember(id="dst2", name="Dr. Arjun Patel, DMD", role="Endodontic Specialist", qualified_services=["Root Canal & Restorative Consultation", "Comprehensive Dental Exam & Cleaning"]),
    ],
    faqs=[
        FAQItem(question="Do you accept dental insurance?", answer="Yes, we are in-network with Delta Dental, Cigna, MetLife, Aetna, and Guardian, and we file out-of-network claims on your behalf."),
        FAQItem(question="What should I do in a dental emergency?", answer="If you are experiencing severe pain, swelling, or trauma, our on-call emergency team can see you the same day."),
        FAQItem(question="What is the cancellation policy?", answer="We request 48 hours notice for dental appointments so we can accommodate other patients needing urgent care."),
    ],
    accent_profiles=DEFAULT_ACCENTS,
    default_accent="red_american"
)

AUTOMOTIVE_PROFILE = BusinessProfile(
    tenant_id="auto_precision",
    vertical="automotive",
    business_name="Precision Motor Works & Tire Care",
    tagline="Certified German & Domestic Auto Diagnostics, Maintenance & Tires",
    phone_number="+18884449876",
    address="1820 Industrial Blvd, Austin, TX 78745",
    timezone="America/Chicago",
    currency="USD",
    lead_time_hours=3,
    cancellation_window_hours=12,
    google_calendar_id="primary",
    services=[
        ServiceItem(id="a1", name="Full Synthetic Oil & Filter Service", category="Maintenance", duration_minutes=45, price=89.0, description="Premium synthetic oil up to 5 qts, OEM filter, and 30-point digital inspection."),
        ServiceItem(id="a2", name="Brake Pad & Rotor Inspection & Replacement", category="Brakes", duration_minutes=90, price=240.0, description="Ceramic brake pads, rotor resurfacing, and brake fluid test."),
        ServiceItem(id="a3", name="Computer Diagnostic & Check Engine Scan", category="Diagnostics", duration_minutes=60, price=110.0, description="OBD-II advanced scan, electrical circuit testing, and mechanic estimate."),
        ServiceItem(id="a4", name="4-Wheel Laser Alignment & Tire Balance", category="Tires", duration_minutes=60, price=129.0, description="Digital camera laser alignment, tire rotation, and high-speed road force balancing."),
    ],
    staff=[
        StaffMember(id="ast1", name="Mike Rodriguez", role="ASE Master Technician", qualified_services=["Full Synthetic Oil & Filter Service", "Brake Pad & Rotor Inspection & Replacement", "Computer Diagnostic & Check Engine Scan"]),
        StaffMember(id="ast2", name="Dave Sterling", role="Chassis & Suspension Specialist", qualified_services=["4-Wheel Laser Alignment & Tire Balance", "Brake Pad & Rotor Inspection & Replacement"]),
    ],
    faqs=[
        FAQItem(question="Do you offer loaner cars or shuttle service?", answer="Yes, we provide complimentary local shuttle service within 10 miles and loaner vehicles for repairs taking over 4 hours."),
        FAQItem(question="Do you warranty your repair work?", answer="All parts and labor are backed by our 24-Month / 24,000-Mile Nationwide Peace of Mind Warranty."),
    ],
    accent_profiles=DEFAULT_ACCENTS,
    default_accent="red_american"
)

CLINIC_PROFILE = BusinessProfile(
    tenant_id="clinic_carefirst",
    vertical="clinic",
    business_name="CareFirst Family Medical Clinic",
    tagline="Compassionate Primary Care, Pediatrics & Telehealth",
    phone_number="+18002225464",
    address="105 Medical Center Way, Suite 200, Boston, MA 02115",
    timezone="America/New_York",
    currency="USD",
    lead_time_hours=2,
    cancellation_window_hours=24,
    google_calendar_id="primary",
    services=[
        ServiceItem(id="c1", name="Annual Wellness & Physical Exam", category="Primary Care", duration_minutes=45, price=175.0, description="Comprehensive health assessment, vital signs, biometric screening, and lab orders."),
        ServiceItem(id="c2", name="Urgent Illness & Sick Visit", category="Urgent Care", duration_minutes=30, price=120.0, description="Evaluation for fever, respiratory illness, infection, or minor injuries."),
        ServiceItem(id="c3", name="Pediatric Well-Child Checkup", category="Pediatrics", duration_minutes=40, price=140.0, description="Developmental screening, growth tracking, and childhood vaccinations."),
    ],
    staff=[
        StaffMember(id="cst1", name="Dr. Emily Thorne, MD", role="Internal Medicine Physician", qualified_services=["Annual Wellness & Physical Exam", "Urgent Illness & Sick Visit"]),
        StaffMember(id="cst2", name="Dr. Kwesi Mensah, MD", role="Pediatrician", qualified_services=["Pediatric Well-Child Checkup", "Urgent Illness & Sick Visit"]),
    ],
    faqs=[
        FAQItem(question="What insurance do you accept?", answer="We accept Medicare, Blue Cross Blue Shield, Harvard Pilgrim, Tufts, and UnitedHealthcare."),
        FAQItem(question="Can I book a telehealth appointment?", answer="Yes, non-emergency consultations can be conducted securely over telehealth."),
    ],
    accent_profiles=DEFAULT_ACCENTS,
    default_accent="red_american"
)


class TenantManager:
    """Manages active tenant profiles and vertical switching."""

    def __init__(self):
        self.tenants: Dict[str, BusinessProfile] = {
            "salon": SALON_PROFILE,
            "salon_luxe": SALON_PROFILE,
            "default_salon": SALON_PROFILE,
            "dental": DENTAL_PROFILE,
            "dental_apex": DENTAL_PROFILE,
            "automotive": AUTOMOTIVE_PROFILE,
            "auto_precision": AUTOMOTIVE_PROFILE,
            "clinic": CLINIC_PROFILE,
            "clinic_carefirst": CLINIC_PROFILE,
        }
        self.active_tenant_id = "salon"

    def get_tenant(self, tenant_id: Optional[str] = None) -> BusinessProfile:
        tid = (tenant_id or self.active_tenant_id).lower()
        return self.tenants.get(tid, self.tenants["salon"])

    def set_active_tenant(self, tenant_id: str) -> BusinessProfile:
        if tenant_id.lower() in self.tenants:
            self.active_tenant_id = tenant_id.lower()
        return self.get_tenant()

    def list_tenants(self) -> List[BusinessProfile]:
        seen = set()
        unique = []
        for p in self.tenants.values():
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)
        return unique

    def get_accent(self, accent_key: Optional[str] = None) -> AccentProfile:
        k = (accent_key or "red_american").lower()
        if k in DEFAULT_ACCENTS:
            return DEFAULT_ACCENTS[k]
        for acc_k, acc_v in DEFAULT_ACCENTS.items():
            if acc_k in k or k in acc_k:
                return acc_v
        return DEFAULT_ACCENTS["red_american"]

    def list_accents(self) -> List[AccentProfile]:
        return list(DEFAULT_ACCENTS.values())

    def list_verticals(self) -> List[Dict[str, str]]:
        return [
            {"id": "salon", "name": "Luxe Salon & Spa", "vertical": "Salon / Spa", "services_count": str(len(SALON_PROFILE.services))},
            {"id": "dental", "name": "Apex Dental Clinic", "vertical": "Dental / Orthodontics", "services_count": str(len(DENTAL_PROFILE.services))},
            {"id": "automotive", "name": "Precision Motor Works", "vertical": "Auto Repair / Tires", "services_count": str(len(AUTOMOTIVE_PROFILE.services))},
            {"id": "clinic", "name": "CareFirst Family Medical", "vertical": "Doctor / Clinic", "services_count": str(len(CLINIC_PROFILE.services))},
        ]


tenant_manager = TenantManager()
tenant_registry = tenant_manager
