# MarketVoice SEA — n8n Workflow Automation Architecture

**Module**: Operational Workflow & Decision Triage Orchestration  
**Classification**: `SYNTHETIC_OPERATIONAL_DEMONSTRATION`  
**Runtime Options**: Node.js CLI (`npx n8n`) or Containerized (`docker compose`)  
**Port**: `5678` (Web Dashboard & Webhook Intake)  

---

## 1. Directory Tree Structure

```text
workflows/n8n/
├── README.md                              # Technical guide & operational documentation
├── package.json                           # Node.js manifest & lifecycle scripts
├── .env.example                           # Template environment configuration
├── .env                                   # Local runtime configuration (Postgres, API host, port)
├── docker-compose.yml                     # Dockerized n8n deployment with persistent volume
├── workflows/                             # Version-controlled workflow JSON definitions
│   └── marketvoice_review_triage.json     # Main operational review triage & DSS orchestration
├── credentials/                           # Credentials templates & database connectors
│   └── credentials_template.json          # PostgreSQL warehouse connector template
├── scripts/                               # Automation & testing helper utilities
│   ├── start_n8n.ps1                      # Windows PowerShell automated launcher
│   ├── start_n8n.sh                       # Unix/Mac/WSL automated launcher
│   ├── trigger_webhook_test.py            # Automated webhook integration test harness
│   └── validate_workflow_syntax.py        # Static schema & node graph validator
└── data/                                  # Local persistent data directory (.gitignored)
    └── .gitkeep
```

---

## 2. Quickstart: Running n8n Locally

### Option A: Via PowerShell Launcher (Windows Recommended)
```powershell
powershell -ExecutionPolicy Bypass -File .\workflows\n8n\scripts\start_n8n.ps1
```

### Option B: Via npm / npx
```bash
cd workflows/n8n
npm run start:local
# or directly:
npx n8n start --port 5678
```

### Option C: Via Docker Compose
```bash
cd workflows/n8n
docker compose up -d
```

Once started, open your browser at:  
👉 **http://localhost:5678**

---

## 3. Workflow Import & Activation

1. Navigate to **Workflows** in the n8n UI.
2. Click **Add Workflow** $\to$ **Import from File...**
3. Select `workflows/n8n/workflows/marketvoice_review_triage.json`.
4. In the PostgreSQL nodes, configure credentials using:
   * **Host**: `localhost` (or `host.docker.internal` if in Docker)
   * **Database**: `marketvoice_dev`
   * **Schema**: `marketvoice_warehouse`
   * **User**: `openpg`
   * **Password**: `openpgpwd`
5. Click **Publish / Activate Workflow** (toggle at top right).

---

## 4. Testing Webhook Ingestion

To test the end-to-end pipeline with synthetic review events:
```bash
# Run webhook test suite
python workflows/n8n/scripts/trigger_webhook_test.py
```

### Webhook URL Specification:
* **Production Endpoint**: `POST http://localhost:5678/webhook/review-event`
* **Test Endpoint**: `POST http://localhost:5678/webhook-test/review-event`

### Sample Ingest Payload:
```json
{
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "source_id": "SRC_TOKOPEDIA_REVIEWS_2019",
  "review_id": "SYNTH_REV_001_P1",
  "product_id": "24670745",
  "category_id": "Komputer & Aksesoris",
  "review_text": "Barang rusak parah, tinta bocor dan tidak terdeteksi di printer! Hubungi wa 081234567890",
  "rating": 1
}
```

---

## 5. Automated Validation & Quality Assurance

To validate the syntax and connection graph of the n8n workflow definition without starting the server:
```bash
python workflows/n8n/scripts/validate_workflow_syntax.py
```
