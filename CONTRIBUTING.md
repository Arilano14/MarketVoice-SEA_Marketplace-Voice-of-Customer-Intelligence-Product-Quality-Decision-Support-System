# Contributing to MarketVoice SEA

Thank you for contributing to **MarketVoice SEA** (*Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System*).

---

## 1. Governance & Data Handling Principles

* **Academic & Engineering Rigor**: All analytical contributions must adhere to reproducible, evidence-based standards.
* **No Raw or Restricted Data in Git**: Never commit raw third-party datasets, customer PII, or credentials to version control.
* **Source Isolation**: Preserve strict partitioning between datasets (e.g., Source A PRDECT-ID must not be artificially assigned to SKU-level grains).
* **Zero Mutation of Historical Facts**: Production fact tables (`fact_review`, `fact_review_issue`, `fact_decision_queue`) are immutable.

---

## 2. Development Workflow

1. **Branch Naming**: Use standard conventional branch names:
   * `feat/feature-name`
   * `fix/bug-description`
   * `docs/documentation-update`
   * `refactor/component-cleanup`
2. **Commit Messages**: Follow the Conventional Commits format (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).
3. **Local Testing**: Run the full test suite and ensure 100% pass rate before opening a pull request:
   ```powershell
   $env:PYTHONPATH = "src;.pipdeps"
   python -m pytest tests/ -v
   ```

---

## 3. Code & SQL Conventions

### Python Standards
* Adhere to PEP 8 standards with type hints across all public functions and classes.
* Use functional, responsibility-based module and function naming.
* Avoid redundant or conversational comments; use clear docstrings specifying parameters and return types.

### SQL Standards
* Schema and table references must explicitly target the `marketvoice_warehouse` schema.
* Use snake_case for all table names, column identifiers, and surrogate keys (`_sk`).
* Write deterministic, idempotent DDL and DQL scripts with Common Table Expressions (CTEs) for complex aggregations.

### Power BI & DAX Standards
* Encapsulate business logic exclusively in explicit DAX measures (avoid ad-hoc calculated columns).
* Reconcile DAX measures exactly (0.00% variance) against direct PostgreSQL warehouse queries.

---

## 4. Security & Credential Guidelines

* **Zero Hardcoded Secrets**: Load all database passwords, host configurations, and API keys via environment variables or local `.env` files.
* **Configuration Template**: Update `.env.example` with placeholders whenever introducing new environment variables.
* **PII Protection**: Ensure all inbound text payloads pass through regex masking prior to persistence.
