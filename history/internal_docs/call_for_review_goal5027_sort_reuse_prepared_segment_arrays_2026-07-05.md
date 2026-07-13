# Call For Review - Goal5027 Sort Reuses Prepared Segment Arrays

Please review:

- `history/internal_docs/goal5027_sort_reuse_prepared_segment_arrays_result_2026-07-05.md`
- `history/internal_docs/rtdl_goal5027_query6_lsi_workspace_warmup_repeat_control_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_native_lexsort_valid_count_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_breakdown_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_reuse_prepared_segments_top4.json`
- `history/internal_docs/rtdl_goal5027_query6_sort_reuse_prepared_segments_repeat_control_top4.json`

## Requested Verdict Label

```text
approve_goal5027_sort_reuse_prepared_segment_arrays_reduces_query_batch_body
```

or, if the regime/accounting is judged invalid:

```text
fail_goal5027_due_to_regime_or_sort_accounting_error
```

## Review Questions

1. Does the report correctly identify the stable bottleneck as repeated segment coordinate upload inside sort, rather than the transient carrier spike?

2. Is the implementation generic and app-layer: reusing already prepared segment device arrays, without adding RayJoin-specific RTDL core/native semantics?

3. Does native lexsort sorting `valid_count` instead of `padded_count` preserve semantics for the Thrust backend while leaving bitonic padding behavior intact?

4. Does the POD evidence support the phase movement: `sort_map1` drops from about `0.10s` to about `0.022-0.026s` once prepared segment arrays are reused?

5. Does the 6-batch body sum comparison stay within one regime: top4 County x Zipcode, writer-free binary route, prepared LSI base-session, chain-contiguous distinct query batches?

6. Is the `2.91x` body-sum improvement correctly bounded to Goal5025 -> Goal5027 prepared query-batch body, not cold CLI, not paper text, not author comparison, and not 10x?

7. Is the remaining sort floor correctly diagnosed as mostly host run-table construction, making Goal5028's device run-bounds / carrier handoff the right next target?

8. Are all artifacts and tests sufficient for an internal v2.14.3 performance-workstream record?

## Context

Key same-regime numbers:

```text
Goal5025:
  body_sum        3.012616s
  later_body_sum  1.187455s
  median          0.244431s

Goal5027 sort-reuse repeat control:
  body_sum        1.034264s
  later_body_sum  0.832571s
  median          0.170494s
  best            0.143194s
  worst           0.201693s
```

The route remains a prepared-service/query-batch body route. Session setup and cold CLI remain outside this body number and must not be hidden in public claims.
