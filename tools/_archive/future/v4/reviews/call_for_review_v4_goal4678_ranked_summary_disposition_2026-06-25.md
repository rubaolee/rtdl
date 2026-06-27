# Call For Review: V4 Goal4678 Ranked-Summary Candidate Disposition

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4678_defer_ranked_summary_no_open_candidate_no_release`
- `accept_with_required_amendments`
- `reject_goal4678_disposition_reopen_ranked_summary_candidate`

## Files To Review

- `future/v4/v4_goal4678_ranked_summary_disposition_2026-06-25.md`
- `future/v4/evidence/v4_goal4678_ranked_summary_disposition_2026-06-25.json`
- `future/v4/evidence/v4_goal4660_rtnn_ranked_summary_20260625/summary.json`
- `src/rtdsl/v4_goal4678_ranked_summary_disposition.py`
- `src/rtdsl/v4_ranked_summary.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_scope.py`
- `tests/v4_goal4678_ranked_summary_disposition_test.py`
- `tests/v4_goal4660_ranked_summary_candidate_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_scope_gate_test.py`

## Review Questions

1. Does the existing Goal4660/4661 evidence justify deferring ranked-summary
   instead of keeping it as an open candidate?
2. Does the decision avoid re-running POD or reinterpreting parity as progress?
3. Is it correct that the current V4 front door has 9 measured surfaces and 0
   open candidate surfaces after Goal4678?
4. Does the planner fail closed with a deferred status for ranked-summary?
5. Do public docs avoid suggesting RTNN/ranked-summary is a pending high-speed
   V4 route?
6. Does this review preserve all non-authorization boundaries?

## Expected Non-Authorization

Even if accepted, this review must not authorize V4 release, public speedup
wording, whole-app high-performance wording, RTNN speedup wording, broad
V4-over-V2/V3 claims, true-zero-copy wording, Tier-3 callback/PTX support, raw
OptiX callbacks, C ABI, embedding, non-Python hosts, automatic partner
selection, or app-identity native kernels.
