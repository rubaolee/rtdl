# V4 Goal4632 Final Release Decision

Date: 2026-06-24

Status: `goal4632_final_decision_development_state_not_release`

Decision: `development_state_performance_preview_not_release`

V4 is not release-authorized by Goal4632. The honest current label is:

> V4 development-state performance preview for Torch CUDA generic Tier-2 RT-core operators.

This is stronger and clearer than the earlier V4 development packet because Goals4626-4631 are now closed as a scorecard chain, but it is still not a V4 release or release candidate.

## Why Not Release

Release blockers:

- operator coverage remains limited, not broad app coverage;
- weighted-sum remains a candidate, not a measured surface;
- Tier-3 remains deferred and unsupported;
- external review debt remains for recent Goal4630/Goal4631 and some prior amendment checks;
- no all-application benchmark authorizes whole-app speedup wording;
- CuPy performance is unmeasured;
- public true-zero-copy wording is not authorized;
- C ABI / embedding / non-Python host scope is not in V4.0.

## What Is Real

V4 has real development-state assets:

- five measured Torch CUDA Tier-2 device-array surfaces;
- one candidate weighted-sum surface;
- fixed-radius bounded prepared/device-array evidence;
- grouped-i64 second same-contract gate with serious POD evidence;
- coverage audit over ten promoted benchmark app families;
- minimum push-down recognizer;
- explicit Tier-3 spike boundary.

## Scorecard

| Gate | Status | Release-Passing? | Meaning |
|---|---|---:|---|
| G1 fixed-radius anchor | `pass_bounded_one_primitive` | yes | Bounded Torch CUDA fixed-radius primitive evidence exists. |
| G2 operator coverage audit | `complete_limited_coverage` | no | Coverage is limited: 1 strong measured, 5 partial measured, 1 candidate, 3 deferred. |
| G3 second Tier-2 gate | `pass_grouped_i64_second_gate` | yes | Grouped-i64 second gate passed with min same-contract ratio 1.641x. |
| G4 weighted-sum candidate | `keep_candidate_not_promoted` | no | Weighted-sum is useful but not measured-catalog promoted. |
| G5 push-down recognizer | `pass_minimum_slice` | yes | Minimal recognizer routes known operators and fails closed otherwise. |
| G6 Tier-3 boundary | `defer_tier3_not_v4_0_supported` | yes | Tier-3 is explicitly out of release dependency path. |
| G7 final release decision | `development_state_performance_preview_not_release` | no | Current decision is not release. |

## Measured And Candidate Surface Counts

- measured surfaces: 5
- candidate surfaces: 1
- measured partner: Torch CUDA
- CuPy performance: not authorized
- OptiX ABI scope for newer evidence: OptiX 8.0
- broad app coverage: not authorized

## Allowed Wording

Allowed:

- "V4 development-state performance preview."
- "Torch CUDA measured Tier-2 device-array surfaces exist for the documented measured operators."
- "Fixed-radius and grouped-i64 have bounded same-contract performance evidence."
- "The push-down recognizer routes known generic operators and fails closed otherwise."
- "Tier-3 is spike-only/deferred."

Forbidden:

- "V4 release."
- "V4 release candidate."
- "V4 broadly speeds up RTDL."
- "V4 is faster across all benchmarks."
- "V4 has whole-application speedups."
- "V4 true zero-copy."
- "V4 supports arbitrary callbacks."
- "V4 supports raw OptiX callbacks."
- "V4 supports Tier-3 callbacks."
- "V4 has CuPy performance evidence."
- "V4 exposes C ABI / embedding / non-Python-host integration."
- "V4 includes app-specific native kernels."

## Code And Tests

Code:

- `src/rtdsl/v4_release_decision.py`

Tests:

- `tests/v4_goal4632_release_decision_test.py`

Full scorecard test command:

```powershell
py -m unittest tests.v4_goal4626_section8_scorecard_protocol_test tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test tests.v4_goal4630_pushdown_recognizer_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4632_release_decision_test
```

Result:

- 35 tests passed.

## Required Next Work Before Release

Before any V4 release label, at minimum:

- clear or explicitly waive external review debt;
- either promote/reject remaining candidate surfaces through predeclared gates or keep public wording candidate-limited;
- run a meaningful release benchmark protocol if whole-app or broad speedup wording is desired;
- decide whether V4 release is allowed as a bounded operator release despite limited app coverage;
- update user-facing docs to match the exact authorized wording;
- run final clean-tree verification.

## Goal-Level Decision Self-Audit

Decision: do not release V4; label it development-state performance preview.

1. Am I being foolish?
   - No. This decision avoids repeating the earlier mistake of promoting evidence beyond its boundary.

2. What actions would make this foolish?
   - Calling V4 a release while weighted-sum is candidate, coverage is limited, Tier-3 is unsupported, and review debt remains.
   - Using grouped-i64 ratios to imply broad benchmark speedup.
   - Hiding the real measured Tier-2 progress as if nothing happened.

3. Is there another path that avoids being stuck on one idea?
   - Yes. A later release can be either a bounded operator release or a broader benchmark-backed release, but it must be explicitly authorized.

4. Can I start a different path that truly solves the problem?
   - Yes. The immediate next path is release-readiness cleanup only if the owner accepts a bounded development/performance-preview label; otherwise, the project must keep building measured operator coverage before release.

## Non-Authorization

Goal4632 does not authorize:

- V4 release
- V4 release-candidate status
- public broad speedup wording
- whole-application speedup wording
- all-benchmark speedup wording
- public true-zero-copy wording
- measured-catalog promotion
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels

