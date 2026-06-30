# Goal3158 Fixed-Radius Graph Typed Producer Metadata

Date: 2026-06-03

Verdict: `accept-with-boundary`

## Purpose

Goal3157 refreshed the v2.8 runtime-gap matrix and left the next shared RT-DBSCAN task precise: add typed producer metadata for the fixed-radius graph grouped-stream path.

Goal3158 adds that metadata to the v2.8 fixed-radius graph component front door without changing native execution:

- `point_ids`: typed result role `item_id`, dtype `uint32`
- `component_labels`: typed result role `group_key`, dtype `int64`
- `is_core`: typed result role `mask`, dtype `uint32`
- `neighbor_counts`: typed result role `payload`, dtype `uint32`

The stream kind is `adjacency_stream`, the producer primitive is `fixed_radius_graph_component_labels_3d`, and ordering is `stable_row_order`.

## What Changed

| File | Operation |
| --- | --- |
| `src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py` | Added `make_v2_8_fixed_radius_graph_component_typed_stream_contract(...)` and attached typed-stream metadata to describe/plan/run metadata. |
| `src/rtdsl/__init__.py` | Exported the typed-stream contract helper. |
| `tests/goal3158_fixed_radius_graph_typed_producer_metadata_test.py` | Added regression coverage for the helper, describe metadata, runtime metadata, and claim boundaries. |

## Boundary

This is a metadata/contract hardening goal:

- it does not change native kernels;
- it does not change RT-DBSCAN semantics;
- it does not add automatic partner selection;
- it does not authorize release, public speedup, broad RT-core speedup, whole-app speedup, or true-zero-copy wording.

Runtime metadata can observe CuPy device pointers when the columns expose them. The public buffer metadata records `data_ptr_observed` and `device_resident`; it does not expose raw pointer values. That is typed producer evidence, not a true-zero-copy release claim.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3158_fixed_radius_graph_typed_producer_metadata_test tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test tests.goal3156_rt_dbscan_v2_8_front_door_route_test tests.goal3155_fixed_radius_graph_component_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

Result: 36 tests passed.

Pod validation on `root@69.30.85.131:22063` from clean `origin/main` checkout at commit `b649b7ca`:

```bash
python -m unittest \
  tests.goal3158_fixed_radius_graph_typed_producer_metadata_test \
  tests.goal3157_v2_8_runtime_gap_rt_dbscan_front_door_refresh_test \
  tests.goal3156_rt_dbscan_v2_8_front_door_route_test \
  tests.goal3155_fixed_radius_graph_component_front_door_test \
  tests.goal3111_v2_8_segmented_typed_stream_adapter_test
```

Result: 36 tests passed.

App-level tiny grouped-stream metadata probe:

```json
{
  "column_names": ["point_ids", "component_labels", "is_core", "neighbor_counts"],
  "data_ptr_observed": {
    "component_labels": true,
    "is_core": true,
    "neighbor_counts": true,
    "point_ids": true
  },
  "device_resident_column_count": 4,
  "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
  "matches_reference": true,
  "producer_primitive": "fixed_radius_graph_component_labels_3d",
  "public_speedup_claim_authorized": false,
  "release_authorized": false,
  "status": "pass",
  "stream_kind": "adjacency_stream",
  "true_zero_copy_claim_authorized": false
}
```
