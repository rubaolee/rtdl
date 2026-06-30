# Handoff: Gemini Review for Goal3191 Dense Grouped-Count Device Columns

Please perform an independent read-only Gemini review of Goal3191 at current
`main`.

Write the review to:

`docs/reviews/goal3192_gemini_review_goal3191_dense_grouped_count_device_columns_2026-06-03.md`

Do not leave placeholder answer sections. Answer each question explicitly after
checking the files.

## Context

Goal3191 extends the Goal3185/3187/3189 device pair-column chain with a generic
dense grouped-count device output.

The new native ABI is:

`rtdl_optix_columnar_device_payload_grouped_count_i64_device_columns_with_capacity`

It reuses the existing generic device-column grouped-count CUDA kernel, but
returns a native-owned dense CUDA `count[group_id]` column instead of compact
host rows.

The Python front door currently exercised by the pod is:

`OptixNativeDevicePairColumnOutput.grouped_count_by_left_id_device_columns(group_capacity=...)`

It returns:

`OptixNativeDeviceGroupedCountI64Output`

The output can be wrapped as a CuPy view through `as_cupy_counts()`.

## Files To Review

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `tests/goal3191_dense_grouped_count_device_columns_test.py`
- `docs/reports/goal3191_dense_grouped_count_device_columns_2026-06-03.md`
- `docs/reports/goal3191_pod_dense_grouped_count_device_columns_2026-06-03.json`

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3191_dense_grouped_count_device_columns_test tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test
```

## Questions To Answer

1. Does Goal3191 remain app-agnostic in the native layer, with no RayJoin or
   app-specific native logic?
2. Does the native path reuse the existing grouped-count kernel rather than
   adding a new app-specific kernel?
3. Is the dense output boundary correct: native-owned CUDA `count[group_id]`
   column, direct-address `group_capacity`, no compact sparse row stream, and no
   exact intersection witness rows?
4. Does Python provide safe ownership/release and a bounded CuPy view via
   `cp.cuda.UnownedMemory`?
5. Is the direct-address key-capacity limitation documented and tested, including
   the pod negative probe where `group_capacity=64` overflows for IDs `200..215`?
6. Does the pod artifact support only bounded claims: live authored smoke, dense
   device count residency, CuPy validation copy only, no true zero-copy claim, no
   release authorization, no public speedup claim, and no RayJoin-specific native
   logic?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`, because the implementation is
real and pod-proven for the bounded dense count output, while resident sparse
compaction, device-to-device downstream continuation, public speedup claims,
true zero-copy claims, and release authorization remain out of scope.
