# Goal3117: v2.8 Explicit Partner-Consumer Front Door

Date: 2026-06-03

Status: internal dry-run/bridge contract, pod execution pending

## Purpose

Goal3114 gave the segmented typed-stream adapter a Python reference consumer.
Goal3117 adds the next local bridge: an explicit partner-consumer front door
over the same typed stream contract.

The point is not to claim performance on Windows. The point is to define the
front-door mapping that a pod run can execute later without hidden dispatch or
hidden host materialization.

## What Was Added

Updated module:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`

New exported functions:

- `plan_segmented_typed_stream_partner_continuation`
- `execute_segmented_typed_stream_partner_continuation`

New exported constants:

- `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_STATUS`
- `V2_8_SEGMENTED_TYPED_STREAM_PARTNER_CONSUMER_SUPPORTED_OPERATIONS`

Supported dry-run/execution operations:

- `segmented_count_i64`
- `segmented_sum_f64`
- `grouped_vector_sum_f64x2`
- `grouped_argmin_f64`
- `grouped_argmax_f64`
- `grouped_topk_f64`
- `bounded_collect_finalize_i64`

## Design Boundary

The bridge is explicit by construction:

- callers must name the partner,
- `partner="auto"` and empty partner names fail closed,
- dry-run returns the required partner-column mapping,
- real execution requires caller-supplied partner columns,
- the bridge does not secretly materialize host rows into partner tensors,
- unsupported operations are visible in dry-run metadata,
- all release/speedup/RT-core/zero-copy/hidden-dispatch flags remain false.

This means local Windows can validate the mapping and fail-closed behavior
without Torch, CuPy, Numba, or a pod. Real partner execution remains a hardware
validation step.

## Validation

Local validation commands:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed local result: `py_compile` passed, and the focused unittest command
ran 25 tests successfully.

The new tests check:

- explicit partner dry-run mapping for grouped argmax,
- no automatic partner selection,
- no hidden host materialization when `partner_columns` are missing,
- unsupported operation visibility for `compact_mask_i64`,
- all non-authorizing flags remain false.

## Next Step

The next step requires hardware: provide Torch/Numba/CuPy partner columns on a
CUDA-capable pod or local Linux GPU environment and execute one supported
operation through this front door, then compare against the Goal3114 Python
reference consumer.
