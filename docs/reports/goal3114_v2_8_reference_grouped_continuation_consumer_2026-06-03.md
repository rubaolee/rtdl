# Goal3114: v2.8 Reference Grouped-Continuation Consumer

Date: 2026-06-03

Status: internal reference consumer, no native or partner promotion

## Purpose

Goal3111 created a `host_reference_contract_adapter` that bridges segmented
rows into the Goal3108 typed result-stream contract. Goal3114 adds the next
local oracle: a reference grouped-continuation consumer that executes the
adapter's continuation plan through the existing v2.5 Python reference
continuation executor.

This gives v2.8 a real executable reference path:

`SegmentedRowStream -> V28TypedResultStreamContract -> V28GroupedContinuationPlan -> v2.5 Python reference outputs`

## What Changed

Updated module:

- `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`

New exported function:

- `execute_segmented_typed_stream_reference_continuation`

The function:

1. validates the adapter,
2. reconstructs rows from segmented pages,
3. extracts typed columns by schema,
4. maps the `V28GroupedContinuationPlan` into the existing v2.5 reference
   continuation input names,
5. executes `execute_v2_5_partner_continuation_reference`,
6. returns reference outputs and preserves all non-authorizing flags.

Currently covered operations include:

- `segmented_count_i64`
- `segmented_sum_f64`
- `segmented_min_f64`
- `segmented_max_f64`
- `grouped_vector_sum_f64x2`
- `grouped_argmin_f64`
- `grouped_argmax_f64`
- `grouped_topk_f64`
- `bounded_collect_finalize_i64`
- `compact_mask_i64`

## Boundary

This is still a reference consumer only.

It is:

- not a native producer
- not a partner consumer promotion
- not a device-residency proof
- not a true-zero-copy claim
- not a release authorization
- not a public speedup claim
- not broad RT-core wording
- not hidden dispatch
- not hidden partner selection
- not app-specific native-engine behavior
- not user-defined shader injection

The returned `reference_partner` is `python_reference`, matching the existing
v2.5 reference executor.

## Validation

Local validation commands:

```powershell
py -3 -m py_compile src\rtdsl\v2_8_segmented_typed_stream_adapter.py src\rtdsl\v2_8_typed_result_stream.py src\rtdsl\__init__.py
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal3108_v2_8_typed_result_stream_contract_test tests.goal3105_v2_8_benchmark_runtime_gap_map_test
```

Observed local result:

- `py_compile`: passed
- focused unittest: 22 tests, OK

The new tests check:

- grouped argmax reference output,
- segmented sum reference output,
- top-k fail-closed behavior when `k` is missing,
- top-k deterministic output when `k` is supplied,
- claim flags remain false in reference-consumer output.

## Next Step

The next v2.8 step should select one benchmark subpath and replace either the
reference producer or reference consumer with a real native/partner
implementation that emits or consumes the same typed stream contract. That next
step will need pod validation when it touches OptiX or partner GPU execution.
