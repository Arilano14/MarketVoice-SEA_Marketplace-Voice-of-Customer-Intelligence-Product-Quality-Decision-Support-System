# Raw Data Landing Zone Policy

* **Immutability**: Files in `data/raw/` must remain unchanged after landing.
* **Git Protection**: All raw dataset files (*.csv, *.tsv, *.json, *.zip) are strictly gitignored to comply with redistribution terms.
* **Checksum Registration**: Run `python scripts/data_acquisition/register_dataset.py` after placing raw competition dataset files here.
