# Handoff: Gemini Review for Goal3193 Compact Grouped-Count Device Columns

Please perform an independent read-only Gemini review of Goal3193 at current
`main`.

Write the review to:

`docs/reviews/goal3194_gemini_review_goal3193_compact_grouped_count_device_columns_2026-06-03.md`

Do not leave placeholder answer sections. Answer each question explicitly after
checking the files.

## Context

Goal3191 added dense direct-address grouped-count device columns. Goal3193 builds
on that with compact grouped-count device columns:

- native ABI:
  `rtdl_optix_columnar_device_payload_grouped_count_i64_compact_device_columns_with_capacity`
- release ABI:
  `rtdl_optix_release_device_grouped_count_i64_compact_columns`
- Python front door:
  `OptixNativeDevicePairColumnOutput.grouped_count_by_left_id_compact_device_columns(...)`
- Python output:
  `OptixNativeDeviceGroupedCountI64CompactOutput`

The compact output keeps two SoA columns resident on CUDA:

- `group_key[]`
- `count[]`

It materializes only the row-count scalar on host so Python can know the valid
prefix length. It does not materialize the compact columns on host except in the
pod validation script, where CuPy copies are used only to compare against the
exact-row oracle.

## Files To Review

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `tests/goal3193_compact_grouped_count_device_columns_test.py`
- `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md`
- `docs/reports/goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json`

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3193_compact_grouped_count_device_columns_test tests.goal3191_dense_grouped_count_device_columns_test tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test
```

## Questions To Answer

1. Does Goal3193 remain app-agnostic in the native layer, with no RayJoin or
   app-specific native logic?
2. Does it reuse the existing grouped-count kernel and add only a generic
   compact-count-columns kernel?
3. Is the compact output boundary correct: native-owned CUDA `group_key[]` and
   `count[]` columns, host row-count scalar only, direct-address `group_capacity`
   before compaction, and no exact intersection witness rows?
4. Does Python provide safe ownership/release and bounded CuPy views for both
   compact columns?
5. Is the direct-address key-capacity limitation documented and tested, including
   the pod negative probe where `group_capacity=64` overflows for IDs `200..215`?
6. Does the pod artifact support only bounded claims: live authored smoke,
   compact device column residency, CuPy validation copy only, no true zero-copy
   claim, no release authorization, no public speedup claim, and no RayJoin-
   specific native logic?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`, because the implementation is
real and pod-proven for bounded compact columns, while broader downstream
device-to-device continuations, public speedup claims, true zero-copy claims,
and release authorization remain out of scope.
