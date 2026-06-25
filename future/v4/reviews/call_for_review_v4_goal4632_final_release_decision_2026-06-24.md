# Call For Review: V4 Goal4632 Final Release Decision

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4632_development_state_performance_preview_not_release`
- `accept_with_required_amendments`
- `reject_should_release_v4`
- `reject_too_positive_or_overclaiming`
- `reject_too_negative_or_hides_real_progress`

Primary document:

- `future/v4/v4_goal4632_final_release_decision_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_release_decision.py`
- `tests/v4_goal4632_release_decision_test.py`

Supporting completion records:

- `future/v4/reviews/goal4626_completion_consensus_and_review_debt_2026-06-24.md`
- `future/v4/reviews/goal4627_completion_consensus_and_review_debt_2026-06-24.md`
- `future/v4/reviews/goal4628_completion_consensus_2026-06-24.md`
- `future/v4/reviews/goal4629_completion_consensus_and_review_debt_2026-06-24.md`
- `future/v4/reviews/goal4630_completion_consensus_and_review_debt_2026-06-24.md`
- `future/v4/reviews/goal4631_completion_consensus_and_review_debt_2026-06-24.md`

Full scorecard test result:

```text
py -m unittest tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4632_release_decision_test
Ran 35 tests
OK
```

Review objective:

Decide whether Goal4632 correctly labels current V4 as `development_state_performance_preview_not_release`.

Questions:

1. Is the "not release" conclusion correct from the scorecard evidence?
2. Does the packet preserve real V4 progress without hiding it?
3. Are the release blockers complete and fair?
4. Is the allowed public wording bounded enough?
5. Does the packet correctly forbid broad speedup, whole-app, true-zero-copy, Tier-3, raw callback, CuPy, C ABI, and app-kernel claims?
6. Does the code/test scorecard prevent accidental release authorization?
7. Is any required amendment needed before this decision can stand?

Non-authorization requirements:

- Do not authorize V4 release unless you choose `reject_should_release_v4` and provide exact release wording and evidence basis.
- Do not authorize broad speedup claims.
- Do not authorize whole-application speedup claims.
- Do not authorize all-benchmark speedup claims.
- Do not authorize true-zero-copy wording.
- Do not authorize Tier-3 callback support.
- Do not authorize raw OptiX callback support.
- Do not authorize CuPy performance claims.
- Do not authorize C ABI / embedding claims.
- Do not authorize app-specific native kernels.

