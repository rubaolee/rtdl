# Goal1305: v1.5 Grouped Reduction Contract Plan

Date: 2026-05-05

## Purpose

Goal1305 tightens the next v1.5 blocker before more native implementation
work. The project already has pod-verified generic wrappers for scalar
`ANY_HIT + COUNT_HITS` and fixed-radius `REDUCE_INT(COUNT)` threshold paths.
The remaining app-specific rows need grouped output contracts, not new
primitive names.

This is an internal design gate. It does not authorize public NVIDIA speedup
wording and does not require a pod.

## Contract Decision

Grouping is a result layout and keying rule, not a new stable primitive.

Stable reduction primitive names remain:

```text
COUNT_HITS
REDUCE_FLOAT(MIN)
REDUCE_FLOAT(MAX)
REDUCE_FLOAT(SUM)
REDUCE_INT(COUNT)
REDUCE_INT(SUM)
```

`COLLECT_K_BOUNDED` remains experimental and blocked until overflow,
truncation, and failure behavior are reviewed.

## Deferred Rows and Unblockers

| App | Deferred subpath | Contract to define | What unblocks implementation |
| --- | --- | --- | --- |
| `robot_collision_screening` | `prepared_pose_flags` | `ANY_HIT` plus grouped `REDUCE_INT(COUNT)` with `grouped_threshold_bool` layout | OptiX and Embree expose per-pose count output; app maps count `> 0` to flag. |
| `database_analytics` | `sales_risk_grouped_count` | grouped `REDUCE_INT(COUNT)` | Generic numeric predicate lowering plus grouped int64 count output. |
| `database_analytics` | `sales_risk_grouped_sum` | grouped `REDUCE_INT(SUM)` | Generic numeric predicate lowering plus grouped int64 payload sum output. |
| `polygon_pair_overlap_area_rows` | `exact_area_sum` | grouped `REDUCE_FLOAT(SUM)` | Float64-preferred result layout and abs/rel tolerance schema. |
| `polygon_set_jaccard` | `chunked_candidate_scoring` | experimental `COLLECT_K_BOUNDED` plus grouped `REDUCE_FLOAT(SUM)` | Explicit no-silent-truncation behavior, overflow/failure policy, and scoring tolerance. |

## Inventory Correction

`robot_collision_screening / prepared_pose_flags` previously used
`GROUPED_ANY_BOOL` as a placeholder. Goal1305 removes that placeholder from the
machine-readable inventory. The intended lowering is:

```text
input primitive: ANY_HIT
reduction primitive: REDUCE_INT(COUNT)
group key: pose_id
result layout: grouped_threshold_bool
boolean rule: count > 0
```

This preserves the Goal1042/Goal1255/Goal1274 primitive boundary and avoids
silently expanding the v1.5 stable ABI.

## Machine-Readable Gate

Added:

```text
src/rtdsl/grouped_reduction_contracts.py
tests/goal1305_v1_5_grouped_reduction_contract_test.py
```

Exported APIs:

```text
v1_5_grouped_reduction_contracts()
validate_v1_5_grouped_reduction_contracts()
```

## Next Engineering Slice

The next implementation step should choose one grouped contract and implement
it end-to-end behind the generic API. The safest order is:

1. Robot pose flags as grouped `REDUCE_INT(COUNT)` because it is closest to the
   already pod-verified `ANY_HIT + COUNT_HITS` path.
2. DB grouped count/sum because OptiX already has app-specific compact summary
   concepts, but it needs an app-name-free wrapper.
3. Polygon float sum only after tolerance/result-shape review.
4. Jaccard bounded collection remains diagnostic until `COLLECT_K_BOUNDED`
   policy is reviewed.

## Verification

Planned local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1304_v1_5_generic_migration_inventory_test \
  tests.goal1305_v1_5_grouped_reduction_contract_test
```
