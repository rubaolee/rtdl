# Handoff: Gemini Review for Goal3195 Compact Grouped-Count Timing Probe

Please perform an independent read-only Gemini review of Goal3195 at current
`main`.

Write the review to:

`docs/reviews/goal3196_gemini_review_goal3195_compact_grouped_count_timing_probe_2026-06-03.md`

Do not leave placeholder answer sections. Answer each question explicitly after
checking the files.

## Context

Goal3195 is an internal timing probe for the Goal3193 compact resident
grouped-count columns.

It compares:

- exact host-row materialization:
  `prepared.run(left_segments)` plus Python `Counter(left_id)`
- compact resident primitive path:
  `candidate_device_columns(...)` plus
  `grouped_count_by_left_id_compact_device_columns(...)`

The workload is authored all-crossing segment pairs at scales:

- `512 x 512`
- `1024 x 1024`
- `2048 x 2048`

The compact path uses CuPy copies only for validation. This is not a public
speedup claim, not a RayJoin paper reproduction claim, and not release evidence.

## Files To Review

- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.md`
- `docs/reports/goal3195_compact_grouped_count_timing_probe_2026-06-03.json`
- `tests/goal3195_compact_grouped_count_timing_probe_test.py`
- `docs/reports/goal3193_compact_grouped_count_device_columns_2026-06-03.md`
- `docs/reports/goal3193_pod_compact_grouped_count_device_columns_2026-06-03.json`
- `src/rtdsl/optix_runtime.py`

## Suggested Validation

Run:

```powershell
$env:PYTHONPATH="src;."; py -3 -m unittest tests.goal3195_compact_grouped_count_timing_probe_test tests.goal3193_compact_grouped_count_device_columns_test tests.goal3191_dense_grouped_count_device_columns_test tests.goal3189_pair_column_grouped_count_continuation_test
```

## Questions To Answer

1. Is Goal3195 correctly framed as an internal primitive-path timing probe, not a
   public speedup claim, release gate, or RayJoin paper reproduction?
2. Do the artifact rows support the report table exactly, including the 2048 x
   2048 row with exact host rows `5.909632220864296` seconds and compact resident
   columns plus validation copy `0.01623670384287834` seconds?
3. Are all rows validated against exact-row oracle counts with
   `all_match_exact_rows: true`?
4. Does the report correctly explain that the compact path avoids large
   host-row materialization but still performs a validation copy in this probe?
5. Are claim boundaries false for release, public speedup, RT-core speedup, true
   zero-copy, whole-app speedup, and RayJoin paper reproduction?
6. What should be the next engineering step after this evidence: app-facing
   integration, larger stress tests, downstream device-to-device continuation,
   or something else?

## Required Verdict

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

Expected likely verdict: `accept-with-boundary`, because the timing evidence is
useful and correctly bounded, but it does not authorize public claims or release.
