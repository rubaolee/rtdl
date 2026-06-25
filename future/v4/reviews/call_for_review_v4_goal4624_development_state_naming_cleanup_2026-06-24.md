# Call For Review: V4 `goal4624` Development-State Naming Cleanup

Date: 2026-06-24
Requested verdict labels:

- `accept_goal4624_complete_naming_cleanup_not_release`
- `reject_goal4624_incomplete_or_claim_drift`

## Review Request

Please review whether `goal4624` correctly resolves the misleading
release-candidate packet filename noted during `goal4623`, without changing V4
status or authorizing any release claim.

## Goal

Clean the development-state decision packet naming and references so the current
V4 front door no longer exposes misleading release-candidate filenames, without
changing measured/candidate status or authorizing release claims.

## Changes

Renamed current packet:

- old path removed:
  `future/v4/v4_0_release_candidate_packet_2026-06-24.md`
- new path:
  `future/v4/v4_0_development_state_decision_packet_2026-06-24.md`

Updated current references:

- `tests/v4_release_candidate_packet_test.py`
- `future/v4/reviews/call_for_review_v4_goal4623_development_state_decision_2026-06-24.md`
- `future/v4/reviews/call_for_review_v4_0_release_candidate_2026-06-24.md`
- `future/v4/reviews/goal4623_completion_consensus_2026-06-24.md`
- `future/v4/reviews/goal4623_completion_consensus_pending_third_seat_2026-06-24.md`
- `future/v4/evidence/v4_local_full_test_sweep_2026-06-24.md`
- `future/v4/reviews/review_debt_v4_0_release_candidate_2026-06-24.md`
- `scripts/run_claude_v4_0_release_candidate_review_2026_06_24.ps1`

External raw review files were not rewritten. They are historical evidence and
may still quote the old filename.

## Verification

Local:

```text
Test-Path future/v4/v4_0_release_candidate_packet_2026-06-24.md -> False
Test-Path future/v4/v4_0_development_state_decision_packet_2026-06-24.md -> True
py -m unittest tests.v4_release_candidate_packet_test tests.v4_scope_gate_test tests.v4_frontdoor_test
Ran 11 tests in 2.432s
OK
```

POD:

```text
rm -f future/v4/v4_0_release_candidate_packet_2026-06-24.md
test ! -f future/v4/v4_0_release_candidate_packet_2026-06-24.md
test -f future/v4/v4_0_development_state_decision_packet_2026-06-24.md
PYTHONPATH=src:. python3 -m unittest tests.v4_release_candidate_packet_test tests.v4_scope_gate_test tests.v4_frontdoor_test
Ran 11 tests in 1.354s
OK
```

Remaining old-path mentions are limited to raw review history or older context
statements, not the current decision packet path.

## Non-Authorization

This cleanup does not authorize:

- V4 release
- V4 release-candidate status
- broad V4 speedup wording
- whole-application speedup wording
- public true-zero-copy wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
