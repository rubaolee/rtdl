# Goal877 Polygon Overlap OptiX Phase Profiler

- date: `2026-04-24`
- apps: `polygon_pair_overlap_area_rows`, `polygon_set_jaccard`
- status: `local_phase_contract_complete`

## Work Completed

Goal877 adds a phase profiler for the Goal876 OptiX native-assisted polygon
overlap/Jaccard app surfaces.

New script:

```text
scripts/goal877_polygon_overlap_optix_phase_profiler.py
```

Modes:

- `--mode dry-run`: validates schema and CPU reference locally without OptiX.
- `--mode optix`: runs OptiX LSI/PIP candidate discovery, then CPU exact
  area/Jaccard refinement, and checks parity against CPU reference.

Generated local dry-run artifacts:

- `docs/reports/goal877_pair_overlap_phase_dry_run_2026-04-24.json`
- `docs/reports/goal877_jaccard_phase_dry_run_2026-04-24.json`

## Phase Contract

The profiler records:

- `input_build_sec`
- `cpu_reference_sec`
- `optix_candidate_discovery_sec`
- `cpu_exact_refinement_sec`
- `parity_vs_cpu`
- `rt_core_candidate_discovery_active`

This directly addresses the Goal876 boundary: OptiX can own candidate
discovery, while CPU/Python still owns exact grid-cell area/Jaccard refinement.
The Jaccard profiler calls the app's shared
`_exact_jaccard_rows_for_candidates(...)` helper so phase timing cannot drift
from the app's exact-refinement implementation.

## Manifest Refresh

The Goal759 RTX cloud benchmark manifest now includes deferred entries:

- `polygon_pair_overlap_optix_native_assisted_phase_gate`
- `polygon_set_jaccard_optix_native_assisted_phase_gate`

They are deferred, not active benchmarks. Promotion requires a real RTX
artifact, reviewed phases, and claim language limited to candidate discovery.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal877_polygon_overlap_optix_phase_profiler_test tests.goal759_rtx_cloud_benchmark_manifest_test tests.goal822_rtx_cloud_manifest_claim_boundary_test tests.goal713_polygon_overlap_embree_app_test tests.goal816_polygon_overlap_rt_core_boundary_test tests.goal705_optix_app_benchmark_readiness_test tests.goal687_app_engine_support_matrix_test tests.goal803_rt_core_app_maturity_contract_test tests.goal512_public_doc_smoke_audit_test
```

Result: `53 tests OK`.

```text
PYTHONPATH=src:. python3 -m py_compile scripts/goal877_polygon_overlap_optix_phase_profiler.py tests/goal877_polygon_overlap_optix_phase_profiler_test.py scripts/goal759_rtx_cloud_benchmark_manifest.py tests/goal759_rtx_cloud_benchmark_manifest_test.py
git diff --check
```

Result: both passed.

## Boundary

This goal does not authorize full polygon-area/Jaccard RTX speedup claims. It
only gives the next cloud session a phase-clean way to test the
native-assisted OptiX candidate-discovery slice.
