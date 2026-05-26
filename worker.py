import json
import os
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

print("=" * 50)
print("     LAGOS TRUST ENGINE - ASSET SYNC     ")
print("=" * 50)

# 1. CORE SYSTEM INITIALIZATION
try:
    print("[INIT] Loading Service Account...")
    if "GOOGLE_CREDENTIALS_JSON" in os.environ:
        raw_data = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    else:
        with open("credentials.json", "r") as f:
            raw_data = f.read().strip()
            
    if not raw_data:
        raise ValueError("Credentials payload is empty.")
        
    creds = json.loads(raw_data)
    if "private_key" in creds and "\\n" in creds["private_key"]:
        creds["private_key"] = creds["private_key"].replace("\\n", "\n")
        
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    g_creds = ServiceAccountCredentials.from_json_keyfile_dict(creds, scopes)
    client = gspread.authorize(g_creds)
    print("[INIT] Auth initialized.")
except Exception as e:
    print(f"[FATAL] Init failed: {str(e)}")
    exit(1)

SHEET_ID = "1Oy2q6YIVDe4kMMagomRm252Mf3INZgES87MFoUp72yA"

try:
    sheet = client.open_by_key(SHEET_ID)
    ws = sheet.get_worksheet(0)
    print(f"[CONNECT] Connected to: {ws.title}")
except Exception as e:
    print(f"[FATAL] Sheet connection failed: {str(e)}")
    exit(1)

# 2. EXTERNAL GATEWAYS (MONO & DISCORD)
MONO_KEY = os.environ.get("MONO_SECRET_KEY", "SIMULATION_MODE")
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK_URL", "SIMULATION_MODE")

def broadcast_alert(name, rc, status):
    if DISCORD_URL == "SIMULATION_MODE" or not DISCORD_URL:
        print(f"  [SIM_ALERT] Bypassed for {name}: {status}")
        return
        
    color = 15158332 if "UNVERIFIED" in status or "ALERT" in status else 3447003
    payload = {
        "embeds": [{
            "title": "🚨 LAGOS TRUST ENGINE ALERT",
            "description": "Validation anomaly triggered monitoring engine loop.",
            "color": color,
            "fields": [
                {"name": "Entity Name", "value": f"`{name}`", "inline": True},
                {"name": "RC Number", "value": f"`{rc}`", "inline": True},
                {"name": "Resolution", "value": f"**{status}**", "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }]
    }
    try:
        res = requests.post(DISCORD_URL, json=payload, timeout=8)
        if res.status_code == 204:
            print("  [ALERT] Dispatched to Discord.")
    except Exception as e:
        print(f"  [ALERT ERROR] Discord fail: {str(e)}")

def verify_entity(name, rc):
    if MONO_KEY == "SIMULATION_MODE":
        print(f"  [SIM] Verifying '{name}' (RC: {rc})")
        time.sleep(1)
        triggers = ["12345", "fail", "mismatch", "unverified", "alert"]
        if any(t in str(rc).lower() for t in triggers):
            return "UNVERIFIED (RED)"
        return "VERIFIED"
        
    url = "https://api.withmono.com/lookup/cac"
    headers = {"mono-sec-key": MONO_KEY, "Content-Type": "application/json"}
    payload = {"rc_number": str(rc).strip()}
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "active" or "id" in data:
                return "VERIFIED"
            return "ALERT MISMATCH (RED)"
        elif res.status_code == 404:
            return "UNVERIFIED (RED)"
        return f"ERROR (STATUS {res.status_code})"
    except Exception as e:
        return f"ERROR ({str(e)})"

# 3. BACKGROUND POLLING LOOP
print("\n[LIVE] Sync worker daemon running...")
while True:
    try:
        rows = ws.get_all_records()
        for idx, row in enumerate(rows, start=2):
            t_name = str(row.get("Company Name", "")).strip()
            t_rc = str(row.get("RC Number", "")).strip()
            status = str(row.get("Verification Status", "")).strip()
            
            if (t_name or t_rc) and (not status or status in ["", "None"]):
                print(f"[ENTRY] Processing row {idx}...")
                res_status = verify_entity(t_name, t_rc)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                ws.update_cell(idx, 3, res_status)
                ws.update_cell(idx, 4, ts)
                print(f"[SUCCESS] Row {idx} updated: {res_status}")
                
                if "UNVERIFIED" in res_status or "ALERT" in res_status or "ERROR" in res_status:
                    broadcast_alert(t_name, t_rc, res_status)
                print()
        time.sleep(15)
    except KeyboardInterrupt:
        print("\n[HALTED] Sync worker shutting down cleanly.")
        break
    except Exception as err:
        print(f"[LOOP ERROR] Retrying in 10s... Error: {str(err)}")
        time.sleep(10)

