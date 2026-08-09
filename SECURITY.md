# Security Policy — MarketVoice SEA

---

## 1. SECRETS & CREDENTIALS POLICY

MarketVoice SEA strictly prohibits committing secrets, private credentials, database passwords, or API keys to version control.

* Environment variables must be declared in `.env` (gitignored).
* Use `.env.example` as a template for public reference.
* Automated secret scans are conducted prior to Phase Gate transitions.

---

## 2. REPORTING A VULNERABILITY

If you discover a security vulnerability or credential leak in this repository:
1. Do **NOT** open a public GitHub issue.
2. Report the vulnerability privately to the project maintainers.
3. Include detailed steps to reproduce the security concern.
