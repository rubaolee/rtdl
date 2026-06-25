# Call For Review: V4 Goal4629 Weighted-Sum Candidate Decision

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4629_keep_candidate_not_promoted`
- `accept_with_required_amendments`
- `reject_should_promote_to_measured`
- `reject_should_reject_candidate`
- `reject_overclaiming_or_route_drift`

Primary document:

- `future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_weighted_sum_candidate_decision.py`
- `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`

Supporting evidence:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/reviews/claude_v4_goal4620_weighted_sum_completion_review_2026-06-24.raw.md`
- `future/v4/reviews/goal4620_completion_consensus_and_review_debt_2026-06-24.md`
- `future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`
- `future/v4/v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md`

Focused test result:

```text
py -m unittest tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test
Ran 13 tests
OK
```

Review objective:

Decide whether Goal4629 correctly closes scorecard gate G4 by keeping `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` as a Tier-2 candidate, not a measured release surface.

Questions:

1. Is `keep_candidate_not_promoted` the right decision from the existing evidence?
2. Does the document correctly preserve the positive candidate value without hiding it as a failure?
3. Does the document correctly prevent measured-catalog and release-surface overclaiming?
4. Does the decision preserve Goal4627's `triangle_counting` classification as candidate-bound?
5. Are the listed future promotion requirements sufficient for a later measured-catalog attempt?
6. Are the tests and code-level scorecard adequate to prevent Goal4632 from miscounting this surface?
7. Are all non-authorization boundaries preserved?

Non-authorization requirements:

- Do not authorize V4 release.
- Do not authorize measured-catalog promotion unless you choose `reject_should_promote_to_measured` and give exact required amendments.
- Do not authorize broad V4 speedup claims.
- Do not authorize whole-application speedup claims.
- Do not authorize true-zero-copy wording.
- Do not authorize Tier-3 callback support.
- Do not authorize C ABI / embedding claims.
- Do not authorize app-specific native kernels.

