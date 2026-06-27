# Call For Review: V4 Goal4743 Public Docs Current Framing Cleanup

Date: 2026-06-26

Reviewer requested: Claude and Antigravity when available.

Status: `external_review_requested_debt_allowed`

## Files To Review

- `README.md`
- `docs/README.md`
- `docs/current_v4_status.md`
- `docs/app_level_benchmark_summary.md`
- `docs/learn/performance_wording.md`
- `docs/public_documentation_map.md`
- `tutorials/current/README.md`
- `tutorials/current/05_measurement_boundaries.md`
- `src/rtdsl/v4.py`
- `src/rtdsl/v4_scope.py`
- `src/rtdsl/v4_goal4643_publication_decision.py`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`
- `future/v4/examples/v4_frontdoor_quickstart.py`
- `future/v4/v4_0_scope_gate.md`
- `tests/v4_frontdoor_test.py`
- `tests/v4_scope_gate_test.py`
- `tests/v4_goal4643_publication_decision_test.py`
- `future/v4/v4_goal4743_public_docs_current_framing_cleanup_2026-06-26.md`
- `future/v4/evidence/v4_goal4743_public_docs_current_framing_cleanup_2026-06-26.json`

## Questions

1. Do the public docs now match the Goal4742 bounded release framing?
2. Are stale Goal4669 RayDB/Triangle numbers no longer presented as current?
3. Is custom predicate early-exit correctly framed as V4 eDSL value, not a
   legacy 10-app win?
4. Do the docs clearly say V4 does not claim all 10 historical benchmark apps
   are faster than V2.14?
5. Do the current public entry docs avoid presenting Goal4669/Goal4655 as the
   current user-facing truth?
6. Do `claim_boundary_v4()`, quickstart JSON, and the V4 scope gate now expose
   Goal4742 as the current boundary rather than Goal4655/Goal4718?
7. Is `docs/current_v4_status.md` now a current user status page rather than an
   internal development ledger?
8. Are all non-authorization boundaries preserved?

## Requested Verdict Labels

- `accept_goal4743_public_docs_current_framing`
- `accept_with_required_amendments`
- `reject_docs_stale_or_overclaiming`

## Non-Authorization

This review must not authorize final V4 tag, all-benchmark speedup claims,
broad V4-over-V2.14 claims, arbitrary callbacks, raw OptiX callbacks,
true-zero-copy wording, non-Python embedding/C ABI, or app-specific native
kernels.
