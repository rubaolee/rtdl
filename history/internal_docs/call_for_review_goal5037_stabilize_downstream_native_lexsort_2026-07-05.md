# Call For Review: Goal5037 Stabilize Downstream + Native Lexsort

Date: 2026-07-05

Please review:

```text
history/internal_docs/goal5037_stabilize_downstream_native_lexsort_result_2026-07-05.md
```

Requested verdict:

```text
approve_goal5037_stable_70ms_prepared_query_batch_native_lexsort_route
```

## Review Questions

1. Does the report correctly stabilize the Goal5036 `~0.089s` Numba fallback result with N=5?
2. Does the native lexsort rebuild with `OPTIX_CUDA_ARCH=sm_89` properly solve the POD `cudaErrorUnsupportedPtxVersion` issue?
3. Is the new `0.07031s` number correctly scoped to prepared query-batch, writer-free binary route with native lexsort?
4. Does the report avoid presenting `0.07031s` as cold CLI, paper text output, or author parity?
5. Are the structural anchors sufficient and unchanged across the runs?
6. Is the downstream decomposition correctly interpreted: LSI is no longer the bottleneck, and the next targets are carrier construction, PIP, descriptor consumer, and sort?
7. Is it acceptable that this goal changes no RTDL core/native source code, because the native lexsort issue was fixed by explicit build targeting on the POD?
8. Should the line proceed to a next goal targeting the largest remaining downstream component, device carrier construction (~25ms)?

## Artifacts

Numba fallback N=5:

```text
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_1_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_2_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_3_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_4_top4.json
history/internal_docs/rtdl_goal5037_stability_warmed_numba_sort_5_top4.json
```

Native lexsort N=5:

```text
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_1_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_2_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_3_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_4_top4.json
history/internal_docs/rtdl_goal5037_native_lexsort_warmed_5_top4.json
```
