# Goal1131 Polygon App Phase And Summary Contract

Date: 2026-04-29

## Scope

Goal1131 improves the pre-cloud readiness of the polygon-pair overlap and
polygon-set Jaccard apps. The goal is observability and compact app output, not
public RTX promotion.

## Implementation

- `examples/rtdl_polygon_pair_overlap_area_rows.py` now reports app-level
  `run_phases`.
- `examples/rtdl_polygon_set_jaccard.py` now supports
  `--output-mode summary`, omitting the single row while preserving the exact
  Jaccard summary.
- Embree and OptiX native-assisted polygon paths now expose:
  `rt_candidate_discovery_sec` and `native_exact_continuation_sec`.
- CPU paths expose `query_and_materialize_sec` and
  `summary_postprocess_sec`.
- Existing RT claim boundaries remain unchanged:
  `rt_core_accelerated` is still `false`; `rt_core_candidate_discovery_active`
  is true only on OptiX app paths.

## Local Evidence

| Artifact | App | Backend | Copies | Candidate rows | Output rows | Key phases |
|---|---|---:|---:|---:|---:|---|
| `docs/reports/goal1131_polygon_pair_local_embree_summary_2026-04-29.json` | polygon-pair overlap | embree | 1000 | 3000 | 2000 | candidate discovery + native exact continuation |
| `docs/reports/goal1131_polygon_jaccard_local_embree_summary_2026-04-29.json` | polygon-set Jaccard | embree | 1000 | 3000 | 1 | candidate discovery + native exact continuation |

The local Embree artifacts prove that the apps expose the intended phase split
without RTX hardware. Real OptiX timing still requires a cloud RTX artifact.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1131_polygon_app_phase_contract_test \
  tests.goal732_polygon_pair_summary_output_test \
  tests.goal733_polygon_set_jaccard_scalable_embree_test \
  tests.goal816_polygon_overlap_rt_core_boundary_test \
  tests.goal877_polygon_overlap_optix_phase_profiler_test \
  tests.goal713_polygon_overlap_embree_app_test \
  tests.goal948_polygon_native_continuation_test -v

Ran 33 tests in 0.394s
OK
```

## Boundary

Accepted wording:

> Polygon overlap and Jaccard apps now expose RT candidate discovery and exact
> continuation phase splits, and Jaccard has a compact summary output.

Forbidden wording:

- Do not claim polygon overlap or Jaccard public RTX speedups from this goal.
- Do not claim monolithic GPU polygon-area overlay or monolithic GPU Jaccard.
- Do not claim exact area/Jaccard continuation is performed by NVIDIA RT cores.
- Do not promote public wording before reviewed real RTX artifacts.
