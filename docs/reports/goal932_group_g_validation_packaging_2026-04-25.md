# Goal932 Group G Validation Packaging

Date: 2026-04-25

## Verdict

Status: local validation packaging improved; no readiness promotion.

Goal931 showed that the manual Group G RTX artifacts are analyzer-clean but not promotion-ready because they used `--skip-validation`. Goal932 removes that blocker for the next real RTX batch by making the held prepared-decision commands validation-capable before the pod starts.

## Changes

- Added `expected_tiled_candidate_threshold(...)` to `examples/rtdl_ann_candidate_app.py`.
- Updated `scripts/goal887_prepared_decision_phase_profiler.py` so ANN dry-run and validation use the tiled oracle instead of the quadratic `candidate_threshold_oracle(...)`.
- Changed skipped validation semantics from fake `matches_oracle: true` to `matches_oracle: null`.
- Removed `--skip-validation` from the future RTX manifest commands for:
  - `hausdorff_distance` / `directed_threshold_prepared`
  - `ann_candidate_search` / `candidate_threshold_prepared`
  - `barnes_hut_force_app` / `node_coverage_prepared`
- Kept `facility_knn_assignment` unchanged because it is already promoted through Goal920 and its current manifest path remains intentionally skip-validation based on the reviewed same-scale CPU oracle baseline.

## Local Evidence

The ANN production-scale dry-run oracle is now cheap:

```text
PYTHONPATH=src:. python3 scripts/goal887_prepared_decision_phase_profiler.py \
  --scenario ann_candidate_coverage \
  --mode dry-run \
  --copies 20000 \
  --iterations 1 \
  --output-json build/goal932_ann_dryrun.json
```

Result:

```json
{"query_count": 60000, "covered_query_count": 60000, "within_candidate_radius": true}
```

## Boundary

This goal prepares the next cloud run. It does not promote Hausdorff, ANN, or Barnes-Hut. Those apps still need a production-scale RTX artifact with validation enabled and analyzer/intake review before any readiness change.
