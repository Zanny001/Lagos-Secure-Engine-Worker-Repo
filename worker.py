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
MONO_SECRET

