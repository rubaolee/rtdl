# Gemini Review Task: Goal2312 Prepared Closed-Shape Raw Row View

Please perform an independent read-only review of Goal2312 and write your
review to:

`docs/reviews/goal2313_gemini_review_goal2312_raw_row_view_rayjoin_perf_2026-05-17.md`

Files to inspect:

- `src/rtdsl/optix_runtime.py`
- `scripts/goal2292_rayjoin_current_prepared_comparison.py`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_2026-05-17.md`
- `docs/reports/goal2312_prepared_closed_shape_raw_row_view_pod_2026-05-17.json`
- `tests/goal2312_prepared_closed_shape_raw_row_view_test.py`
- `docs/research/future_version_to_do_list.md`

Review questions:

1. Does `PreparedOptixPointClosedShapeMembership2D.run_raw(...)` mirror the
   generic OptiX row-view pattern already used by prepared segment-pair
   intersection without adding RayJoin/PIP/county/map app-specific engine logic?
2. Does the high-level `run(...)` behavior remain compatible with existing
   dictionary-row callers?
3. Does the RayJoin comparison script now measure positive rows through the raw
   row view, avoiding Python dictionary materialization for the scoped timing?
4. Does the pod artifact support the bounded claim: PIP positive rows on the
   100k RayJoin-exported stream are now near scalar-count timing, exact count
   remains 8,686, and LSI remains around 10 ms?
5. Are the claim boundaries correctly narrow: no RTDL-beats-RayJoin claim, no
   full RayJoin paper reproduction claim, no whole-app speedup, no true
   zero-copy/device-resident continuation claim, and no v2.0 release
   authorization?

Please use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. This should be a review only; do not modify source code or artifacts
except for writing the review file above.
