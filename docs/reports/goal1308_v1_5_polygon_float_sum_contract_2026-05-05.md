# Goal1308: Polygon REDUCE_FLOAT(SUM) Contract

Date: 2026-05-05

## Purpose

Goal1308 defines the v1.5 `REDUCE_FLOAT(SUM)` contract needed before polygon
exact-area and Jaccard scoring can leave app-specific continuations.

This is a design/validation slice only. It does not implement a native
float-sum backend, does not require a pod, and does not authorize public
NVIDIA speedup wording.

## Contract

Default policy:

```text
reduction primitive = REDUCE_FLOAT(SUM)
dtype = float64
abs_tol = 1e-9
rel_tol = 1e-9
determinism = backend publishes reduction order or validates within tolerance
```

For the current polygon-pair app, the authored workload is still integer-grid
unit-cell area. That means correctness must first satisfy exact integer parity
with the current oracle; float tolerance is only the future generic reduction
schema for non-integer or reordered reductions.

## Rows

| App | Subpath | Status | Contract |
| --- | --- | --- | --- |
| `polygon_pair_overlap_area_rows` | `exact_area_sum` | `design_required` | Sum `intersection_area` and `union_area` into `summary_float64_sums`; keep exact integer parity for current unit-cell oracle. |
| `polygon_set_jaccard` | `exact_score_sum` | `blocked_by_collect_k_bounded` | Sum candidate score fields only after `COLLECT_K_BOUNDED` has no-silent-truncation and overflow/failure behavior. |

## Boundary

- This is not a generic polygon overlay engine.
- This is not broad GIS acceleration.
- This is not whole-app polygon speedup wording.
- Jaccard remains diagnostic while `COLLECT_K_BOUNDED` and OptiX-slower status
  remain unresolved.

## Machine-Readable Gate

Added:

```text
src/rtdsl/float_reduction_contracts.py
tests/goal1308_v1_5_polygon_float_sum_contract_test.py
```

Exported APIs:

```text
v1_5_float_sum_reduction_contracts()
validate_v1_5_float_sum_reduction_contracts()
```

## Next Step

The next implementation slice should add a generic polygon exact-area summary
wrapper that exposes `REDUCE_FLOAT(SUM)` metadata while preserving exact
integer parity for the current unit-cell oracle. Only after that local wrapper
passes should it be copied to the pod for OptiX validation.
