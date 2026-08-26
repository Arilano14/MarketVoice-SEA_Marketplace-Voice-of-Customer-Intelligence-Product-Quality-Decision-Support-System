# MarketVoice SEA — Phase 11 n8n Workflow Design Specification

**Workflow File**: `workflows/n8n/marketvoice_review_triage.json`  
**Classification**: `SYNTHETIC_OPERATIONAL_DEMONSTRATION`  
**Status**: VALIDATED & DEPLOYED  

---

## 1. Architectural Role & Governance

The n8n workflow serves as the **Operational Event Orchestration Engine** for MarketVoice SEA.  
It demonstrates how high-volume incoming e-commerce customer feedback is:
1. Ingested via webhooks.
2. Sanitized to remove PII (Personally Identifiable Information).
3. Protected by SHA-256 idempotency hashing to prevent duplicate processing.
4. Analyzed via FastAPI microservices for NLP aspect intelligence and contextual decision scoring.
5. Dynamically routed into either Human-in-the-Loop review queues (for P1/P2 critical risks) or automated monitoring logs (for P3/P4 low risks).

> [!IMPORTANT]
> **Operational Demonstration Boundary**: This workflow is strictly classified as `SYNTHETIC_OPERATIONAL_DEMONSTRATION`. It uses controlled synthetic JSON fixtures and PostgreSQL tables. No scraping, live feeds, or unauthorized marketplace APIs are used.

---

## 2. Node Graph Topology & Execution Flow

```text
[1. Webhook Trigger] (POST /webhook/review-event)
         │
         ▼
[2. Payload & PII Sanitizer] (Regex mask emails, phone numbers, handles)
         │
         ▼
[3. Compute Idempotency Key] (SHA-256 hash generation)
         │
         ▼
[4. Database Idempotency Check] (Postgres query on operational_event_log)
         │
         ▼
[5. Idempotency Router (If)]
   ├── [True: Duplicate] ──► [Format Response Webhook] (Cached Outcome)
   └── [False: New]
         │
         ▼
[6. FastAPI Review Analyze] (POST /v1/review/analyze)
         │
         ▼
[7. FastAPI Decision Evaluate] (POST /v1/decision/evaluate)
         │
         ▼
[8. Decision Switch Router]
   ├── [P1_CRITICAL / P2_HIGH] ──► [9. Insert Human Review Case] ──┐
   │                                                               │
   └── [P3_MONITORING / P4_INFO] ──────────────────────────────────┼─► [10. Insert Operational Event Log]
                                                                   │
                                                                   ▼
                                                 [11. Insert Workflow Execution Metrics]
                                                                   │
                                                                   ▼
                                                 [12. Format Response Webhook]
```

---

## 3. Node Specification & Responsibilities

| # | Node Name | Type | Key Responsibility |
|---|---|---|---|
| 1 | **Webhook Trigger** | `n8n-nodes-base.webhook` | Ingests JSON review event payload. |
| 2 | **Payload & PII Sanitizer** | `n8n-nodes-base.code` | Strips emails, phone numbers, and username tags. |
| 3 | **Compute Idempotency Key** | `n8n-nodes-base.code` | Computes deterministic SHA-256 hash `source_id:review_id:version`. |
| 4 | **Database Idempotency Check** | `n8n-nodes-base.postgres` | Queries `operational_event_log` for duplicate idempotency key. |
| 5 | **Idempotency Router** | `n8n-nodes-base.if` | Fast-paths duplicate replays without duplicate DB mutations. |
| 6 | **FastAPI Review Analyze** | `n8n-nodes-base.httpRequest` | Calls `/v1/review/analyze` for aspect & severity proxy inference. |
| 7 | **FastAPI Decision Evaluate** | `n8n-nodes-base.httpRequest` | Calls `/v1/decision/evaluate` for contextual PRS & reason codes. |
| 8 | **Decision Switch Router** | `n8n-nodes-base.switch` | Directs high risk (P1/P2) vs low risk (P3/P4). |
| 9 | **Insert Human Review Case** | `n8n-nodes-base.postgres` | Inserts triage ticket into `human_review_case` (`PENDING_HUMAN_REVIEW`). |
| 10 | **Insert Operational Event Log** | `n8n-nodes-base.postgres` | Writes immutable event ledger into `operational_event_log`. |
| 11 | **Insert Workflow Execution Metrics**| `n8n-nodes-base.postgres` | Records execution time, API latency, and status in `workflow_execution`. |
| 12 | **Format Response Webhook** | `n8n-nodes-base.code` | Returns standardized operational JSON payload to caller. |

---

## 4. Controlled Demonstration Fixtures

| Fixture ID | Source | Scenario | Expected PRS Tier | Routing Target | PII Sanitized? |
|---|---|---|---|---|---|
| `SYNTHETIC_P1_EVENT` | Source B | Severe chronic defect complaint (tinta bocor) | `P2_HIGH_PRIORITY` (PRS 68.62) | `HUMAN_REVIEW_QUEUE` | Yes (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`) |
| `SYNTHETIC_P2_EVENT` | Source B | Chronic order inaccuracy (salah kirim warna/ukuran) | `P2_HIGH_PRIORITY` (PRS 68.62) | `HUMAN_REVIEW_QUEUE` | N/A |
| `SYNTHETIC_P3_EVENT` | Source A | Moderate category packaging complaint (kardus penyok) | `P3_MONITORING` (PRS 45.96) | `MONITORING_LOG` | N/A |
| `SYNTHETIC_P4_EVENT` | Source B | Incidental 5-star positive review with PII | `P4_INFORMATIONAL` (PRS 10.00) | `MONITORING_LOG` | Yes (`[REDACTED_EMAIL]`, `[REDACTED_USER]`) |
