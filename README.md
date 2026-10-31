# Bengaluru AirWatch

Real-data PM2.5 analysis at six Bengaluru monitoring stations using PySpark 4.0.1.

## Recorded run
- 398,420 source rows in 68,534,283 bytes.
- 92,479 valid station-hour observations.
- Eight charts and all 15 station-pair comparisons.
- Independent pandas verification: PASS.
- Actual local total excluding downloads: 126.294 seconds.

## Run
```powershell
git clone https://github.com/aganusha27/Bengaluru-AirWatch.git
cd Bengaluru-AirWatch
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
python build_report.py
python render_report.py
python verify_submission.py
```
Java 17 or 21 is required; Java 21 was used for the recorded run. Python 3.12 was used. On Linux/macOS, activate with `source .venv/bin/activate`. LibreOffice must be on PATH for `render_report.py`; alternatively pass `--soffice` with its absolute executable path. The analysis runs locally with two Spark worker threads. Permit local Java loopback communication if your sandbox requires execution outside its network isolation. No external service or API key is needed. To run analysis alone, stop after `python main.py`; the committed report is available for reading without installing a renderer.

The first run downloads six pinned OpenCity CSVs automatically and checks SHA-256 hashes. Raw files are retained locally, excluded from Git, and never replaced silently. To acquire only the files, use `python main.py --download-only`. Exact links and checksums are in `data/manifest.json`; catalog metadata are in `data/catalog_snapshot.json`.

## Outputs
`report/Bengaluru_AirWatch_Final_Report.docx` and `.pdf` contain the submission report. `outputs/tables` contains all generated CSV summaries; `outputs/charts` contains the eight figures. `outputs/metrics` records timing, configuration, source schema, checks and report evidence. `data/processed` is regenerated locally. `report/final_report.md` is a text version. The source PDFs and research full text are not redistributed.

## Method
PM2.5 concentration (µg/m³), not AQI. Honor encoded UTC timestamps, convert to IST and restrict to local 2024–2025. Reject absent/invalid/negative measurements with an audit; collapse identical selected readings; average conflicts; retain hourly means with >=3 valid distinct quarter-hours. Strictly exceed the station-specific exact 95th percentile for a spike. Compare station pairs only on actual overlapping hours. Independence expectation = marginal spike count A × count B / overlapping hours. Lift is descriptive, with no causal, transport, forecasting or significance claim.

## Performance and verification
`main.py` times actual Spark actions, not lazy transformation declarations. Warm grouped statistics use the same hourly data and equivalent count/mean/min/max/sample-SD operations in Spark and pandas, one warmup and three timed repetitions. Startup and cleaning are excluded from both benchmark timers. This small local workload does not establish cluster scalability. `src/verification.py` independently recomputes results from raw data using pandas; `verify_submission.py` validates delivered files and report evidence.

## Report regeneration
`python build_report.py` generates the DOCX and supporting Markdown after analysis. `python render_report.py --soffice /absolute/path/to/soffice --poppler /absolute/path/to/poppler/bin` renders the DOCX using an isolated LibreOffice profile and copies its PDF into `report/`. This optional step needs LibreOffice and Poppler installed from official sources. Analysis and source acquisition do not depend on those applications. Fill `report/team_details.json` using the example before rebuilding the final cover.

## Source and permissions
Dataset: https://data.opencity.in/dataset/bengaluru-hourly-air-quality-reports . Catalog license: Other (Public Domain). Attribute OpenCity, KSPCB and CPCB-labelled station sources. Access checked 31 October 2026. Raw and processed row-level files are excluded from Git; acquisition instructions and hashes allow reproduction.

## Research reference
Soni et al. (2024), Environmental Monitoring and Assessment 196:505. DOI https://doi.org/10.1007/s10661-024-12678-z . Publisher https://link.springer.com/article/10.1007/s10661-024-12678-z ; PubMed fallback https://pubmed.ncbi.nlm.nih.gov/38700603/ . This is a domain-method reference, not a Spark scalability study. See `report/references.md`.
