# Handoff: Gemini Review for Goal3185-3189 Device Pair Column Chain

Please perform an independent read-only Gemini review of the current RTDL `main`
state for the Goal3185 -> Goal3187 -> Goal3189 chain.

Write the review to:

`docs/reviews/goal3190_gemini_review_goal3185_3189_device_pair_columns_chain_2026-06-03.md`

Important: do not leave placeholder sections such as `[Answer to Q1]`. Answer
each question explicitly in prose after checking the files.

## Context

Current commit after the chain is `b3fe0f72`.

Goal3185 added native-owned CUDA device-resident segment-pair candidate ID
columns for prepared OptiX segment-pair traversal:

- `left_id`
- `right_id`

Goal3187 superseded Goal3185's original single-launch limitation by adding
chunked traversal append into the same output stream. Output capacity remains
uint32-bounded and fail-closed; no live >4B-pair case is claimed.

Goal3189 added the first generic continuation over those columns:

- Python method:
  `OptixNativeDevicePairColumnOutput.grouped_count_by_left_id(group_capacity=...)`
- It consumes the resident CUDA `left_id` column through the existing generic
  OptiX device-column grouped-count ABI:
  `rtdl_optix_columnar_device_payload_grouped_count_i64_with_capacity`
- It returns compact host-materialized count rows:
  `{"left_id": ..., "count": ...}`
- It does not add a new native kernel and does not add RayJoin-specific native
  engine logic.

The reused grouped-count primitive uses direct-address key capacity:
`group_capacity` must exceed the maximum non-negative `left_id` key unless the
caller remaps sparse IDs before grouping.

## Files To Review

- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/v2_8_geometry_relation_typed_stream.py`
- `tests/goal3185_segment_pair_candidate_device_columns_test.py`
- `tests/goal3187_segment_pair_candidate_chunked_append_test.py`
- `tests/goal3189_pair_column_grouped_count_continuation_test.py`
- `docs/reports/goal3185_segment_pair_candidate_device_columns_2026-06-03.md`
- `docs/reports/goal3185_pod_segment_pair_candidate_device_columns_2026-06-03.json`
- `docs/reports/goal3187_segment_pair_candidate_chunked_append_2026-06-03.md`
- `docs/reports/goal3187_pod_segment_pair_candidate_chunked_append_2026-06-03.json`
- `docs/reports/goal3189_pair_column_grouped_count_continuation_2026-06-03.md`
- `docs/reports/goal3189_pod_pair_column_grouped_count_continuation_2026-06-03.json`

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3189_pair_column_grouped_count_continuation_test tests.goal3187_segment_pair_candidate_chunked_append_test tests.goal3185_segment_pair_candidate_device_columns_test tests.goal3183_shape_pair_relation_active_count_test tests.goal3181_geometry_relation_row_view_typed_producer_metadata_test
```

## Questions To Answer

1. Does the native ABI remain app-agnostic and generic, with no RayJoin or
   app-specific native-engine logic?
2. Is the output boundary correct: device-resident candidate ID columns only,
   not exact intersection witness rows?
3. Does the Python binding provide safe RAII ownership/release for native-owned
   CUDA memory?
4. Does Goal3187 correctly supersede the old single-launch limitation with
   chunked append while keeping output capacity uint32-bounded and fail-closed?
5. Does Goal3189 correctly reuse an existing generic grouped-count primitive
   instead of adding a new native kernel?
6. Is the `group_capacity` direct-address key-capacity limitation documented
   and machine-tested, including the `group_capacity=64` fail-closed negative
   probe?
7. Do the pod artifacts support only the bounded claims recorded in the reports:
   live small authored smoke, no >4B-pair proof, no true zero-copy claim, no
   release authorization, no public speedup claim, and no RayJoin-specific native
   logic?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`, because the implementation is
real and pod-proven for the bounded chain, while larger live stress, exact
witness rows, device-resident grouped-count result chaining, public speedup
claims, true zero-copy claims, and release authorization remain out of scope.
