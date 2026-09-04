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
├── fixtures/                              # Standalone synthetic review event payloads (P1–P4)
│   ├── synthetic_p1_event.json            # P1 Chronic defect event
│   ├── synthetic_p2_event.json            # P2 Order inaccuracy event
│   ├── synthetic_p3_event.json            # P3 Moderate packaging event
│   └── synthetic_p4_event.json            # P4 Informational positive review with PII
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

1. Open n8n UI at `http://localhost:5678`.
2. Create local admin credentials (instance is local-only).
3. Navigate to **Workflows** $\to$ **Import from File...**
4. Select `workflows/n8n/workflows/marketvoice_review_triage.json`.
5. On PostgreSQL nodes, connect to the local analytical warehouse (`marketvoice_warehouse` schema).
6. Click **Activate Workflow**.

---

## 4. Automated Testing & Validation

### Validate Workflow JSON Topology & Syntax:
```powershell
python workflows/n8n/scripts/validate_workflow_syntax.py
```

### Trigger Automated Webhook Test Suite:
```powershell
python workflows/n8n/scripts/trigger_webhook_test.py
```
