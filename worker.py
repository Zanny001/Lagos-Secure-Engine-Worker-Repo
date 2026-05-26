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
    
    # Repair standard formatting issue with keys often hitting mobile configurations
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
    
    # Dynamic tab discovery: Grabs the absolute first visible tab on the sheet, regardless of name
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
# 2. DIGITAL INFRASTRUCTURE GATEWAY NODE (MONO INTEGRATION)
# ==========================================================
# Reads from Railway variables if live, defaults to "YOUR_MONO_SECRET_KEY_HERE" to run simulations
MONO_SECRET_KEY = os.environ.get("MONO_SECRET_KEY", "YOUR_MONO_SECRET_KEY_HERE")

def verify_target_entity(company_name, rc_identification):
    # If key isn't provided, safe mock simulation mode takes over automatically
    if MONO_SECRET_KEY == "test_sk_c4zyttomn2mwyrb0w5a5":
        print(f"  [SIMULATION] Checking '{company_name}' (RC: {rc_identification})")
        time.sleep(1.5)
        
        invalid_triggers = ["12345", "fail", "mismatch", "unverified", "alert"]
        if any(trigger in str(rc_identification).lower() for trigger in invalid_triggers):
            return "UNVERIFIED (RED)"
        return "VERIFIED"
    
    # Real live API request processing node
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
        return f"ERROR ({str(gateway_exception)})"

# ==========================================================
# 3. INTERACTIVE POLLING DAEMON LOOP
# ==========================================================
print("\n[LIVE] Engine Worker daemon running. Listening for spreadsheet updates...")
print("-> Press Ctrl+C inside your terminal workspace to halt the loop.\n")

while True:
    try:
        spreadsheet_rows = target_worksheet.get_all_records()
        
        for current_index, individual_row in enumerate(spreadsheet_rows, start=2):
            target_name = str(individual_row.get("Company Name", "")).strip()
            target_rc = str(individual_row.get("RC Number", "")).strip()
            current_status = str(individual_row.get("Verification Status", "")).strip()
            
            # Identify rows where details exist but no check status has been logged yet
            if (target_name or target_rc) and (not current_status or current_status == "" or current_status == "None"):
                print(f"[FOUND ENTRY] Processing row {current_index}...")
                print(f"  Target -> Name: '{target_name}' | RC: '{target_rc}'")
                
                resolved_status = verify_target_entity(target_name, target_rc)
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Write status back into column 3 (C) and the time stamp into column 4 (D)
                target_worksheet.update_cell(current_index, 3, resolved_status)
                target_worksheet.update_cell(current_index, 4, current_timestamp)
                
                print(f"[UPDATED SUCCESS] Row {current_index} committed: {resolved_status}\n")
                
        # Wait 15 seconds before checking the sheet again to keep within API limits
        time.sleep(15)
        
    except KeyboardInterrupt:
        print("\n[HALTED] Sync worker shutting down cleanly.")
        break
    except Exception as general_runtime_error:
        print(f"[LOOP EXCEPTION] Retrying loop in 10s... Error: {str(general_runtime_error)}")
        time.sleep(10)

