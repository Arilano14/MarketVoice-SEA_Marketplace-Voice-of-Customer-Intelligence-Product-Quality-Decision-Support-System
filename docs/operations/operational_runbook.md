# MarketVoice SEA — Operational Runbook

**Document Version**: 1.0  
**Domain**: Operational Automation, API Microservice & Workflow Execution  
**Scope**: FastAPI Service Deployment, n8n Demonstration Execution, and Human-in-the-Loop Case Management  

---

## 1. Starting the FastAPI Microservice

### Production / Development Runner
```powershell
# Using repository runner script
python scripts/runners/start_api.py

# Or directly via Uvicorn ASGI Server on port 8000
python -m uvicorn marketvoice.api.application:app --host 127.0.0.1 --port 8000
```

### Validating Service Health & Readiness Probes
```powershell
# Liveness probe
curl http://127.0.0.1:8000/health

# Readiness probe (verifies database connectivity and loaded ML models)
curl http://127.0.0.1:8000/ready
```

---

## 2. Importing & Running the n8n Workflow

1. Open the local n8n web dashboard (`http://localhost:5678`).
2. Navigate to **Workflows** $\to$ **Import from File**.
3. Select `workflows/n8n/workflows/marketvoice_review_triage.json`.
4. Configure the PostgreSQL node connector pointing to the `marketvoice_warehouse` database schema.
5. Click **Activate Workflow**.
6. Send test payloads using the automated test harness:
   ```powershell
   python workflows/n8n/scripts/trigger_webhook_test.py
   ```

---

## 3. Human-in-the-Loop Review Resolution

When a high-risk review event (Priority P1 / P2) is ingested, it is recorded in `marketvoice_warehouse.human_review_case` with `review_status = 'PENDING_HUMAN_REVIEW'`.

### Resolving a Case via REST API
```http
POST http://127.0.0.1:8000/v1/workflow/human-review
Content-Type: application/json

{
  "case_id": "CASE_8498366AF58B6461",
  "action_type": "VENDOR_INQUIRY",
  "action_notes": "Defect confirmed with supplier. Supplier has paused batch #4402.",
  "performed_by": "QA_LEAD_01"
}
```

### Supported Triage Action Types:
* `QUALITY_AUDIT_INITIATED`: Internal physical inspection triggered.
* `VENDOR_INQUIRY`: Supplier contact and warranty check initiated.
* `LOGISTICS_REVIEW`: Courier packaging inspection requested.
* `DISMISSED_FALSE_POSITIVE`: Reviewed and flagged as non-defect.
* `MONITORING_CONFIRMED`: Acknowledged for trend tracking without immediate intervention.
