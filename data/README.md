# MarketVoice SEA — Data Directory Governance

This directory follows a multi-tier data architecture:

```
data/
├── raw/         # Immutable raw competition dataset landing (Gitignored)
├── interim/     # Intermediate ETL staging outputs (Gitignored)
├── processed/   # Validated analytical warehouse datasets (Gitignored)
└── metadata/    # Dataset manifests, SHA256 checksums, and lineage records
```

## Tier Governance Rules
1. **data/raw/**: Read-only source landing area. Never manually edit, patch, or overwrite raw files.
2. **data/interim/**: Temporary ETL staging zone.
3. **data/processed/**: Final transformed database export tables and analytical marts.
4. **data/metadata/**: Contains source registration manifests (`source_manifest.csv`) and checksum audits.
