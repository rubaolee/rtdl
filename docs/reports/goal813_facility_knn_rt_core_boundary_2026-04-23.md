# Goal 813: Facility KNN RT-Core Boundary

Date: 2026-04-23

Status: complete

## Decision

`examples/rtdl_facility_knn_assignment.py` remains a CPU, Embree, and SciPy
baseline app. It is not promoted to an OptiX or NVIDIA RT-core app in this
goal.

The reason is semantic, not just implementation backlog. The app needs ranked
nearest-depot assignments:

- each customer needs one or more nearest depots;
- output rows include `neighbor_rank`;
- tie and distance ordering are part of correctness;
- summary mode still depends on the rank-1 depot.

The prepared OptiX fixed-radius threshold primitive used by recent spatial
summary work answers a different question: whether a query has enough neighbors
inside a radius, or how many bounded hits exist. It cannot by itself emit KNN
ordering or a nearest-depot ranking. Substituting that primitive for this app
would be an overclaim.

## Current Support

| Engine | App status | Claim boundary |
| --- | --- | --- |
| CPU/Python | supported | correctness oracle |
| Embree | supported | CPU BVH/RT-style high-performance implementation |
| SciPy | supported | external baseline |
| OptiX | not exposed by app CLI | no NVIDIA RT-core claim |
| Vulkan | not exposed by app CLI | no claim |
| HIPRT | not exposed by app CLI | no claim |
| Apple RT | not exposed by app CLI | no claim |

## What Would Be Required For Promotion

A future OptiX path must implement or prove a traversal-friendly KNN ranking
design. Acceptable directions include:

- RT traversal to generate bounded candidate sets plus a native device-side
  distance/ranking reducer;
- an iterative radius expansion design with deterministic rank completion and
  explicit phase accounting;
- a new prepared KNN primitive that returns compact nearest IDs/distances
  without Python row materialization dominating the app.

Unacceptable shortcuts:

- treating fixed-radius threshold counts as KNN;
- using CUDA-through-OptiX KNN rows and labeling it as RT-core traversal;
- exposing `--backend optix` before local correctness and phase-clean profiling
  gates exist.

## Changes

- Updated `src/rtdsl/app_support_matrix.py` to spell out the KNN ranking gap in
  app support, OptiX performance, benchmark readiness, and RT-core maturity.
- Updated `docs/app_engine_support_matrix.md` with the same boundary.
- Added `tests/goal813_facility_knn_rt_core_boundary_test.py` to prevent silent
  promotion of Facility KNN into RTX claim tables.

## Verification

Run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal813_facility_knn_rt_core_boundary_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test
python3 -m py_compile src/rtdsl/app_support_matrix.py tests/goal813_facility_knn_rt_core_boundary_test.py
git diff --check
```

Expected result: all tests pass and no whitespace errors.

## Release Boundary

This goal improves honesty and release safety. It does not add a new OptiX
runtime path and does not authorize any Facility KNN NVIDIA RT-core performance
claim.
