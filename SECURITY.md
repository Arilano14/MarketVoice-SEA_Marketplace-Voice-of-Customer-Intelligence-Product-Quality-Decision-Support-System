# Security & Responsible Data Policy — MarketVoice SEA

---

## 1. Security Overview

MarketVoice SEA is an applied data intelligence and decision support system. Maintaining high standards of security hygiene, credential isolation, and customer data privacy is a primary design principle.

---

## 2. Secrets & Credential Isolation

* **Zero Committed Secrets**: Private API keys, database passwords, OAuth secrets, and connection strings must **never** be committed to version control.
* **Environment Variables**: Local configuration parameters are managed via `.env`, which is strictly ignored by version control.
* **Public Templates**: Use `.env.example` as the canonical reference template containing placeholder values only.
* **Automated Scans**: Pre-commit and pre-release audits enforce zero credential leakage across all source files, SQL migrations, and workflow definitions.

---

## 3. Data Governance & Privacy Responsibility

* **No Production Customer PII**: The repository does not store real-world Personal Identifiable Information (PII).
* **Automated Sanitization**: Inbound review payloads pass through deterministic regex-based PII masking (`[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_USER]`) prior to storage.
* **Synthetic Demonstrations**: All operational integration workflows (e.g., n8n webhook triage) utilize explicitly documented synthetic test fixtures (`SYNTHETIC_OPERATIONAL_DEMONSTRATION`).
* **Source Dataset Provenance**: Underlying research datasets are governed per project data governance policies and stored locally.

---

## 4. Vulnerability Reporting & Responsible Disclosure

If you discover a potential security issue, credential exposure, or data handling vulnerability:

1. **Do NOT** disclose the issue publicly through GitHub Issues, pull requests, or public discussions.
2. Submit a confidential report detailing:
   * Description and location of the vulnerability.
   * Specific steps to reproduce the issue.
   * Potential security or privacy impact.
3. The project maintainers will review the submission, verify the findings, and apply appropriate remediation promptly.

---

## 5. Scope & Limitations

This policy applies strictly to the source code, SQL migrations, configuration templates, and documentation owned by the MarketVoice SEA project. External runtime dependencies (PostgreSQL, n8n, Python interpreters, Power BI Desktop) are governed by their respective vendor security guidelines.
