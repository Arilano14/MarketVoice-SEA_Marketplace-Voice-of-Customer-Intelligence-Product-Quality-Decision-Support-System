"""MarketVoice SEA ETL package (Phase 6 DEL-09).

Modules:
  extract   — CSV read with strict UTF-8 (§21), SHA256 verify (§26)
  transform — dimension mapping, row hash (§16), category/product/shop logic
  load      — 3-transaction model (§11), full refresh (§17), pre-commit checks (§12)
  pipeline  — orchestrator (steps 6.7–6.11 combined)
  report    — pipeline result reporting
"""
