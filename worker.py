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
    
    if "GOOGLE_CREDENTIALS_JSON" in os.environ:
        print("[INIT] Environment variable detected. Loading from Cloud configuration...")
        raw_string_data = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    else:
        print("[INIT] No environment variable found. Loading from local credentials.json...")
        with open("credentials.json", "r") as file_pointer:
            raw_string_data = file_pointer.read().strip()
            
    if not raw_string_data:
        raise ValueError("The credential data payload is completely empty.")
        
    raw_credentials = json.loads(raw_string_data)
    
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

TARGET_SPREADSHEET_ID = "1Oy2q6YIVDe4kMMagomRm252Mf3INZgES87MFoUp72yA"

try:
    print(f"[CONNECT] Opening Google Sheet ID: {TARGET_SPREADSHEET_ID}...")
    opened_spreadsheet = google_client.open_by_key(TARGET_SPREADSHEET_ID)
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
MONO_SECRET_KEY = os.environ.get("MONO_SECRET_KEY", "SIMULATION_MODE")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "SIMULATION_MODE")

def broadcast_alert(name, rc, status_type):
    """Dispatches a rich embed alert log to your Discord channel when an asset is flagged."""
    if DISCORD_WEBHOOK_URL == "SIMULATION_MODE" or not DISCORD_WEBHOOK_URL:
        print(f"  [NOTIFY SIMULATION] Discord alert bypassed: Target '{name}' status: {status_type}")
        return
        
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
        
        invalid_triggers = ["12345", "fail", "mismatch", "unverified", "alert"]
        if any(trigger in str(rc_identification).lower() for trigger in invalid_triggers):
            return "UNVER

