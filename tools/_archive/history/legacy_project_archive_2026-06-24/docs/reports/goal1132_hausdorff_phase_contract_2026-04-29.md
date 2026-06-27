# Goal1132 Hausdorff Phase Contract

Date: 2026-04-29

## Scope

Goal1132 improves local pre-cloud readiness for the Hausdorff app by adding
phase metadata to the app-level true RT-core threshold-decision path and the
native Embree directed-summary path.

This does not repair the Hausdorff public speedup baseline contract. The
existing analytic tiled oracle is still too cheap to serve as a meaningful
same-semantics speed baseline. Hausdorff remains a capability/parity candidate
until a separate benchmark contract is designed or a cloud run is explicitly
scoped as non-public-wording evidence.

## Implementation

- `examples/rtdl_hausdorff_distance_app.py` now records `run_phases`.
- OptiX `directed_threshold_prepared` records:
  `input_construction_sec`, `optix_prepare_sec`, `optix_query_sec`,
  `python_postprocess_sec`, and `validation_sec`.
- Each directed threshold result also records its local prepare/query phase
  split.
- Embree `directed_summary` records `native_directed_summary_sec` and
  `validation_sec`.
- Row-returning modes record `query_and_materialize_sec` and
  `python_reduction_sec`.

## Local Evidence

| Artifact | Mode | Scale | Key result |
|---|---|---:|---|
| `docs/reports/goal1132_hausdorff_local_embree_directed_summary_2026-04-29.json` | Embree directed summary | 1000 copies / 4000 points per side | native directed summary phase recorded |
| `docs/reports/goal1132_hausdorff_threshold_dry_run_2026-04-29.json` | OptiX threshold dry-run contract | 20000 copies / 80000 points per side | dry-run still uses analytic tiled oracle |

The dry-run confirms the same unresolved issue from Goal1067: the CPU reference
is analytic and intentionally tiny. Therefore, this goal improves measurement
readiness but does not authorize a pod speedup claim.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1132_hausdorff_phase_contract_test \
  tests.goal879_hausdorff_threshold_rt_core_subpath_test \
  tests.goal957_graph_hausdorff_native_continuation_metadata_test \
  tests.goal722_embree_hausdorff_summary_test \
  tests.goal505_v0_8_app_suite_test \
  tests.goal208_nearest_neighbor_examples_test -v

Ran 25 tests in 1.117s
OK
```

## Boundary

Accepted wording:

> Hausdorff threshold-decision and Embree directed-summary paths now expose
> app-level phase timing for future cloud review.

Forbidden wording:

- Do not claim exact Hausdorff distance is RTX accelerated.
- Do not claim KNN-row output or nearest-neighbor ranking speedup.
- Do not claim a Hausdorff public RTX speedup until a meaningful
  same-semantics baseline contract exists and is reviewed.
- Do not use the analytic tiled oracle timing as a public speed baseline.
