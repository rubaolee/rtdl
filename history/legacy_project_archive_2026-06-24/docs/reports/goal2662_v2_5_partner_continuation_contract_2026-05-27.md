# Goal2662: v2.5 Partner Continuation Contract

Status: first v2.5 implementation slice, local-test backed.

Date: 2026-05-27

## Purpose

This goal starts v2.5 after the accepted v2.4 completion gate.

The v2.5 purpose is to make RT-core programming easier from Python without
forcing users to write C++/CUDA/OptiX or CuPy RawKernel continuations for every
app. This first slice defines the generic continuation contract that Triton and
Numba must implement before any benchmark path can be promoted.

This is not a performance claim and not a public release. It does not add pod
evidence or replace any v2.3/v2.4 benchmark row.

## Implemented Surface

New module:

- `src/rtdsl/partner_continuation_protocol.py`

New exported API:

- `RtdlPartnerContinuationOperation`
- `RtdlPartnerContinuationSpec`
- `PartnerContinuationOverflowError`
- `v2_5_partner_continuation_contract()`
- `validate_v2_5_partner_continuation_contract()`
- `plan_v2_5_partner_continuation()`
- `execute_v2_5_partner_continuation_reference()`

New test:

- `tests/goal2662_v2_5_partner_continuation_contract_test.py`

## Generic Operations

The first accepted v2.5 operation set is deliberately small and app-agnostic:

| Operation | Behavior |
| --- | --- |
| `segmented_count_i64` | Count int64 rows per integer group id. |
| `segmented_sum_f64` | Sum float64 values per integer group id. |
| `compact_mask_i64` | Compact int64 values by a boolean mask and preserve original indices. |
| `bounded_collect_finalize_i64` | Finalize bounded int64 rows per group with fail-closed overflow. |
| `grouped_argmin_f64` | Select the lowest-score item per group with deterministic item-id tie-break. |

These operations are shared continuation behaviors. They contain no RayDB,
DBSCAN, Barnes-Hut, graph, contact, collision, robot, RTNN, LibRTS, or
Hausdorff semantics.

## Partner Direction

The planner follows the Goal2661 handoff:

```text
preferred: Triton
fallback: Numba
conformance: CuPy
portable reference: Python
```

In this first slice, Triton and Numba are descriptor-only. The Python reference
executor defines exact semantics and fail-closed behavior. A later pod-backed
goal must add real Triton/Numba kernels and measure them against the
same-contract benchmark basis.

## Boundaries

The contract blocks:

- replacing RTDL/OptiX RT traversal with Triton or Numba;
- app-specific native vocabulary;
- app-specific continuation semantics;
- CuPy RawKernel as a required user path;
- promoted performance-path status;
- public speedup claims.

The intended pipeline remains:

```text
Python app
  -> partner prepares typed columns
  -> RTDL/OptiX performs generic RT-core traversal
  -> Triton/Numba performs generic continuation/reduction/finalization
  -> Python consumes compact results
```

## Reference Semantics

The local Python reference executor is intentionally simple. It is used to pin
correctness before introducing partner kernels:

- segmented count/sum reject group ids outside `[0, group_count)`;
- compaction preserves deterministic source indices;
- grouped argmin breaks ties by smaller item id;
- bounded collect raises `PartnerContinuationOverflowError` with
  `failure_mode=fail_closed_overflow; partial_result_returned=False` before
  any partial output is accepted.

The executor also emits phase-timing validation metadata. It does not authorize
RT-core speedup wording.

## Validation

Run:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2662_v2_5_partner_continuation_contract_test
```

Expected:

```text
Ran 8 tests
OK
```

## Next Work

The next v2.5 goal should implement the first real Triton continuation kernel
for one of these generic operations, most likely `segmented_sum_f64` or
`compact_mask_i64`, then compare it with:

- the Python reference semantics;
- existing CuPy conformance paths where available;
- the accepted benchmark phase contract for the selected pilot app.

No benchmark row should be promoted until the Triton/Numba path preserves the
current same-contract RT-vs-Embree performance basis.
