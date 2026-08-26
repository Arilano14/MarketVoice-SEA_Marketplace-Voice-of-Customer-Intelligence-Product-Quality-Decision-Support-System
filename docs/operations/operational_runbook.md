# MarketVoice SEA — Operational Runbook

**Document Version**: 1.0  
**Phase**: Phase 11 — Operational Automation & Workflow Execution  
**Scope**: FastAPI Service Deployment, n8n Demonstration Execution, and Human-in-the-Loop Case Management  

---

## 1. Starting the FastAPI Microservice

### Development Mode
```powershell
# Set PYTHONPATH
$env:PYTHONPATH = "C:\Users\Arilano\Downloads\Project ARICE\Project SEA\src;C:\Users\Arilano\Downloads\Project ARICE\Project SEA\.pipdeps"

# Run Uvicorn ASGI Server on port 8000
python -m uvicorn marketvoice.api.application:app --host 127.0.0.1 --port 8000 --reload
```

### Validating Service Health & Readiness
```powershell
# Liveness probe
curl http://localhost:8000/health

# Full readiness probe (Database + Models)
curl http://localhost:8000/ready
```

---

## 2. Importing & Running n8n Workflow

1. Open n8n web dashboard (e.g. `http://localhost:5678`).
2. Navigate to **Workflows** $\to$ **Import from File**.
3. Select `C:\Users\Arilano\Downloads\Project ARICE\Project SEA\workflows\n8n\marketvoice_review_triage.json`.
4. Configure PostgreSQL node credentials pointing to `marketvoice_warehouse` database.
5. Click **Activate Workflow**.

---

## 3. Running Synthetic Operational Demonstration

To trigger and execute the synthetic review triage pipeline without n8n running:
```powershell
python "C:\Users\Arilano\.gemini\antigravity-ide\brain\ff4a96cd-b8fc-4c5e-ae37-96ee9cc9eb53\scratch\run_phase11.py"
```

---

## 4. Human-in-the-Loop Review Resolution

When a high-risk review event (P1/P2) is ingested, it is stored in `marketvoice_warehouse.human_review_case` with `review_status = 'PENDING_HUMAN_REVIEW'`.

### To Resolve a Case via REST API:
```bash
POST http://localhost:8000/v1/workflow/human-review
Content-Type: application/json

{
  "case_id": "CASE_8498366AF58B6461",
  "action_type": "VENDOR_INQUIRY",
  "action_notes": "Defect confirmed with supplier. Supplier has paused batch #4402.",
  "performed_by": "QA_LEAD_01"
}
```

### Supported Action Types:
* `QUALITY_AUDIT_INITIATED`: Internal physical inspection triggered.
* `VENDOR_INQUIRY`: Supplier contact and warranty check initiated.
* `LOGISTICS_REVIEW`: Courier packaging inspection requested.
* `DISMISSED_FALSE_POSITIVE`: Reviewed and flagged as safe or non-defect.
* `MONITORING_CONFIRMED`: Acknowledged for trend tracking without immediate intervention.
