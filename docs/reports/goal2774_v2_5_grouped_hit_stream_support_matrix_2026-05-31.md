# Goal2774 - v2.5 Grouped Hit-Stream Support Matrix Declaration

Date: 2026-05-31

## Purpose

Goal2774 records the API/support-matrix shape for the grouped hit-stream
reducers proven in Goals2771 and 2772. The goal is not to add another
performance result. It is to make the v2.5 partner contract honest about which
partner can currently consume the event-ordered RT hit stream.

## Contract Addition

New generic continuation operation:

`hit_stream_grouped_ray_id_primitive_i64`

Inputs:

- `ray_ids`
- `primitive_ids`
- `row_count`
- `hit_event_count`
- `overflow`
- `group_count`

Outputs:

- `group_hit_counts`
- `group_primitive_id_sum`
- `group_primitive_id_xor`
- `group_primitive_id_min`
- `group_primitive_id_max`
- `group_first_hit_row_index`
- `group_last_hit_row_index`
- `group_first_primitive_id`
- `group_last_primitive_id`

Semantics:

- group event-ordered RT hit-stream rows by generic `ray_id`
- reduce nonnegative `primitive_id` rows with count/sum/xor/min/max
- preserve first/last primitive ids by stored hit-stream row order, not by
  sorted group order
- report empty groups with signed `-1` sentinels for min/max/first/last fields
- fail closed if the native producer reports overflow

This vocabulary is intentionally generic. It does not name RayJoin, DBSCAN,
Hausdorff, RTNN, or any application.

## Support Matrix Change

The v2.5 support matrix is now operation-specific:

| Partner | Status for `hit_stream_grouped_ray_id_primitive_i64` | Reason |
| --- | --- | --- |
| `python_reference` | `reference_contract` | CPU reference semantics exist for correctness and review. |
| `triton` | `unsupported_fail_closed` | No Triton kernel currently consumes the event-ordered native hit stream. |
| `numba` | `unsupported_fail_closed` | No Numba kernel currently consumes the event-ordered native hit stream. |
| `cupy_conformance` | `preview_not_promoted` | Goals2771-2772 proved a CuPy preview consumer for the event-ordered grouped hit stream. |

This fixes the earlier over-broad matrix shape where every operation appeared to
have a Triton preview row. Triton remains the primary v2.5 partner direction for
the established continuation operations. The grouped hit-stream reducer is a
CuPy preview only until a Triton or Numba consumer is implemented and tested.
The generic planner now skips unsupported Triton/Numba cells for this operation
and selects the CuPy preview only when `cupy`/`cupy_conformance` is explicitly
available.
The hit-stream transfer planner also reports this operation as
`cuda_descriptor_preview` for `cupy_conformance`, rather than the descriptor-only
status used for CuPy cells without executable evidence.

## Boundary

Goal2774 does not authorize:

- no public speedup claims
- true zero-copy claims
- release readiness
- partner replacement of RTDL/OptiX traversal
- app-specific primitive semantics inside the engine or generic partner contract

The result is a contract/support declaration aligned with existing evidence,
not a promotion of the path to a release-grade performance primitive.
For this operation, Triton and Numba fail closed until kernels exist.

## Files Changed

- `src/rtdsl/partner_continuation_protocol.py`
- `src/rtdsl/v2_5_partner_support_matrix.py`
- `src/rtdsl/hit_stream_handoff.py`
- `src/rtdsl/__init__.py`
- `tests/goal2662_v2_5_partner_continuation_contract_test.py`
- `tests/goal2671_v2_5_preview_gate_test.py`
- `tests/goal2696_v2_5_partner_support_matrix_test.py`
- `tests/goal2774_v2_5_grouped_hit_stream_support_matrix_test.py`

## Validation Plan

Required local checks:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2671_v2_5_preview_gate_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2774_v2_5_grouped_hit_stream_support_matrix_test
```

Recommended continuity checks:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal2771_hit_stream_event_ordered_grouped_reduction_consumer_test \
  tests.goal2772_hit_stream_event_ordered_grouped_richer_reductions_test
```

The Goal2771/2772 live CUDA cases remain hardware-dependent and should be
treated as pod evidence only when the OptiX library and CUDA partner stack are
available.
