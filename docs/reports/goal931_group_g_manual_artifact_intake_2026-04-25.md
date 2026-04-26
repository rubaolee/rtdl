# Goal931 Group G Manual Artifact Intake

Date: 2026-04-25

## Verdict

Status: analyzer intake complete; no readiness promotion.

Goal929 captured reduced-scale manual RTX 3090 artifacts for the three remaining prepared decision apps:

- `hausdorff_distance`
- `ann_candidate_search`
- `barnes_hut_force_app`

Goal931 feeds those copied artifacts through the standard Goal762 analyzer using a replayable synthetic summary:

- `docs/reports/goal931_group_g_manual_artifact_summary_2026-04-25.json`
- `docs/reports/goal931_group_g_manual_artifact_report_2026-04-25.json`
- `docs/reports/goal931_group_g_manual_artifact_report_2026-04-25.md`

## Analyzer Result

Goal762 status: `ok`.

| App | Path | Artifact | Warm query median | Decision |
|---|---|---:|---:|---|
| `hausdorff_distance` | `directed_threshold_prepared` | ok | `0.000248 s` | hold |
| `ann_candidate_search` | `candidate_threshold_prepared` | ok | `0.000132 s` | hold |
| `barnes_hut_force_app` | `node_coverage_prepared` | ok | `0.000363 s` | hold |

## Why They Stay Held

These artifacts are useful evidence that the prepared OptiX traversal sub-paths execute on the RTX 3090 and expose the expected phase fields. They are not enough for promotion because:

- The runs were reduced-scale manual commands, not the manifest production scales.
- All three used `--skip-validation`; `validation_sec` is zero by construction.
- Same-semantics CPU/Embree baselines for the exact threshold-decision contract are not yet packaged for claim review.
- The artifacts show very short query timings, which are good as smoke evidence but too short to be reliable public performance evidence.

Current status remains:

| App | Readiness | Maturity |
|---|---:|---:|
| `hausdorff_distance` | `needs_real_rtx_artifact` | `rt_core_partial_ready` |
| `ann_candidate_search` | `needs_real_rtx_artifact` | `rt_core_partial_ready` |
| `barnes_hut_force_app` | `needs_real_rtx_artifact` | `rt_core_partial_ready` |

## Next Work

Before promotion, each app needs a production-scale, analyzer-clean RTX artifact with validation or same-semantics baseline packaging:

- Hausdorff: threshold-decision oracle/baseline at the same `copies`, `radius`, and output semantics.
- ANN: candidate-coverage baseline at the same query/build counts, radius, and threshold semantics.
- Barnes-Hut: node-coverage baseline at the same body count, radius, and threshold semantics.

These should be prepared locally before another pod is started. Do not rent a pod only to repeat the same reduced-scale manual runs.
