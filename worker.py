import json
import os
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

print("=" * 50)
print("     LAGOS TRUST ENGINE - RECENT ASSET SYNC     ")
print("=" * 50)

# ==========================================================
# 1. LIVE ENGINE CONFIGURATION & DYNAMIC CREDENTIAL REPAIR
# ==========================================================
try:
    print("[INIT] Loading Service Account credentials...")
    
    # Check if the environment variable exists (Railway/Cloud execution)
    if "GOOGLE_CREDENTIALS_JSON" in os.environ:
        print("[INIT] Environment variable detected. Loading from Cloud configuration...")
        raw_string_data = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    else:
        # Fallback to local storage (Mobile UserLAnd terminal execution)
        print("[INIT] No environment variable found. Loading from local credentials.json...")
        with open("credentials.json", "r") as file_pointer:
            raw_string_data = file_pointer.read().strip()
            
    if not raw_string_data:
        raise ValueError("The credential data payload is completely empty.")
        
    raw_credentials = json.loads(raw_string_data)
    
    # Repair standard formatting issue with keys hitting mobile configurations
    if "private_key" in raw_credentials:
        if "\\n" in raw_credentials["private_key"]:
            print("[REPAIR] Correcting literal line-breaks in private key...")
            raw_credentials["private_key"] = raw_credentials["private_key"].replace("\\n", "\n")
    else:
        raise KeyError("Missing critical key 'private_key' inside credentials data.")
        
    auth_scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    api_credentials = ServiceAccountCredentials.from_json_keyfile_dict(raw_credentials, auth_scopes)
    google_client = gspread.authorize(api_credentials)
    print("[INIT] Authentication Token initialized successfully.")
    
except Exception as initialization_error:
    print(f"\n[FATAL ERROR] Cryptographic Initialization failed: {str(initialization_error)}")
    exit(1)

# Unique target document link connection node
TARGET_SPREADSHEET_ID = "1Oy2q6YIVDe4kMMagomRm252Mf3INZgES87MFoUp72yA"

try:
    print(f"[CONNECT] Opening Google Sheet ID: {TARGET_SPREADSHEET_ID}...")
    opened_spreadsheet = google_client.open_by_key(TARGET_SPREADSHEET_ID)
    
    # Dynamic tab discovery: Grabs the absolute first visible tab on the sheet
    target_worksheet = opened_spreadsheet.get_worksheet(0)
    print(f"[CONNECT] Success! Active bridge connected to tab: '{target_worksheet.title}'")
    
except Exception as network_error:
    print("\n" + "="*60)
    print("         RAW GOOGLE DEVELOPER MESSAGE DETECTED         ")
    print("="*60)
    print(repr(network_error))
    print("="*60 + "\n")
    exit(1)

# ==========================================================
# 2. SECURE EXTERNAL GATEWAY GATE CARRIER (MONO & DISCORD)
# ==========================================================
# 100% Secure. Uses placeholder text so your real production keys are never leaked online.
MONO_SECRET_KEY = os.environ.get("MONO_SECRET_KEY", "SIMULATION_MODE")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "SIMULATION_MODE")

def broadcast_alert(name, rc, status_type):
    """Dispatches a rich embed alert log to your Discord channel when an asset is flagged."""
    if DISCORD_WEBHOOK_URL == "SIMULATION_MODE" or not DISCORD_WEBHOOK_URL:
        print(f"  [NOTIFY SIMULATION] Discord alert bypassed: Target '{name}' status: {status_type}")
        return
        
    # Red color code for unverified/errors, Blue color code for clean entries
    embed_color = 15158332 if "UNVERIFIED" in status_type or "ALERT" in status_type else 3447003
    
    payload = {
        "embeds": [{
            "title": "🚨 LAGOS TRUST ENGINE ALERT",
            "description": "An asset validation anomaly has triggered the automatic monitoring engine loop.",
            "color": embed_color,
            "fields": [
                {"name": "Target Entity Name", "value": f"`{name}`", "inline": True},
                {"name": "Registration / RC Number", "value": f"`{rc}`", "inline": True},
                {"name": "Engine Resolution Status", "value": f"**{status_type}**", "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=8)
        if response.status_code == 204:
            print("  [NOTIFY SUCCESS] Real-time alert dispatched to Discord channel.")
        else:
            print(f"  [NOTIFY WARN] Discord API returned status: {response.status_code}")
    except Exception as e:
        print(f"  [NOTIFY ERROR] Could not broadcast webhook payload: {str(e)}")


def verify_target_entity(company_name, rc_identification):
    """Executes verification routines. Switches automatically between sandbox testing and live calls."""
    if MONO_SECRET_KEY == "SIMULATION_MODE":
        print(f"  [SIMULATION] Verification running for '{company_name}' (RC: {rc_identification})")
        time.sleep(1.2)
        
        # Simulates failure states instantly if certain key phrases hit your spreadsheet
        invalid_triggers = ["12345", "fail", "mismatch", "unverified", "alert"]
        if any(trigger in str(rc_identification).lower() for trigger in invalid_triggers):
            return "UNVERIFIED (RED)"
        return "VERIFIED"
    
    # Real Live Mono Request Protocol Node
    gateway_url = "https://api.withmono.com/lookup/cac"
    request_headers = {
        "mono-sec-key": MONO_SECRET_KEY,
        "Content-Type": "application/json"
    }
    request_payload = {"rc_number": str(rc_identification).strip()}
    
    try:
        api_response = requests.post(gateway_url, json=request_payload, headers=request_headers, timeout=12)
        if api_response.status_code == 200:
            payload_data = api_response.json()
            if payload_data.get("status") == "active" or "id" in payload_data:
                return "VERIFIED"
            else:
                return "ALERT MISMATCH (RED)"
        elif api_response.status_code == 404:
            return "UNVERIFIED (RED)"
        else:
            return f"ERROR (STATUS {api_response.status_code})"
    except Exception as gateway_exception:

