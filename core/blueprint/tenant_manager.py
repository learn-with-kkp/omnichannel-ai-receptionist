"""
Universal Multi-Tenant Business Registry & Vertical Configurations.
Pre-packages production manifests for Salon, Dental, Automotive, and Medical Clinic.
"""

from typing import Dict, List, Optional, Any
from core.blueprint.schema import BusinessProfile, ServiceItem, StaffMember, FAQItem, AccentProfile

# 1. Standard Multi-Dialect Voice Profiles (Female Voice: Sofia)
DEFAULT_ACCENTS: Dict[str, AccentProfile] = {
    "general_american": AccentProfile(
        accent_id="general_american",
        name="General American (Neutral US / West Coast)",
        flag="🇺🇸",
        locale="en-US",
        tts_voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel / Sofia
        greeting_template="Hello and welcome to {business_name}! My name is Sofia, your AI receptionist. How can I assist you with scheduling or questions today?",
        conversational_style="Crisp, modern, corporate neutral, articulate, and welcoming.",
        sample_phrase="I would be happy to check our availability and book that slot for you right now."
    ),
    "canadian_english": AccentProfile(
        accent_id="canadian_english",
        name="Canadian English (Polite & Warm)",
        flag="🇨🇦",
        locale="en-CA",
        tts_voice_id="21m00Tcm4TlvDq8ikWAM",
        greeting_template="Hello there! Welcome to {business_name}. My name is Sofia. Great to have you reach out today! How can I help you book your appointment?",
        conversational_style="Courteous, polite North American raising, attentive Canadian phrasing, friendly hospitality.",
        sample_phrase="No problem at all! Let's get that scheduled for you right away, no worries."
    ),
    "latino_american": AccentProfile(
        accent_id="latino_american",
        name="Latino-American (Warm Bilingual Hospitality)",
        flag="🇺🇸🇲🇽",
        locale="en-US",
        tts_voice_id="21m00Tcm4TlvDq8ikWAM",
        openai_voice="nova",
        greeting_template="¡Hola! Welcome to {business_name}! Sofia here. So wonderful to have you reach out today. How can I help you book your appointment?",
        conversational_style="Warm, expressive, vibrant hospitality, bilingual conversational touches ('Hola', 'gracias', 'amigo', 'con mucho gusto').",
        sample_phrase="¡Con mucho gusto! I would be delighted to arrange that appointment for you right now."
    ),
    "red_american": AccentProfile(
        accent_id="red_american",
        name="Red American / Southern Warmth",
        flag="🇺🇸",
        locale="en-US",
        tts_voice_id="21m00Tcm4TlvDq8ikWAM",
        greeting_template="Hey there! Thanks for reaching out to {business_name}. My name is Sofia, your virtual receptionist. How can I help you today, darlin'?",
        conversational_style="Warm, hospitable, friendly southern colloquialisms ('sure thing', 'you bet', 'we'd love to have you').",
        sample_phrase="Sure thing! We'll get that all squared away for you right now."
    ),
    "european_british": AccentProfile(
        accent_id="european_british",
        name="European / British English (London RP)",
        flag="🇬🇧",
        locale="en-GB",
        tts_voice_id="pFZP5JQG7iQjIQuC4Bku",  # Lily
        greeting_template="Good day! Thank you for contacting {business_name}. My name is Sofia. Splendid of you to reach out. How may I be of assistance with your appointment today?",
        conversational_style="Polite Received Pronunciation, crisp diction, British idioms ('splendid', 'brilliant', 'half past', 'sorted').",
        sample_phrase="Splendid! I have reserved that time for you, and your details are perfectly sorted."
    ),
    "irish_english": AccentProfile(
        accent_id="irish_english",
        name="Irish English (Dublin Warmth)",
        flag="🇮🇪",
        locale="en-IE",
        tts_voice_id="pFZP5JQG7iQjIQuC4Bku",
        greeting_template="Hello and welcome to {business_name}! Sofia here to help you out. How are you keeping today, and how can I sort your booking?",
        conversational_style="Warm, engaging, melodious cadence, helpful and approachable phrasing.",
        sample_phrase="Grand! That's no trouble at all, I'll have that booked and sorted for you in two seconds."
    ),
    "euro_international": AccentProfile(
        accent_id="euro_international",
        name="Euro-International English (Continental)",
        flag="🇪🇺",
        locale="en-EU",
        tts_voice_id="pFZP5JQG7iQjIQuC4Bku",
        greeting_template="Hello and welcome to {business_name}. My name is Sofia. We are delighted to assist international and European clients today. How may I direct your booking?",
        conversational_style="Clear, measured pace, universally understood English tailored for European business hubs.",
        sample_phrase="Certainly. I am confirming your reservation across our system now."
    ),
    "australian_english": AccentProfile(
        accent_id="australian_english",
        name="Australian English (Sydney Friendly)",
        flag="🇦🇺",
        locale="en-AU",
        tts_voice_id="EXAVITQu4vr4xnSDxMaL",
        greeting_template="G'day! Welcome to {business_name}. Sofia here, how's it going today? How can I help sort your booking?",
        conversational_style="Breezy, optimistic, cheerful, clear Australian pacing.",
        sample_phrase="Too easy! Let's lock in that time for you straight away."
    ),
    "indian_english": AccentProfile(
        accent_id="indian_english",
        name="Indian English (Clear & Courteous)",
        flag="🇮🇳",
        locale="en-IN",
        tts_voice_id="ThT5KcBeYPX3keUQqHPh",
        greeting_template="Namaste and a very good day to you! Thank you for contacting {business_name}. I am Sofia. Kindly let me know which booking slot or service you would like to arrange today.",
        conversational_style="Polite, respectful, articulated syllables, honorifics ('kindly', 'pleased to help', 'reconfirming your slot').",
        sample_phrase="Kindly share your preferred date and time, and I will check the live available slots right away."
    ),
    "african_english": AccentProfile(
        accent_id="african_english",
        name="African English (Warm Cadence)",
        flag="🌍",
        locale="en-ZA",
        tts_voice_id="EXAVITQu4vr4xnSDxMaL",
        greeting_template="Warm greetings! Welcome to {business_name}. My name is Sofia. You are most welcome, and I am here to assist you with your booking. How may I serve you today?",
        conversational_style="Measured, respectful, vibrant and warm hospitality, community-focused phrasing.",
        sample_phrase="You are most welcome! Let us secure this appointment time for you."
    ),
}

# 2. Industry Vertical Manifests

SALON_PROFILE = BusinessProfile(
    tenant_id="salon_luxe",
    vertical="salon",
    business_name="Luxe Salon & Spa",
    tagline="Bespoke Hair Styling, Luxury Color Treatments & Wellness",
    phone_number="+19124999633",
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

# 6. Real Estate Agency & Luxury Property Showings
REAL_ESTATE_PROFILE = BusinessProfile(
    tenant_id="real_estate_primekey",
    vertical="real_estate",
    business_name="PrimeKey Luxury Real Estate & Property Advisory",
    tagline="Premier Residential Showings, Luxury Listings & Commercial Brokerage",
    phone_number="+18007775533",
    address="800 5th Avenue, Suite 24A, New York, NY 10065",
    timezone="America/New_York",
    currency="USD",
    lead_time_hours=2,
    cancellation_window_hours=6,
    google_calendar_id="primary",
    services=[
        ServiceItem(id="re1", name="Private Home Showing & Property Tour", category="Residential", duration_minutes=60, price=0.0, description="Exclusive walkthrough of listing with licensed luxury specialist. Proof of funds / pre-approval reviewed."),
        ServiceItem(id="re2", name="Home Valuation & Seller Strategy Session", category="Advisory", duration_minutes=45, price=0.0, description="Comprehensive comparative market analysis (CMA) and listing strategy consultation."),
        ServiceItem(id="re3", name="First-Time Homebuyer Strategy & Pre-Approval", category="Consultation", duration_minutes=60, price=0.0, description="Buyer intake, financing roadmap, neighborhood profiling, and MLS portal setup."),
        ServiceItem(id="re4", name="Commercial Real Estate Space Viewing", category="Commercial", duration_minutes=90, price=0.0, description="Guided tour of prime retail, office, or industrial properties with lease term advisory."),
        ServiceItem(id="re5", name="Luxury Penthouse VIP Viewing", category="Luxury", duration_minutes=75, price=0.0, description="Private escort through high-end waterfront / penthouse portfolio with private broker."),
    ],
    staff=[
        StaffMember(id="rest1", name="Victoria Sterling", role="Managing Listing Broker", qualified_services=["Private Home Showing & Property Tour", "Home Valuation & Seller Strategy Session", "Luxury Penthouse VIP Viewing"]),
        StaffMember(id="rest2", name="David Vance", role="Senior Commercial & Residential Broker", qualified_services=["Commercial Real Estate Space Viewing", "Private Home Showing & Property Tour"]),
        StaffMember(id="rest3", name="Chloe Montgomery", role="Buyer Specialist & Relocation Advisor", qualified_services=["First-Time Homebuyer Strategy & Pre-Approval", "Private Home Showing & Property Tour"]),
    ],
    faqs=[
        FAQItem(question="Do I need a pre-approval letter before touring luxury properties?", answer="Yes, private showings for properties above $1.5M require either a lender pre-approval letter or proof of funds."),
        FAQItem(question="Do you help with corporate and international relocations?", answer="Yes, our international relocation desk assists clients moving between the US, Canada, UK, and European hubs."),
        FAQItem(question="Are property showings free of charge?", answer="Yes! All residential and commercial showings booked through our AI concierge are 100% complimentary."),
    ],
    accent_profiles=DEFAULT_ACCENTS,
    default_accent="general_american"
)

# 7. Corporate, Litigation & Estate Law Firm
LEGAL_PROFILE = BusinessProfile(
    tenant_id="legal_apex",
    vertical="legal",
    business_name="Apex & Partners Legal Advocates & Counsel",
    tagline="Confidential Legal Representation, M&A Advisory & Litigation Intake",
    phone_number="+18009994422",
    address="100 Financial District Blvd, 32nd Floor, Boston, MA 02110",
    timezone="America/New_York",
    currency="USD",
    lead_time_hours=3,
    cancellation_window_hours=24,
    google_calendar_id="primary",
    services=[
        ServiceItem(id="l1", name="Confidential Initial Legal Consultation", category="General", duration_minutes=45, price=150.0, description="Initial case assessment protected under attorney-client privilege."),
        ServiceItem(id="l2", name="Corporate Formation & M&A Strategy Review", category="Corporate", duration_minutes=60, price=350.0, description="Review of venture financing, incorporation, shareholder agreements, or M&A contracts."),
        ServiceItem(id="l3", name="Personal Injury Case Evaluation", category="Litigation", duration_minutes=30, price=0.0, description="Free case evaluation for auto accidents, workplace injury, or liability. Contingency-based."),
        ServiceItem(id="l4", name="Estate Planning, Wills & Trust Strategy", category="Estate", duration_minutes=60, price=250.0, description="Comprehensive asset protection, revocable living trusts, wills, and health directives."),
        ServiceItem(id="l5", name="Cross-Border Immigration & Visa Advisory", category="Immigration", duration_minutes=45, price=200.0, description="Consultation for investor visas (E-2/EB-5), corporate transfers (L-1/H-1B), or residency."),
    ],
    staff=[
        StaffMember(id="lst1", name="Attorney Julian Hayes", role="Managing Partner - Corporate & Commercial", qualified_services=["Corporate Formation & M&A Strategy Review", "Confidential Initial Legal Consultation"]),
        StaffMember(id="lst2", name="Attorney Rebecca Sinclair", role="Senior Litigator - Personal Injury", qualified_services=["Personal Injury Case Evaluation", "Confidential Initial Legal Consultation"]),
        StaffMember(id="lst3", name="Attorney Arthur Pendelton", role="Trust & Estate Planning Counsel", qualified_services=["Estate Planning, Wills & Trust Strategy", "Confidential Initial Legal Consultation"]),
    ],
    faqs=[
        FAQItem(question="Is this conversation protected under attorney-client privilege?", answer="Yes, all information disclosed to our AI intake receptionist and during legal consultations is kept strictly confidential under attorney-client privilege."),
        FAQItem(question="Do you charge upfront fees for personal injury cases?", answer="No, our personal injury practice works on a contingency basis—no recovery, no legal fees."),
    ],
    accent_profiles=DEFAULT_ACCENTS,
    default_accent="general_american"
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
            "real_estate": REAL_ESTATE_PROFILE,
            "real_estate_primekey": REAL_ESTATE_PROFILE,
            "legal": LEGAL_PROFILE,
            "legal_apex": LEGAL_PROFILE,
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
        k = (accent_key or "general_american").lower()
        if k in DEFAULT_ACCENTS:
            return DEFAULT_ACCENTS[k]
        for acc_k, acc_v in DEFAULT_ACCENTS.items():
            if acc_k in k or k in acc_k:
                return acc_v
        return DEFAULT_ACCENTS["general_american"]

    def list_accents(self) -> List[AccentProfile]:
        return list(DEFAULT_ACCENTS.values())

    def list_verticals(self) -> List[Dict[str, str]]:
        return [
            {"id": "salon", "name": "Luxe Salon & Spa", "vertical": "Salon / Spa", "services_count": str(len(SALON_PROFILE.services))},
            {"id": "dental", "name": "Apex Dental Clinic", "vertical": "Dental / Orthodontics", "services_count": str(len(DENTAL_PROFILE.services))},
            {"id": "automotive", "name": "Precision Motor Works", "vertical": "Auto Repair / Tires", "services_count": str(len(AUTOMOTIVE_PROFILE.services))},
            {"id": "clinic", "name": "CareFirst Family Medical", "vertical": "Doctor / Clinic", "services_count": str(len(CLINIC_PROFILE.services))},
            {"id": "real_estate", "name": "PrimeKey Luxury Real Estate", "vertical": "Real Estate / Showings", "services_count": str(len(REAL_ESTATE_PROFILE.services))},
            {"id": "legal", "name": "Apex & Partners Legal Counsel", "vertical": "Law Firm / Legal Intake", "services_count": str(len(LEGAL_PROFILE.services))},
        ]

    def onboard_custom_tenant(
        self,
        tenant_id: str,
        business_name: str,
        vertical: str,
        phone_number: str,
        address: str,
        currency: str = "USD",
        services: Optional[List[Dict[str, Any]]] = None,
        staff: Optional[List[Dict[str, Any]]] = None,
        whatsapp_phone_number_id: str = "",
        meta_page_id: str = "",
        instagram_account_id: str = "",
        google_calendar_id: str = "primary",
        primary_accent: str = "general_american"
    ) -> BusinessProfile:
        """Dynamically instantiates and registers a new customer tenant."""
        tid = tenant_id.lower().strip().replace(" ", "_")
        service_items = []
        if services:
            for i, s in enumerate(services):
                service_items.append(ServiceItem(
                    id=f"{tid}_s{i+1}",
                    name=s.get("name", "Consultation"),
                    category=s.get("category", "General"),
                    duration_minutes=int(s.get("duration_minutes", 45)),
                    price=float(s.get("price", 50.0)),
                    description=s.get("description", "Standard consultation")
                ))
        else:
            # Default starter service
            service_items.append(ServiceItem(
                id=f"{tid}_s1",
                name="Initial Consultation",
                category="General",
                duration_minutes=45,
                price=50.0,
                description="Initial consultation and onboarding session."
            ))

        staff_items = []
        if staff:
            for i, st in enumerate(staff):
                staff_items.append(StaffMember(
                    id=f"{tid}_st{i+1}",
                    name=st.get("name", "Specialist"),
                    role=st.get("role", "Specialist"),
                    qualified_services=[s.name for s in service_items]
                ))
        else:
            staff_items.append(StaffMember(
                id=f"{tid}_st1",
                name="Front Desk Specialist",
                role="Specialist",
                qualified_services=[s.name for s in service_items]
            ))

        new_profile = BusinessProfile(
            tenant_id=tid,
            vertical=vertical,
            business_name=business_name,
            tagline=f"Premier {vertical.replace('_', ' ').title()} Services",
            phone_number=phone_number,
            address=address,
            currency=currency,
            google_calendar_id=google_calendar_id or "primary",
            services=service_items,
            staff=staff_items,
            accent_profiles=DEFAULT_ACCENTS,
            default_accent=primary_accent
        )

        self.tenants[tid] = new_profile

        # Also persist into SQLite
        try:
            from backend.database import create_tenant
            db_services = [(s.name, s.duration_minutes, int(s.price)) for s in service_items]
            db_stylists = [st.name for st in staff_items]
            create_tenant(tid, business_name, phone_number, address, db_services, db_stylists)
        except Exception:
            pass

        return new_profile


tenant_manager = TenantManager()
tenant_registry = tenant_manager
