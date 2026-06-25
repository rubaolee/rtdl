# V4 Goal4630 Completion Consensus And Review Debt

Date: 2026-06-24

Status: `goal4630_complete_pushdown_recognizer_minimum_slice`

## Verdict

Goal4630 is complete.

Implemented:

- minimum declarative push-down recognizer;
- front-door export;
- measured/candidate Tier-2 routing;
- fail-closed boundaries for unmeasured partners, app-identity kernels, action-shaped callbacks, Tier-3 scalar callbacks, and unsupported custom logic.

Primary document:

- `future/v4/v4_goal4630_pushdown_recognizer_minimum_slice_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`
- `tests/v4_goal4630_pushdown_recognizer_test.py`

Focused verification:

```text
py -m unittest tests.v4_goal4630_pushdown_recognizer_test tests.v4_operator_catalog_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test
Ran 26 tests
OK
```

Broader front-door/catalog verification:

```text
py -m unittest tests.v4_operator_catalog_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_fixed_radius_docs_and_example_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test
Ran 33 tests
OK
```

## Consensus Seats

### Seat 1: Codex Implementation And Self-Audit

Codex implemented:

- `V4PushdownRecognition`;
- `recognize_v4_pushdown_request(...)`;
- `recognize_pushdown_request_v4(...)`;
- Goal4630 docs and tests.

Self-audit:

1. Am I being foolish?
   - No. The implementation is a minimal recognizer, not a full compiler.

2. What actions would make this foolish?
   - Claiming this is a full ITRE compiler.
   - Treating candidate or unmeasured partner routes as measured release surfaces.
   - Accepting app-identity kernels or raw callback support.

3. Is there another possible path?
   - Yes. Future operator additions can extend the catalog while preserving the fail-closed boundary.

4. Can we start a different path that truly solves the problem?
   - Yes. Proceed to Goal4631 and settle Tier-3 as spike-only/unsupported or explicitly bounded by evidence.

### Seat 2: Internal Code Reviewer

Reviewer:

- Hilbert
- agent id: `019efcc5-397f-7cc3-984b-1504383ed0d9`

Initial verdict:

- `accept_with_required_amendments`

Required amendment:

- CuPy weighted-sum candidate was incorrectly recognized as push-down instead of failing closed.

Fix:

- `recognize_v4_pushdown_request(...)` now maps candidate/no-surface partner routes to `pushdown_fail_closed_unmeasured_partner`.
- Added `test_unmeasured_candidate_partner_fails_closed`.
- Updated the Goal4630 document to state that CuPy requests to Torch-only measured or candidate surfaces fail closed.

Amendment check:

- Dewey
- agent id: `019efcc7-9127-76b0-8406-48fd08f9ea78`
- verdict: `accept_goal4630_cupy_candidate_amendment_closed`

### Seat 3: Internal Docs/Tests Reviewer

Reviewer:

- Arendt
- agent id: `019efcc5-be82-7a83-bbdf-4b3062d4f3f5`

Verdict:

- `accept_goal4630_docs_tests_complete`

Summary:

- Docs are thin and bounded.
- They align with the V4 three-tier/push-down design.
- They avoid overclaiming release, speedup, Tier-3, raw callback, CuPy, C ABI, or app-kernel authorization.
- Arendt independently ran 24 related tests and they passed.

## External Review Debt

### Claude

File:

- `future/v4/reviews/claude_v4_goal4630_pushdown_recognizer_minimum_slice_review_blocked_2026-06-24.md`

Debt:

- `claude_goal4630_review_session_limit_debt`

Reason:

- Claude CLI returned session limit.

### Antigravity

File:

- `future/v4/reviews/antigravity_v4_goal4630_pushdown_recognizer_minimum_slice_review_blocked_2026-06-24.md`

Debt:

- `antigravity_goal4630_review_empty_output_debt`

Reason:

- Antigravity CLI exited with code 0 and empty stdout/stderr.

## Recognizer Outcomes

Accepted measured push-down:

- `pushdown_recognized_measured_tier2`

Accepted candidate but non-measured:

- `pushdown_recognized_candidate_tier2_not_measured`

Fail-closed outcomes:

- `pushdown_fail_closed_unmeasured_partner`
- `pushdown_fail_closed_app_identity_kernel`
- `pushdown_fail_closed_action_shape`
- `pushdown_fail_closed_tier3_spike_only`
- `pushdown_fail_closed_unsupported`

## Non-Authorization

Goal4630 does not authorize:

- V4 release.
- V4 release-candidate status.
- measured-catalog promotion.
- broad V4 speedup claims.
- whole-application speedup claims.
- public true-zero-copy wording.
- Tier-3 callback support.
- raw OptiX callback support.
- CuPy performance claims.
- C ABI / embedding / non-Python-host work.
- app-specific native kernels.

## Next Goal

Proceed to Goal4631:

- reconcile Tier-3 spike execution evidence;
- decide whether Tier-3 remains spike-only/deferred or passes any bounded support gate;
- preserve non-authorization unless evidence and review explicitly authorize otherwise.

