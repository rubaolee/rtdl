# Goal1939 - DB Native Phase Totals Fix

Status: db-phase-total-aggregation-fixed-release-still-blocked

Date: 2026-05-13

Hardware: `NVIDIA RTX A5000`, driver `570.195.03`

Pod: `root@194.68.245.162 -p 22102`

## Purpose

Claude Goal1936 accepted the large-scale v2 performance packet but noted a DB
control anomaly: `reported_native_db_phases_sec` contained non-zero native
counter records, while `reported_native_db_phase_totals_sec` aggregated them as
zeros. Goal1939 fixes the local totals helper so it recursively descends through
compact-summary batch groups before summing phase records, then reruns the DB
control on the RTX A5000 pod.

Artifact:
`docs/reports/goal1939_db_phase_totals_fix_pod/control_database_analytics_100000_fixed_totals.json`

## Result

The rerun uses `--backend optix --scenario all --copies 100000 --iterations 3
--output-mode compact_summary`.

| Metric | Value |
| --- | ---: |
| Prepared warm query median | 1.228439 s |
| Native operation count | 6 |
| Native traversal total | 1.047622 s |
| Native exact-filter total | 0.139906 s |
| Native output-pack total | 0.034308 s |
| Raw candidate count | 2600000 |
| Emitted count | 800017 |

The DB row remains a seconds-scale control/fallback artifact, not a v2 partner
columnar scan or grouped-reduction speedup row. This goal fixes provenance and
phase accounting quality; it does not authorize v2.0 release, whole-app speedup,
broad RT-core speedup, arbitrary PyTorch/CuPy acceleration, true zero-copy, or
package-install claims.
