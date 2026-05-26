# Lagos Trust Engine — Asset Verification Worker

A continuous cloud-native automation engine that links secure corporate registries with administrative tracking infrastructure. This background daemon listens to an ingestion portal data pipeline, executes cryptographic verification handshakes, and logs live statuses dynamically.

## 🏗️ System Architecture

The engine bridges Google Sheets API endpoints with real-time identity nodes utilizing a decoupled environment architecture to keep security credentials separated from the codebase:

- **Ingestion Interface:** Google Sheets API (gspread node wrapper)
- **Identity Resolver:** Mono Verification Gateway (CAC corporate registry)
- **Runtime Host:** Railway Cloud Infrastructure (Persistent Linux Container)
- **Deployment Control:** GitHub Version Control Pipeline

## 🚀 Technical Highlights

- **Dynamic Credential Parser:** Detects and switches automatically between local file storage and cloud environment environments (`GOOGLE_CREDENTIALS_JSON`).
- **Cryptographic Key Repair:** Built-in string sanitation layer to handle linear breaking issues common with mobile terminal deployment vectors.
- **Fault-Tolerant Daemon:** Outfitted with an isolated interactive polling daemon loop backed by automatic exponential backoff retry cycles to withstand API structural rate-limiting thresholds.

## 🛠️ Environment Parameters

To deploy this script securely without exposing private infrastructure keys, the host container requires the configuration of two primary environment variables:

| Variable Key | Purpose / Description |
| :--- | :--- |
| `MONO_SECRET_KEY` | Dynamic bearer authorization secret string utilized for primary verification node operations. |
| `GOOGLE_CREDENTIALS_JSON` | Compressed structural raw block corresponding to the Google Cloud Service Account IAM profile keys. |

## 👨‍💻 Author Profile
Developed as part of the backend automation and infrastructure systems deployment portfolio for **Zannie DevOps & Automation Services**.

