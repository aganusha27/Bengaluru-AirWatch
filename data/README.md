# Dataset

Six pinned 2024–2025 OpenCity resources: Bapuji Nagar, BTM Layout, Hebbal, Jayanagar 5th Block, Peenya and Silk Board. Download automatically with `python main.py --download-only`; files go in `data/raw/`.

If automated access is blocked, open the catalog URL in README.md, choose each matching resource named in `manifest.json`, click Download and save it under the exact `file` name in `data/raw/`. The manifest URL also opens the direct CSV. Rerun the command to check its hash. Do not use staging copies or replace a pinned dataset without inspection.

`manifest.json` supplies exact URLs, bytes, row counts, SHA-256 hashes and raw schema. `catalog_snapshot.json` supplies publisher and public-domain metadata. `outputs/tables/dataset_inventory.csv` supplies parsed coverage and schema compatibility; `column_completeness.csv` audits all fields. Source timestamps explicitly encode +0000; local-calendar calculations use IST. Selected schemas have concentrations rather than AQI. PM2.5, PM10, most gases and aromatics use µg/m³; CO uses mg/m³; NOx uses ppb; meteorological units are in headers.

Do not mix pollutants, fill missing measurements with zero, infer sensor timezone independently of metadata, or claim instrument validation. One one-field 2025 separator occurs in each file and is accounted for in the audit. The locally retained raw files are immutable; generated processed CSVs can be reproduced with `python main.py`.
