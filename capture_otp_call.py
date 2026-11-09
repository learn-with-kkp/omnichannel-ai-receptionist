import os, time, requests, json, re
from dotenv import load_dotenv

load_dotenv()
vapi_key = os.getenv("VAPI_PRIVATE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

print("Active listener started: monitoring incoming calls to +1 (617) 271-8180 for 10 minutes...")
known_calls = set()

try:
    r = requests.get("https://api.vapi.ai/call?limit=15", headers={"Authorization": f"Bearer {vapi_key}"})
    if r.status_code == 200:
        for c in r.json():
            known_calls.add(c.get("id"))
except Exception as e:
    pass

# Run for 300 iterations (10 minutes)
for attempt in range(300):
    try:
        r = requests.get("https://api.vapi.ai/call?limit=5", headers={"Authorization": f"Bearer {vapi_key}"})
        if r.status_code == 200:
            calls = r.json()
            for c in calls:
                cid = c.get("id")
                if cid not in known_calls:
                    cust = c.get("customer")
                    print(f"\n🔔 [NEW CALL DETECTED!] Call ID: {cid} | Customer: {cust}")
                    # Wait for call to process
                    for poll in range(20):
                        time.sleep(2)
                        detail = requests.get(f"https://api.vapi.ai/call/{cid}", headers={"Authorization": f"Bearer {vapi_key}"}).json()
                        status = detail.get("status")
                        transcript = detail.get("transcript", "")
                        
                        if transcript:
                            print(f"  Live Transcript: {transcript}")
                            nums = re.findall(r'\b(?:\d{1,3}[\s-]?\d{3,4}|\d{6})\b', transcript)
                            if nums:
                                print(f"\n🔑 >>> EXTRACTED DIGITS FROM TRANSCRIPT: {nums} <<<")

                        if status == "ended":
                            cust_url = detail.get("artifact", {}).get("presignedCustomerUrl")
                            if cust_url and openai_key:
                                audio_res = requests.get(cust_url)
                                with open(f"/tmp/{cid}.wav", "wb") as f:
                                    f.write(audio_res.content)
                                wh_res = requests.post(
                                    "https://api.openai.com/v1/audio/transcriptions",
                                    headers={"Authorization": f"Bearer {openai_key}"},
                                    files={"file": (f"{cid}.wav", open(f"/tmp/{cid}.wav", "rb"), "audio/wav"), "model": (None, "whisper-1")}
                                )
                                print(f"\n🎯 >>> OFFICIAL WHISPER AUDIO TRANSCRIPT: {wh_res.json().get('text')} <<<")
                            known_calls.add(cid)
                            break
                    known_calls.add(cid)
    except Exception as e:
        pass
    time.sleep(2)
