# Claude Review: Phoenix V3 M10 Event Accounting Fix

Date: 2026-06-20

Scope: external review of the M10 same-stream event-accounting fix discovered
during the Phoenix M4 serious-scale pod rerun.

## Context

M9 passed at 65,536 points. M10 failed at 65,536 points with:

```text
GraphValidationError: total event time is smaller than native plus partner events
```

Code inspection showed the failing check compared `median(total_event)` with
`median(native_event) + median(partner_event)`. Those medians are computed
independently across repeats and may come from different samples, so that sum is
not a strict event invariant.

## Verdict

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

## Required Amendments

- Confirm the per-sample invariant is still checked independently: each sample
  must keep `total_event_ms >= native_event_ms` and matching stream pointers.
- Surface `independent_median_accounting_warning` in the final report/evidence
  summary, not only in nested event details.
- Document explicitly that medians are computed independently per repeat, and
  that the sum comparison is an approximation rather than a strict invariant.
- Add a unit test for the case that must still fail: total event time below an
  individual component median.

## Risk Notes

- Turning a hard failure into a warning at the same scale that failed must be
  treated as an accounting fix, not as an unqualified clean pass.
- If the warning path fires on rerun, M10 should be reported as succeeded with
  accounting warning, not as a clean pass.

## Codex Follow-Up

Codex applied the required amendments to:

- `src/rtdsl/v3_0_m10_same_stream_evidence.py`
- `tests/goal4406_v3_0_m10_same_stream_evidence_test.py`
- `docs/reports/goal4406_v3_0_m10_same_stream_evidence_2026-06-15.md`

The implementation now records event-accounting warnings in row and comparison
summaries, validates per-sample event totals independently, preserves same
stream-pointer checks, and still rejects total event time below any individual
component median.

