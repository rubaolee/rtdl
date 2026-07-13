# Call For Review - Goal5040 Fair AuthorOfficial vs RTDL Top4 Performance Comparison

Reviewer: Claude or external reviewer

Please review:

- `history/internal_docs/goal5040_fair_author_rtdl_top4_performance_comparison_2026-07-05.md`
- `history/internal_docs/author_top4_fair_1_summary.json`
- `history/internal_docs/author_top4_fair_1_stderr.txt`
- `history/internal_docs/rtdl_top4_text_fair_1_run_summary.json`
- `history/internal_docs/rtdl_top4_text_fair_1_summary.json`
- `history/internal_docs/fair_top4_phase_calculation_2026-07-05.json`
- Goal5039 binary artifacts:
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_1_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_2_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_3_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_4_top4.json`
  - `history/internal_docs/rtdl_goal5039_vertex_nohost_5_top4.json`

Requested verdict label:

```text
approve_goal5040_fair_top4_comparison__correct_47ms_as_per_batch__binary_route_1_76x_author_core
```

## Review Questions

1. Does the report correctly use the same top4 County x Zipcode CDB input for AuthorOfficial and RTDL?

2. Does the report correctly identify the comparator as AuthorOfficial: pinned author source plus project patches?

3. Does the byte-equality evidence support saying RTDL paper text output matches AuthorOfficial on top4?

4. Is it correct to separate full wall time, post-read paper text time, and writer-free/binary core-style time instead of reporting one blended ratio?

5. Is the full wall-time comparison (`79.931s` RTDL vs `113.011s` AuthorOfficial) correctly caveated as read-cost dominated?

6. Is the post-read paper-text comparison (`64.383s` RTDL vs `12.182s` AuthorOfficial, `5.29x` slower) computed correctly from the phase logs?

7. Is the report correct to state that the previous `47ms` number is a per-query-batch median, not a whole-top4 six-batch total?

8. Is the whole-top4 prepared binary route number correctly computed as the median of six-batch sums, about `0.328842s`?

9. Is the closest current writer-free/core-style ratio (`0.328842s / 0.187042s = 1.76x slower`) a fair bounded comparison, with the semantic caveat that AuthorOfficial computes output polygons while RTDL computes binary descriptors?

10. Does the report avoid claiming author core parity, paper-text performance parity, or `47ms` full-top4 runtime?

11. Should Goal5040 close with `completed_fair_top4_author_rtdl_comparison__binary_route_1_76x_author_core__text_route_5_29x_post_read`?
