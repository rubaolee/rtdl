# Handoff: Goal3406/3408 Recovered Grouped Count Review

Please perform an independent read-only review of Goals 3406 and 3408 and write
the result to:

`docs/reviews/goal3409_claude_review_recovered_exact_stream_grouped_count_2026-06-04.md`

## Context

Goal3406 proves that an exact pair-column stream recovered through explicit
capacity retry can feed the generic compact grouped-count continuation on the
4096-chain `br_county` slice. Goal3408 repeats the same path on full available
`br_county.cdb`.

## Files To Inspect

- `scripts/goal3406_recovered_exact_stream_grouped_count_probe.py`
- `docs/reports/goal3406_recovered_exact_stream_grouped_count_probe_2026-06-04.json`
- `docs/reports/goal3406_recovered_exact_stream_grouped_count_probe_2026-06-04.md`
- `tests/goal3406_recovered_exact_stream_grouped_count_probe_test.py`
- `docs/reports/goal3408_full_br_county_recovered_exact_stream_grouped_count_2026-06-04.json`
- `docs/reports/goal3408_full_br_county_recovered_exact_stream_grouped_count_2026-06-04.md`
- `tests/goal3408_full_br_county_recovered_exact_stream_grouped_count_test.py`
- `src/rtdsl/optix_runtime.py`

## Questions

1. Do the probes preserve explicit caller retry rather than hidden dispatch?
2. Do recovered exact streams feed generic grouped count correctly on both slice
   and full CDB evidence?
3. Are the grouped results correct against host exact counts?
4. Are all claim boundaries still closed?
5. What should be the next engineering gap: chunked streaming recovery,
   device-only exact predicate, or something else?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
