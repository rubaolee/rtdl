# Call For Review - Goal5156 X-HD Route Phase Median Profile

Please strictly review Goal5156.

## Files

- `Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_seeded_performance_matrix.py`
- `Paper-reproduction-apps/x-hd-paper/results/xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json`
- `Paper-reproduction-apps/x-hd-paper/data/manifest.json`
- `tests/goal5156_xhd_route_phase_median_profile_test.py`
- `history/internal_docs/goal5156_xhd_route_phase_median_profile_result_2026-07-08.md`

## Review Questions

1. Does the matrix now compute subphase medians from all RTDL repeats rather
   than relying only on `phase_timings_sec_last_run`?
2. Are `phase_timings_sec_runs` and `phase_timings_sec_median` present for both
   directed routes and for the key phases (`initial_state_seed`,
   `frontier_rows`, `nearest_continuation`)?
3. Does the POD artifact preserve Goal5155's `validation_mode=author-only`,
   exact-reference-null, matched-author, and no-ratio boundaries?
4. Is the interpretation correct that sample1024 is dominated by partner-side
   nearest continuation and seed phases more than by native frontier rows?
5. Do the tests pin the median aggregation logic and artifact shape strongly
   enough?
6. Does the manifest entry avoid overclaiming performance or full reproduction?

## Expected Verdict Shape

```text
verdict_label:
blocking_findings:
required_amendments:
non_blocking_notes:
```
