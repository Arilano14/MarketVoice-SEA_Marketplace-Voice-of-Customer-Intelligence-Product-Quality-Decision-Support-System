# Contributing to MarketVoice SEA

Thank you for your interest in contributing to **MarketVoice SEA** (*Marketplace Voice-of-Customer Intelligence & Product Quality Decision Support System*).

---

## 1. CODE OF CONDUCT & GOVERNANCE

* **Academic & Research Rigor**: All contributions must respect the independent academic positioning of the project.
* **No Third-Party PII or Raw Competition Data**: Never commit raw competition dataset files, user PII, or secret API keys to Git repositories.
* **Function-Based Structure**: Follow the established repository layout in `docs/engineering/repository_structure.md`.

---

## 2. DEVELOPMENT WORKFLOW

1. **Branch Naming**: Use Conventional branch names (e.g., `feat/feature-name`, `chore/phase-01-setup`, `docs/update-readme`). Avoid unprofessional or generic names (e.g., `test1`, `temp`).
2. **Commit Messages**: Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, `chore:`).
3. **Code Style**: Adhere to PEP 8 standards for Python code. Ensure docstrings are provided for all public modules and functions.
4. **Testing**: Run pytest suites locally before opening a pull request:
   ```powershell
   pytest tests/
   ```
