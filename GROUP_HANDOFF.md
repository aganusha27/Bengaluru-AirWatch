# Group handoff

## Overview
The empirical PM2.5 project is implemented and executed. Source rows: 398,420; valid hourly records: 92,479. Eight charts and all 15 station pairs are generated. Independent verification passed. Actual metrics are in outputs/metrics/performance.json.

## Repository structure
- src/: ingestion, cleaning, summaries, spike detection, synchronization, charts and independent checks.
- data/: manifest, catalog snapshot and locally regenerated raw/processed folders.
- outputs/tables/: quality, temporal, station, coincidence and benchmark tables.
- outputs/charts/: all eight figures.
- outputs/metrics/: execution evidence and assertions.
- report/: final report, Markdown text, references and optional team details.
- main.py: pipeline; build_report.py: report; render_report.py: PDF; verify_submission.py: delivered-file checks.

## Completed tasks
Real OpenCity files acquired, hashes checked, actual schemas inspected, PySpark executed, all requested analyses completed, charts generated, outputs independently cross-checked, report generated, walkthrough and 25 viva questions prepared. Consult GITHUB_STATUS.json for verified push status and the verified artifact commit.

## Incomplete submission details
Verify group member and faculty details before submission.
The repository is private. A collaborator username was not supplied; no collaborator was added. The owner can open repository Settings → Collaborators → Add people, enter the intended GitHub username, and send the invitation. The friend must accept before cloning the private repository.

## Installation and execution
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


## Known limitations
Unequal coverage, source timezone convention unconfirmed beyond encoded offsets, no sensor quality flags, retrospective thresholds, no autocorrelation-adjusted inference, no prediction or source attribution, and no distributed performance experiment. The selected paper is a domain analysis reference. See the final report for full qualifications.

## Important files and next actions
Read README.md, ASSIGNMENT_CHECKLIST.md, PROJECT_WALKTHROUGH.md, report/final_report.md and outputs/metrics/verification.json. Inspect raw source updates before changing pinned hashes. Rebuilding the report requires a completed local run; generating its PDF additionally requires LibreOffice and Poppler. Rerun checks after any numerical or methodological change. The recorded report and chart outputs can be reviewed without installing Spark.
