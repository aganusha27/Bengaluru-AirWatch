# Assignment checklist

The eight mandatory faculty sections are addressed in the final report. Completion is supported by the executed outputs and independent checks, not just planned code. PDF and repository delivery are checked separately by verify_submission.py.

| Faculty requirement | Report section | Evidence | Status |
|---|---|---|---|
| Real-world scenario and problem statement | 1 | src/analysis.py; report/final_report.md | COMPLETE |
| Recent research paper and existing approach | 2 | report/references.md; report/final_report.md | COMPLETE |
| Objectives and proposed analysis | 3 | src/preprocessing.py; src/spike_detection.py; src/synchronization.py | COMPLETE |
| Dataset identification and preparation | 4 | data/manifest.json; outputs/tables/dataset_inventory.csv; cleaning_audit.csv | COMPLETE |
| Big Data implementation and workflow | 5 | main.py; src/*.py; outputs/metrics/performance.json | COMPLETE |
| Results, visualization and paper comparison | 6 | outputs/charts/*.png; outputs/tables/*.csv; report/final_report.md | COMPLETE |
| Performance evaluation and observations | 7 | outputs/metrics/performance.json; outputs/tables/benchmark_repeats.csv; verification.json | COMPLETE |
| Tools, responsible use and references | 8 | requirements.txt; data/catalog_snapshot.json; report/references.md | COMPLETE |

## Submission administration
Add the group member names, USNs, responsibilities and faculty guide to report/team_details.json and regenerate the cover before submission.
Private collaborator invitation requires the collaborator username. This does not change the eight technical-content completion statuses. See GITHUB_STATUS.json for verified repository status.

## Deliberate analytical scope
No ML model, causal transport claim or distributed speedup is included. These are optional methods, not missing assignment outputs. The project uses the selected paper for temporal and spatial analysis context and explains the method differences.