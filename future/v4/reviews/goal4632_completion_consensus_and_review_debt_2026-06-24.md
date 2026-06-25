# V4 Goal4632 Completion Consensus And Review Debt

Date: 2026-06-24

Status: `goal4632_complete_development_state_performance_preview_not_release`

## Verdict

Goal4632 is complete.

Final decision:

- `development_state_performance_preview_not_release`

Current authorized label:

- V4 development-state performance preview for Torch CUDA generic Tier-2 RT-core operators.

Not authorized:

- V4 release.
- V4 release candidate.
- Broad speedup claims.
- Whole-application or all-benchmark speedup claims.

Primary decision packet:

- `future/v4/v4_goal4632_final_release_decision_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4632_release_decision_test.py`

Full scorecard verification:

```text
py -m unittest tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4632_release_decision_test
Ran 35 tests
OK
```

User-facing/release-boundary verification:

```text
py -m unittest tests.v4_goal4632_release_decision_test tests.v4_release_candidate_packet_test tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_catalog_regression_gate_test tests.v4_fixed_radius_docs_and_example_test
Ran 27 tests
OK
```

## Scorecard Outcome

| Gate | Outcome |
|---|---|
| G1 fixed-radius anchor | pass as bounded one-primitive evidence |
| G2 operator coverage audit | complete but limited; not release-passing |
| G3 second Tier-2 gate | grouped-i64 accepted |
| G4 weighted-sum candidate | kept candidate, not measured |
| G5 push-down recognizer | minimum slice complete |
| G6 Tier-3 boundary | deferred/not supported |
| G7 final release decision | development-state performance preview, not release |

## Consensus Seats

### Seat 1: Codex Implementation And Self-Audit

Codex assembled the final decision packet, release decision helper, tests, and review request.

Self-audit:

1. Am I being foolish?
   - No. The final decision avoids promoting V4 beyond the evidence boundary.

2. What would make this foolish?
   - Calling V4 a release while weighted-sum is candidate, coverage is limited, Tier-3 is unsupported, and review debt remains.
   - Using grouped-i64 ratios as broad benchmark wording.
   - Hiding real measured Tier-2 progress.

3. Is there another possible path?
   - Yes. A later bounded operator release can be considered if the owner explicitly accepts limited release wording and review debt is resolved or waived.

4. Can we start a different path that truly solves the problem?
   - Yes. The next path is either release-readiness cleanup for a bounded preview label or more measured operator coverage before any release.

### Seat 2: Internal Product/Evidence Reviewer

Reviewer:

- Kepler
- agent id: `019efcd1-2254-7050-9067-9f51ccea0fbe`

Verdict:

- `accept_goal4632_development_state_performance_preview_not_release`

Summary:

- The conclusion is correctly calibrated.
- The packet denies release/release-candidate status while preserving the fair positive label `development-state performance preview`.
- The release blockers match the code-level decision.
- Real progress is fairly represented: five measured Torch CUDA Tier-2 surfaces, one candidate weighted-sum surface, fixed-radius evidence, grouped-i64 second gate, coverage audit, push-down recognizer, and Tier-3 boundary.
- Kepler independently ran the 35-test scorecard suite and it passed.

### Seat 3: Internal Code/Boundary Reviewer

Reviewer:

- Kuhn
- agent id: `019efcd1-5d37-7fa3-890a-b3049fe30e31`

Initial verdict:

- `accept_with_required_amendments`

Required amendment:

- Add an explicit test assertion that `cupy_performance_unmeasured` remains in `decision["release_blockers"]`.

Applied amendment:

- Updated `tests/v4_goal4632_release_decision_test.py`.
- Re-ran the 35-test scorecard suite successfully.

Amendment check:

- Singer
- agent id: `019efcd2-fc38-7c22-ae8b-6a9bced4fb77`
- verdict: `accept_goal4632_cupy_blocker_test_amendment_closed`

## External Review Debt

### Claude

File:

- `future/v4/reviews/claude_v4_goal4632_final_release_decision_review_blocked_2026-06-24.md`

Debt:

- `claude_goal4632_review_session_limit_debt`

Reason:

- Claude CLI returned session limit.

### Antigravity

File:

- `future/v4/reviews/antigravity_v4_goal4632_final_release_decision_review_blocked_2026-06-24.md`

Debt:

- `antigravity_goal4632_review_empty_output_debt`

Reason:

- Antigravity CLI exited with code 0 and empty stdout/stderr.

## What May Be Said

Allowed:

- V4 is a development-state performance preview.
- V4 has Torch CUDA measured Tier-2 device-array surfaces for documented generic operators.
- Fixed-radius and grouped-i64 have bounded same-contract performance evidence.
- Push-down recognition exists as a minimum slice.
- Tier-3 is spike-only/deferred.

Forbidden:

- V4 release.
- V4 release candidate.
- Broad V4 speedup.
- Whole-application speedup.
- All-benchmark speedup.
- Public true-zero-copy.
- Tier-3 callback support.
- Raw OptiX callback support.
- CuPy performance.
- C ABI / embedding / non-Python host.
- App-specific native kernels.

## Non-Authorization

Goal4632 does not authorize:

- V4 release.
- V4 release-candidate status.
- public broad speedup wording.
- whole-application speedup wording.
- all-benchmark speedup wording.
- public true-zero-copy wording.
- measured-catalog promotion.
- Tier-3 callback support.
- raw OptiX callback support.
- CuPy performance claims.
- C ABI / embedding / non-Python-host work.
- app-specific native kernels.

