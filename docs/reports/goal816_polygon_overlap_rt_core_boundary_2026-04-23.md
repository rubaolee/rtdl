# Goal 816: Polygon Overlap RT-Core Boundary

Date: 2026-04-23

Status: complete

## Problem

The polygon overlap apps are useful public examples, but their acceleration
boundary is CPU/Embree native-assisted rather than NVIDIA RT-core:

- `examples/rtdl_polygon_pair_overlap_area_rows.py`
- `examples/rtdl_polygon_set_jaccard.py`

Both apps use Embree for LSI/PIP positive candidate discovery, then keep exact
grid-cell area or set-area/Jaccard refinement in CPU/Python. They do not expose
OptiX and should not enter RTX cloud claim batches.

## Change

Added `--require-rt-core` to both apps. The flag fails immediately with a clear
message:

```text
no OptiX RT-core surface today
```

Normal CPU and Embree runs remain unchanged.

The app payloads now include:

- `rt_core_accelerated: false`
- `optix_performance.class: not_optix_exposed`

Docs were refreshed in:

- `docs/app_engine_support_matrix.md`
- `docs/tutorials/segment_polygon_workloads.md`

## Current Status

| App | Embree status | OptiX/RTX status |
| --- | --- | --- |
| `polygon_pair_overlap_area_rows` | native-assisted candidate discovery plus exact CPU area refinement | no OptiX app surface |
| `polygon_set_jaccard` | native-assisted candidate discovery plus exact CPU set-area/Jaccard refinement | no OptiX app surface |

## Required Future Work

Promotion requires a real OptiX surface with:

- traversal-backed candidate discovery;
- bounded exact-refinement policy;
- compact summary output where possible;
- local correctness gate;
- phase-clean RTX profiler before cloud claim review.

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal816_polygon_overlap_rt_core_boundary_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile examples/rtdl_polygon_pair_overlap_area_rows.py examples/rtdl_polygon_set_jaccard.py tests/goal816_polygon_overlap_rt_core_boundary_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal adds honesty gates and documentation. It does not add OptiX polygon
overlap execution and does not authorize any polygon-overlap NVIDIA RT-core
performance claim.
