# Call For Review: Goal5172 Native Inline-Nearest Frontier

Date: 2026-07-08

Please strictly review Goal5172.

## Files Under Review

Result report:

```text
history/internal_docs/goal5172_native_inline_nearest_frontier_result_2026-07-08.md
```

Primary implementation files:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py
tests/goal5172_native_inline_nearest_frontier_test.py
```

Evidence artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_native_no_inline_control_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_res4full_goal5172_inline_nearest_matrix_pod.json
Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_goal5172_inline_nearest_exact_smoke_pod.json
Paper-reproduction-apps/x-hd-paper/data/manifest.json
history/internal_docs/xhd_review_opinions_register_2026-07-07.md
```

## Claim Being Reviewed

Goal5172 adds an app-neutral native inline-nearest mode to the generic 3-D
cell-MBR frontier collector:

```text
rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
```

The new mode lets native traversal compute nearest witness payload state for
inline cell rows and emit only offload rows to the downstream continuation.

Allowed claim:

```text
Goal5172 is a generic RTDL route improvement for the 3-D cell-MBR frontier
pipeline. On full public Stanford res4 Level B data, same-rebuild route median
moved from about 32.79 ms without inline-nearest to about 29.16 ms with
inline-nearest, while correctness against author HDResult stayed matched.
```

Forbidden claims:

```text
full X-HD paper reproduction
exact paper dataset reproduction
author-performance parity
author-vs-RTDL speedup ratio
complete author X-HD fused RT-core algorithm reproduction
X-HD-specific RTDL core primitive
```

## Evidence Summary

### Local

```text
py -m unittest tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5171_unsorted_native_frontier_rows_test \
  tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test

Ran 20 tests OK
```

### POD

POD build:

```text
make build-optix
```

Focused POD tests:

```text
python3 -m unittest \
  tests.goal5172_native_inline_nearest_frontier_test \
  tests.goal5171_unsorted_native_frontier_rows_test \
  tests.goal5170_parallel_grouped_frontier_nearest_continuation_test \
  tests.goal5169_streaming_frontier_capacity_retry_test \
  tests.goal5168_parallel_nearest_cell_mbr_seed_test \
  tests.goal5155_xhd_production_validation_and_route_profile_test \
  tests.goal5150_xhd_cell_mbr_frontier_route_gate_test

Ran 23 tests OK
```

Full public res4 same-rebuild control:

```text
artifact = xhd_seeded_res4full_goal5172_native_no_inline_control_matrix_pod.json
matched = true
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v2
route_sec_median = 0.03279334306716919
total_sec_median = 0.07399309426546097
continuation_candidate_distance_evaluations = 612923 + 539093
```

Full public res4 inline-nearest:

```text
artifact = xhd_seeded_res4full_goal5172_inline_nearest_matrix_pod.json
matched = true
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
route_sec_median = 0.029158174991607666
total_sec_median = 0.06985066831111908
continuation_candidate_distance_evaluations = 7354 + 0
```

Sample256 exact-and-author smoke:

```text
artifact = xhd_seeded_sample256_goal5172_inline_nearest_exact_smoke_pod.json
matched = true
rtdl_matches_exact_reference = true
frontier_native_symbol = rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v3
route_sec_median = 0.006261758506298065
exact_reference_sec_median = 0.10451782494783401
validation_mode = exact-and-author
```

## Review Questions

1. Is the new v3 native API app-neutral and generic, or does it smuggle X-HD or
   Hausdorff semantics into RTDL core?
2. Does the v3 API preserve v1/v2 compatibility and fail closed when
   `inline_nearest=True` but required target/point-row inputs or output arrays
   are missing?
3. Is the native payload-nearest logic semantically consistent with the
   downstream nearest-witness continuation: double distance, lower-item-id
   tie-break, and seeded current-best behavior?
4. Does the Python runtime/wrapper correctly require the v3 symbol for inline
   mode and expose `nearest_columns` / `nearest_state` without host-only
   self-deception?
5. Do the tests actually exercise the wrapper handoff and source/API contracts,
   or are they only weak string guards?
6. Does the POD evidence support the bounded claim: correctness stayed matched,
   route median improved modestly, and downstream continuation work collapsed?
7. Is the same-rebuild no-inline control the right denominator for the
   Goal5172 delta?
8. Does the report correctly avoid author-performance parity, speedup ratio,
   full paper reproduction, and exact paper dataset claims?
9. Are the manifest/register updates accurate and appropriately marked
   `implemented; review pending` rather than externally approved?
10. Should Goal5172 close as
   `completed_native_inline_nearest_frontier_route__implemented_review_pending`,
   or are amendments required before it enters the review packet?

## Expected Answer Shape

Please answer in this form:

```text
Verdict: approve | approve_with_required_amendments | reject

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers to review questions:
1. ...
2. ...
...
10. ...
```
