# Handoff: Claude Review For Goals3413-3414

Please perform an independent read-only review of Goals3413 and 3414.

## Context

Goal3412 closed the milestone summary for exact pair-column recovery after:

- Goal3401 capacity metadata fix,
- Goal3403 capacity status/retry hint,
- Goal3404 explicit retry,
- Goal3406/3408 recovered stream grouped-count evidence,
- Goal3411 windowed Python orchestration.

Goal3413 adds a reusable generic Python contract for pair-column paged
recovery:

- `src/rtdsl/pair_column_paged_recovery.py`
- `scripts/goal3413_pair_column_paged_recovery_probe.py`
- `docs/reports/goal3413_pair_column_paged_recovery_contract_2026-06-04.md`
- `docs/reports/goal3413_pair_column_paged_recovery_probe_2026-06-04.json`
- `tests/goal3413_pair_column_paged_recovery_contract_test.py`

Goal3414 adds a narrow native OptiX page producer surface:

- `rtdl_optix_prepared_point_closed_shape_membership_exact_device_columns_page_2d`
- `PreparedOptixPointClosedShapeMembership2D.exact_device_columns_page(...)`
- `scripts/goal3414_native_exact_page_producer_probe.py`
- `docs/reports/goal3414_native_exact_page_producer_surface_2026-06-04.md`
- `docs/reports/goal3414_native_exact_page_producer_probe_2026-06-04.json`
- `tests/goal3414_native_exact_page_producer_surface_test.py`

The final committed head for Goal3414 evidence is `012ba645`.

## Required Review Questions

1. Do Goal3413 and Goal3414 preserve the app-agnostic engine boundary?
2. Does Goal3413 correctly encode caller-visible pages, fail-closed explicit
   retry, and key-addition merging without hidden dispatch?
3. Does Goal3414 really move page selection into the native ABI through
   `page_start/page_count`, while honestly preserving the boundary that exact
   rows are still host-refined before upload?
4. Are the artifacts internally consistent: 9 pages, 47,262 exact rows, 16,476
   final groups, 16,541 per-page grouped-row sum, and zero missing/extra/mismatch?
5. Are all public claim boundaries still false: no release authorization, no
   true zero-copy, no public speedup, no RT-core speedup, no RayJoin reproduction
   claim, no automatic retry, no hidden dispatch?
6. What must happen next before this can become a full native paged stream ABI?

## Suggested Verification Commands

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3414_native_exact_page_producer_surface_test `
  tests.goal3413_pair_column_paged_recovery_contract_test `
  tests.goal3412_v2_8_exact_stream_recovery_milestone_test
```

If you can run Linux/pod commands, the final pod-focused validation already
passed:

```text
Ran 19 tests in 0.451s - OK
```

## Output

Write the review to:

`docs/reviews/goal3415_claude_review_goals3413_3414_paged_recovery_native_page_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

Do not edit source files. If you find problems, write them in the review.
