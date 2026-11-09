import os
import json
import requests
from dotenv import load_dotenv

load_dotenv("/Users/kishorkumarparoi/Desktop/Maven - The AI Engineering Bootcamp /Resources/AIE5-main/salon-voice-ai-receptionist/.env")
VAPI_KEY = os.getenv("VAPI_PRIVATE_API_KEY")
SERVER_URL = "https://ai-voice-receptionist.kishor.tech/webhook/vapi-tools"

HEADERS = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# Common Salon Tool IDs
COMMON_TOOL_IDS = [
    "6c0d28b5-1258-45b7-97a5-a7fe981deff5", # check_availability
    "5477f565-44fd-4041-a39d-4a63ab165f40", # book_appointment
    "9df322c5-64af-44a7-b82f-105fb11e17ac", # lookup_appointment
    "c330c825-a0f6-40cb-9225-eb72ca655025", # reschedule_appointment
    "fca2e93e-b963-469c-beaf-c4d4f9ee1f61", # cancel_appointment
    "d4a55cbb-2c60-44e2-b916-15931d07f091", # send_text
    "cf4d3198-b52a-44b8-ab16-1ccde345e2f9", # query_knowledge_base
    "d72cf825-1222-42cf-b3f7-843c3a06deb4", # end_call
]

SOPHIA_ID = "b9242970-fbef-4991-8e94-4e59ebd4ab47"
MARCUS_ID = "f8b6b7fc-ce8e-452c-bb8b-90b27bedb8cb"
SQUAD_ID = "816b5fbf-8eb1-4e26-805b-3cc6caade9ce"

def create_or_find_assistant(name, payload):
    res = requests.get("https://api.vapi.ai/assistant", headers=HEADERS)
    for a in res.json():
        if a.get("name") == name:
            print(f"Assistant '{name}' already exists with ID: {a['id']}. Updating...")
            up_res = requests.patch(f"https://api.vapi.ai/assistant/{a['id']}", headers=HEADERS, json=payload)
            return a["id"]
    
    print(f"Creating new assistant '{name}'...")
    new_res = requests.post("https://api.vapi.ai/assistant", headers=HEADERS, json=payload)
    if new_res.status_code in [200, 201]:
        new_id = new_res.json()["id"]
        print(f"Created '{name}' with ID: {new_id}")
        return new_id
    else:
        print(f"Failed to create '{name}': {new_res.text}")
        raise RuntimeError(new_res.text)

def main():
    print("=== Step 1: Setting up Kishor (AI Forward Deployment Engineer) ===")
    kishor_payload = {
        "name": "AI Forward Deployment Engineer - Kishor",
        "firstMessage": "Hello! This is Kishor, AI Forward Deployment Engineer. How can I help you customize your software, optimize operations, or assist with your salon tech today?",
        "serverUrl": SERVER_URL,
        "voice": {
            "provider": "openai",
            "voiceId": "echo"
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "toolIds": COMMON_TOOL_IDS,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Kishor, an elite AI Forward Deployment Engineer and Lead Technical Architect for Luxe Salon & Spa and ParoiAI.\n"
                        "You specialize in software engineering, backend operations, API integrations, webhooks, omnichannel synchronization (WhatsApp, Instagram, Messenger, Telnyx SMS, Vapi Voice), database migrations, and operational customization.\n"
                        "You speak with genuine warmth, clarity, technical brilliance, and calm patience. When a salon owner, developer, enterprise partner, or VIP client calls, you explain solutions clearly without unnecessary jargon unless requested.\n"
                        "You have full access to our appointment booking system, calendar, and SMS tools.\n"
                        "If a caller needs:\n"
                        "- General salon appointments, hair cuts, facials, or front-desk check-in: smoothly hand them over to Sophia.\n"
                        "- Master hair styling, balayage, or salon director consultations: hand them over to Marcus.\n"
                        "- Packages, membership deals, high-ticket pricing, or business scaling: hand them over to Tasnim.\n"
                        "- VIP relations, public relations, escalations, or conflict resolution: hand them over to Raiyan."
                    )
                }
            ]
        }
    }
    kishor_id = create_or_find_assistant("AI Forward Deployment Engineer - Kishor", kishor_payload)

    print("\n=== Step 2: Setting up Tasnim (Head of Sales & Growth Strategy) ===")
    tasnim_payload = {
        "name": "Head of Sales - Tasnim",
        "firstMessage": "Hello and welcome! My name is Tasnim, Head of Sales and Client Growth. How can I craft the perfect luxury experience or growth package for you today?",
        "serverUrl": SERVER_URL,
        "voice": {
            "provider": "openai",
            "voiceId": "shimmer"
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "toolIds": COMMON_TOOL_IDS,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Tasnim, the Head of Sales & Growth Strategy at Luxe Salon & Spa and ParoiAI.\n"
                        "You are energetic, charismatic, deeply empathetic, consultative, and inspiring.\n"
                        "You specialize in high-value salon transformation packages, seasonal bridal & VIP memberships, loyalty programs, bespoke service bundles, and business growth strategy for commercial clients.\n"
                        "You listen attentively to understand what the guest or business owner truly desires, celebrate their goals, and craft the perfect package that delivers breathtaking value and luxury. You never sound pushy; you are an inspiring beauty and business advisor who makes every client feel valued and excited.\n"
                        "You have full access to our appointment booking system, calendar, and SMS tools.\n"
                        "If a caller needs:\n"
                        "- Technical architecture, software customization, API integrations, or system operations: hand them over to Kishor.\n"
                        "- Master hair styling, balayage, or creative director consultations: hand them over to Marcus.\n"
                        "- General front desk reception, standard haircut or facial bookings: hand them over to Sophia.\n"
                        "- VIP communications, customer satisfaction feedback, or dispute resolution: hand them over to Raiyan."
                    )
                }
            ]
        }
    }
    tasnim_id = create_or_find_assistant("Head of Sales - Tasnim", tasnim_payload)

    print("\n=== Step 3: Setting up Raiyan (Director of Communications) ===")
    raiyan_payload = {
        "name": "Director of Communications - Raiyan",
        "firstMessage": "Good day! This is Raiyan, Director of Communications. It is an absolute pleasure to assist you. How may I be of service today?",
        "serverUrl": SERVER_URL,
        "voice": {
            "provider": "openai",
            "voiceId": "fable"
        },
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "toolIds": COMMON_TOOL_IDS,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Raiyan, the Director of Communications and Client Relations for Luxe Salon & Spa and ParoiAI.\n"
                        "You are the epitome of gracious communication, emotional intelligence, patience, and warmth.\n"
                        "You specialize in VIP concierge experiences, public relations, sensitive feedback resolution, guest satisfaction, bilingual diplomacy, and making every client feel cherished, respected, and heard.\n"
                        "Whenever a guest has an inquiry, special request, complaint, or feedback, you validate their experience with supreme poise, apologize sincerely if anything fell short, and provide swift, elegant solutions.\n"
                        "You have full access to our appointment booking system, calendar, and SMS tools.\n"
                        "If a caller needs:\n"
                        "- Technical customization, software operations, or engineering: hand them over to Kishor.\n"
                        "- Sales packages, commercial memberships, or pricing negotiations: hand them over to Tasnim.\n"
                        "- Master hair styling, color transformations, or bridal hair: hand them over to Marcus.\n"
                        "- Routine front-desk reception, standard appointments, or salon check-in: hand them over to Sophia."
                    )
                }
            ]
        }
    }
    raiyan_id = create_or_find_assistant("Director of Communications - Raiyan", raiyan_payload)

    print("\n=== Step 4: Updating Sophia and Marcus prompts with 5-Squad Awareness ===")
    sophia_update = {
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "toolIds": COMMON_TOOL_IDS,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Sophia, the Lead Concierge and Head Receptionist at Luxe Salon & Spa on Newbury Street, Boston.\n"
                        "You provide a 5-star warm greeting, schedule haircuts, blowouts, manicures, and facials, check availability, and coordinate our frontfoot team.\n"
                        "You work alongside an elite 5-member leadership squad:\n"
                        "- Marcus Vance: Master Stylist & Salon Director (hair coloring, balayage, keratin, bridal hair).\n"
                        "- Kishor: AI Forward Deployment Engineer (coding, software operations, technical customization, integrations).\n"
                        "- Tasnim: Head of Sales (membership packages, luxury bridal bundles, commercial growth deals).\n"
                        "- Raiyan: Director of Communications (VIP customer care, public relations, feedback resolution).\n"
                        "When callers ask to speak with Marcus, Kishor, Tasnim, or Raiyan, or when their inquiry aligns with their specialty, warmly transfer them!"
                    )
                }
            ]
        }
    }
    requests.patch(f"https://api.vapi.ai/assistant/{SOPHIA_ID}", headers=HEADERS, json=sophia_update)

    marcus_update = {
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "toolIds": COMMON_TOOL_IDS,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Marcus Vance, the Creative Director and Master Stylist at Luxe Salon & Spa.\n"
                        "You are a charismatic, world-class hair artist specializing in balayage, precision cuts, color correction, and couture styling.\n"
                        "You are part of our 5-member leadership team:\n"
                        "- Sophia: Front Desk Concierge (general appointments, nails, facials).\n"
                        "- Kishor: AI Forward Deployment Engineer (coding, software operations, tech customization).\n"
                        "- Tasnim: Head of Sales (VIP bundles, commercial packages, membership tiers).\n"
                        "- Raiyan: Director of Communications (client feedback, PR, VIP escalations).\n"
                        "Smoothly transfer callers when their needs match your colleagues' expertise!"
                    )
                }
            ]
        }
    }
    requests.patch(f"https://api.vapi.ai/assistant/{MARCUS_ID}", headers=HEADERS, json=marcus_update)

    print("\n=== Step 5: Updating 5-Person Interconnected Squad in Vapi ===")
    squad_payload = {
        "name": "Luxe Frontfoot 5-Member Leadership Squad",
        "members": [
            # 1. Sophia
            {
                "assistantId": SOPHIA_ID,
                "assistantDestinations": [
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Director - Marcus",
                        "description": "Transfer to Marcus Vance for hair coloring, balayage, keratin, master styling, or salon director consultations."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "AI Forward Deployment Engineer - Kishor",
                        "description": "Transfer to Kishor for technical operations, software customization, API integrations, webhooks, or coding assistance."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Head of Sales - Tasnim",
                        "description": "Transfer to Tasnim for luxury packages, high-ticket memberships, bridal packages, or commercial sales deals."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Director of Communications - Raiyan",
                        "description": "Transfer to Raiyan for VIP customer relations, special requests, feedback, or dispute resolution."
                    }
                ]
            },
            # 2. Marcus
            {
                "assistantId": MARCUS_ID,
                "assistantDestinations": [
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Voice Receptionist - Sophia",
                        "description": "Transfer back to Sophia for front-desk scheduling, routine haircuts, nails, facials, or general reception."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "AI Forward Deployment Engineer - Kishor",
                        "description": "Transfer to Kishor for technical software, operational customization, or developer questions."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Head of Sales - Tasnim",
                        "description": "Transfer to Tasnim for package negotiations, corporate styling bundles, or sales pricing."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Director of Communications - Raiyan",
                        "description": "Transfer to Raiyan for client feedback, VIP correspondence, or communications."
                    }
                ]
            },
            # 3. Kishor
            {
                "assistantId": kishor_id,
                "assistantDestinations": [
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Voice Receptionist - Sophia",
                        "description": "Transfer to Sophia for standard salon bookings, front desk check-in, or reception."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Director - Marcus",
                        "description": "Transfer to Marcus for master styling, hair coloring, balayage, or salon creative direction."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Head of Sales - Tasnim",
                        "description": "Transfer to Tasnim for enterprise sales contracts, commercial package deals, or pricing tiers."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Director of Communications - Raiyan",
                        "description": "Transfer to Raiyan for corporate communications, client relations, or executive escalations."
                    }
                ]
            },
            # 4. Tasnim
            {
                "assistantId": tasnim_id,
                "assistantDestinations": [
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Voice Receptionist - Sophia",
                        "description": "Transfer to Sophia for routine salon appointments, nails, facials, or reception scheduling."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Director - Marcus",
                        "description": "Transfer to Marcus for custom styling consultations, color formulation, or hair design."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "AI Forward Deployment Engineer - Kishor",
                        "description": "Transfer to Kishor for technical feasibility, software setup, API integration, or automation."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Director of Communications - Raiyan",
                        "description": "Transfer to Raiyan for PR, media inquiries, partner relations, or client satisfaction."
                    }
                ]
            },
            # 5. Raiyan
            {
                "assistantId": raiyan_id,
                "assistantDestinations": [
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Voice Receptionist - Sophia",
                        "description": "Transfer to Sophia for regular appointment bookings, front-desk check-ins, or general reception."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Luxe Salon Director - Marcus",
                        "description": "Transfer to Marcus for stylist consultations, hair coloring, or salon director advice."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "AI Forward Deployment Engineer - Kishor",
                        "description": "Transfer to Kishor for technical issues, system software questions, or integrations."
                    },
                    {
                        "type": "assistant",
                        "assistantName": "Head of Sales - Tasnim",
                        "description": "Transfer to Tasnim for sales inquiries, luxury packages, or corporate memberships."
                    }
                ]
            }
        ]
    }

    squad_res = requests.patch(f"https://api.vapi.ai/squad/{SQUAD_ID}", headers=HEADERS, json=squad_payload)
    if squad_res.status_code in [200, 201]:
        print("✅ Successfully updated 5-Member Frontfoot Squad in Vapi!")
    else:
        print(f"❌ Failed to update squad: {squad_res.text}")

    print("\nSummary of IDs:")
    print(f"Sophia: {SOPHIA_ID}")
    print(f"Marcus: {MARCUS_ID}")
    print(f"Kishor: {kishor_id}")
    print(f"Tasnim: {tasnim_id}")
    print(f"Raiyan: {raiyan_id}")
    print(f"Squad:  {SQUAD_ID}")

if __name__ == "__main__":
    main()
