# MARKETVOICE SEA — ISSUE / ASPECT ANNOTATION PROTOCOL

**Document Version**: 1.0 (Phase 2 Hardening)  
**Phase**: Phase 2 (Dataset Forensic Audit & Data Readiness)  
**Classification**: Research Methodology Specification  

---

## 1. READINESS CLASSIFICATION

- `ISSUE_DISCOVERY_READINESS = READY`: Raw review text is fully ready for unsupervised topic discovery and keyword extraction (e.g., LDA, BERTopic, TF-IDF clustering).
- `SUPERVISED_ISSUE_CLASSIFICATION_READINESS = REQUIRES_HUMAN_ANNOTATION`: Gold multi-label aspect/issue annotations do **NOT** exist in raw datasets. Synthetic or LLM/zero-shot outputs will **NOT** be treated as ground truth.

---

## 2. 7-STEP HUMAN ANNOTATION PROTOCOL (FUTURE PHASES)

To establish ground truth for multi-label aspect classification in Phase 9, the following 7-step protocol will be executed:

1. **Step 1 — Stratified Pilot Sampling**:
   - Draw a reproducible sample of $N = 1,000$ authentic reviews stratified across dataset source, customer rating (1 to 5), category, and review length.
2. **Step 2 — Open Coding / Pilot Issue Discovery**:
   - Perform qualitative open coding on 150 sampled reviews to extract candidate customer complaint facets.
3. **Step 3 — Candidate Taxonomy Formulation**:
   - Draft candidate issue taxonomy (e.g., Packaging Damage, Product Defect, Order Accuracy, CS Unresponsiveness, Shipping Delay).
4. **Step 4 — Ambiguity Review & Class Merging**:
   - Resolve overlapping or ambiguous issue definitions; establish explicit inclusion/exclusion guidelines per candidate aspect.
5. **Step 5 — Freeze Issue Taxonomy v1.0**:
   - Lock formal multi-label taxonomy schema prior to full annotation.
6. **Step 6 — Human Multi-Label Annotation**:
   - Annotate the 1,000 sampled reviews with binary multi-label vectors.
7. **Step 7 — Inter-Annotator Consistency Verification**:
   - Re-annotate a 15% random subset to compute Cohen's / Fleiss' Kappa ($\kappa \ge 0.75$ threshold).
