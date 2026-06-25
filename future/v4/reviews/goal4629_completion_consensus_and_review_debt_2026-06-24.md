# V4 Goal4629 Completion Consensus And Review Debt

Date: 2026-06-24

Status: `goal4629_complete_keep_candidate_not_promoted`

## Verdict

Goal4629 is complete.

Decision:

- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` remains a Tier-2 candidate.
- It is not promoted to the measured catalog.
- It cannot count as a measured release surface in Goal4632.
- `triangle_counting` remains `candidate_not_measured_release_coverage`.

Primary decision document:

- `future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_weighted_sum_candidate_decision.py`
- `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`

Focused test result:

```text
py -m unittest tests.v4_goal4629_weighted_sum_candidate_decision_test
Ran 5 tests
OK
```

Related regression context:

```text
py -m unittest tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test
Ran 13 tests
OK
```

## Consensus Seats

### Seat 1: Codex Implementation And Self-Audit

Codex implemented the code-level decision and tests.

Self-audit answers:

1. Am I being foolish?
   - No. The decision prevents candidate evidence from being turned into an overclaim.

2. What would make this foolish?
   - Counting weighted-sum as a measured release surface in Goal4632.
   - Hiding the positive candidate result as a failure.
   - Claiming CuPy, whole-app, true-zero-copy, or release status from this evidence.

3. Is there another possible path?
   - Yes. A later predeclared promotion gate can be run if the project wants measured-catalog promotion.

4. Can we start a different path that solves the problem?
   - Yes. Proceed to Goal4630 so the push-down recognizer can fail closed and avoid measured/candidate confusion.

### Seat 2: Claude

Initial review:

- `future/v4/reviews/claude_v4_goal4629_weighted_sum_candidate_decision_review_2026-06-24.raw.md`

Initial verdict:

- `accept_with_required_amendments`

Required amendment:

- A1: expand `future_promotion_requirements` to mirror all promotion blockers.

Applied amendment:

- Added release-level repeat-count requirement.
- Added CuPy/non-Torch partner measurement requirement.
- Added triangle-counting primary-route release coverage requirement.
- Updated code, tests, and document.

Amendment check:

- `future/v4/reviews/claude_v4_goal4629_weighted_sum_candidate_decision_amendment_check_2026-06-24.raw.md`

Amendment-check verdict:

- `accept_goal4629_amendment_closed`

### Seat 3: Antigravity

Initial review:

- `future/v4/reviews/antigravity_v4_goal4629_weighted_sum_candidate_decision_review_2026-06-24.raw.md`

Initial verdict:

- `accept_goal4629_keep_candidate_not_promoted`

Important limitation:

- Antigravity accepted the original decision.
- It did not provide a successful amendment-check response after Claude A1 was applied.
- The initial Antigravity review's statement that the five original promotion requirements were sufficient is superseded by Claude A1 and the applied amendment.

Amendment-check debt:

- `future/v4/reviews/antigravity_v4_goal4629_weighted_sum_candidate_decision_amendment_check_blocked_2026-06-24.md`

Debt label:

- `antigravity_goal4629_amendment_check_empty_output_debt`

### Seat 4: Internal Third-Seat Reviewer

Reviewer:

- Planck
- agent id: `019efcbf-0e92-7b62-b425-a94fc411a434`

Verdict:

- `accept_goal4629_complete`

Summary:

- `keep_candidate_not_promoted` is evidence-bound.
- Claude A1 is fully closed in document, code, and tests.
- Antigravity initial acceptance is not misrepresented as amendment acceptance.
- Non-authorization boundaries are preserved.

## Evidence Used

Primary candidate gate:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`

Candidate ratios:

| Rays | Parity | Device-Output Median (s) | Host-Scalar Median (s) | Same-Contract Ratio |
|---:|---|---:|---:|---:|
| 32768 | true | 0.000068050 | 0.000139300 | 2.047x |
| 131072 | true | 0.000146613 | 0.000228226 | 1.557x |

## Non-Authorization

Goal4629 does not authorize:

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

Proceed to Goal4630:

- implement or tighten the minimum push-down recognizer slice;
- recognized generic operator requests route to existing Tier-2 surfaces;
- unsupported/action-shaped requests fail closed;
- candidate and measured surfaces must remain distinguishable.

