# MARKETVOICE SEA — SYNTHETIC DATA & OPERATIONAL SIMULATION GOVERNANCE POLICY

**Document Version**: 1.0 (Phase 2 Hardening)  
**Phase**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
**Classification**: Data Governance Policy Specification  

---

## 1. POLICY & MANDATORY FLAGS

1. **No Raw Synthetic Mutation**: Raw datasets (`data/raw/`) are immutable source evidence. Synthetic data shall **NEVER** be mixed into raw CSV files.
2. **Scenario-Driven Operational Simulation**: Synthetic operational records (CS case tickets, SLA tracking logs, intervention events) will ONLY be designed conditionally in Phase 10/11 for workflow automation simulation.
3. **Mandatory Metadata Tags**: Every synthetic record must carry:
   - `is_synthetic = TRUE`
   - `scenario_version = 'v1.0'`
   - `source_record_key` (linking back to authentic review observation)
4. **No False Commercial Claims**: Synthetic timestamps represent `SIMULATED_OPERATIONAL_EVENT_TIME`, never real review dates. Synthetic metrics must display `[SYNTHETIC DATA EXTENSION]` banners in Power BI and API payloads.
