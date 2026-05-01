# Goal890 Public Matrix Sync After RTX Gates

Date: 2026-04-24

## Result

Goal890 refreshes the public app support matrix after the recent RT-core gate
work:

- Goal887 prepared decision profilers for Hausdorff, ANN, facility, and
  Barnes-Hut.
- Goal888 native road-hazard gate.
- Goal889 graph `visibility_edges` RT-core sub-path.

The machine-readable source of truth already had the updated classifications.
The public matrix and older tests were stale in several places, so this goal
syncs those public-facing records.

## Public Doc Corrections

Updated:

```text
docs/app_engine_support_matrix.md
```

Corrections:

- `graph_analytics` now documents only `visibility_edges` as an RT traversal
  candidate, while keeping BFS and triangle-count outside RT-core claims.
- `road_hazard_screening` and `segment_polygon_hitcount` now document deferred
  native RTX gates rather than pre-gate native-kernel-redesign status.
- `polygon_pair_overlap_area_rows` and `polygon_set_jaccard` now document
  `needs_real_rtx_artifact`, matching the Goal877 phase gate.

## Test Corrections

Updated stale expectations in:

```text
tests/goal816_polygon_overlap_rt_core_boundary_test.py
tests/goal820_segment_polygon_rt_core_gate_test.py
```

The tests now match the current matrix:

- polygon overlap/Jaccard: `needs_real_rtx_artifact`
- road hazard and segment hit-count: `needs_real_rtx_artifact` and
  `rt_core_partial_ready`

## Remaining Honest Limitation

`database_analytics` intentionally remains:

```text
needs_interface_tuning
```

Reason: the DB app has a real OptiX path and active cloud entries, but its
public claim still requires fresh phase-clean RTX artifacts showing that
compact-summary/native timing, not Python/interface materialization, is the
dominant measured path.

## Verification

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal816_polygon_overlap_rt_core_boundary_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal814_graph_optix_rt_core_honesty_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `50 tests OK`.

Compile check:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/app_support_matrix.py \
  tests/goal816_polygon_overlap_rt_core_boundary_test.py \
  tests/goal820_segment_polygon_rt_core_gate_test.py
```

Result: `OK`.
