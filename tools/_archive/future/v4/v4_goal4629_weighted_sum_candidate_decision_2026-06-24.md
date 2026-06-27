# V4 Goal4629 Weighted-Sum Candidate Decision

Date: 2026-06-24

Status: `goal4629_weighted_sum_keep_candidate_not_promoted`

Decision: keep `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` as a Tier-2 candidate and do not promote it to the measured catalog.

This document closes Goal4626 scorecard gate G4: the weighted-sum candidate is explicitly promoted, kept candidate, or rejected. The selected decision is `keep_candidate_not_promoted`.

## Surface Under Decision

- Surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- Operator: `ray_triangle_any_hit_weighted_sum`
- Previous status: `tier2_candidate_goal4620_not_measured`
- New status after Goal4629: `tier2_candidate_goal4620_not_measured`
- Measured-catalog promotion: not authorized
- Release-surface use: not authorized

## Evidence Considered

Primary evidence:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/reviews/claude_v4_goal4620_weighted_sum_completion_review_2026-06-24.raw.md`
- `future/v4/reviews/goal4620_completion_consensus_and_review_debt_2026-06-24.md`

Measured candidate rows:

| Rays | Triangles | Parity | Device-Output Median (s) | Host-Scalar Median (s) | Same-Contract Ratio |
|---:|---:|---|---:|---:|---:|
| 32768 | 32768 | true | 0.000068050 | 0.000139300 | 2.047x |
| 131072 | 131072 | true | 0.000146613 | 0.000228226 | 1.557x |

Observed metadata:

- `device_output_used: true`
- `host_scalar_read_before_consumer: false`
- `host_row_materialization_before_consumer: false`
- `query_rays_uploaded_each_run: false`
- `ray_weights_uploaded_each_run: false`
- `cuda_stream_ptr_nonzero: true`

## Why This Is Not A Rejection

The candidate evidence is real and positive:

- correctness parity passed at both measured sizes;
- the device-output path beat the host-scalar path at both measured sizes;
- the hot path avoided host scalar read and row materialization before the consumer.

Therefore the surface remains an important Tier-2 candidate and a legitimate future promotion target.

## Why This Is Not A Promotion

Measured-catalog promotion is not authorized because:

- Goal4620's completion consensus explicitly accepted candidate completion and did not authorize measured-catalog promotion.
- The current evidence matrix covers two ray/triangle sizes only.
- The current repeats are candidate-gate level: five measured repeats after two warmups.
- The larger-size row is positive at 1.557x, but it does not by itself override the missing promotion authorization.
- CuPy and non-Torch partner performance are unmeasured.
- Triangle-counting release coverage is still not proven by this candidate row.

The important engineering distinction is:

- Candidate gate passed.
- Measured release surface did not pass because it has not been put through a predeclared promotion gate.

## Impact On Coverage

Goal4627 classified `triangle_counting` as `candidate_not_measured_release_coverage` because its dominant any-hit weighted/count continuation path depends on this candidate.

Goal4629 preserves that classification:

- `triangle_counting_release_coverage_after_goal4629: candidate_not_measured_release_coverage`
- The measured grouped-i64 operator remains valid for adjacent grouped-reduction coverage.
- The weighted-sum path cannot be counted as a measured release surface in Goal4632.

## Code And Tests

Code:

- `src/rtdsl/v4_weighted_sum_candidate_decision.py`

Tests:

- `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`

Focused test command:

```powershell
py -m unittest tests.v4_goal4627_coverage_audit_test tests.v4_goal4628_second_gate_scorecard_test tests.v4_goal4629_weighted_sum_candidate_decision_test
```

Result:

- 13 tests passed.

## Future Promotion Requirements

A future promotion attempt must be a new predeclared gate, not a reinterpretation of this candidate decision. It must at least:

- predeclare the promotion gate before rerun;
- expand the same-contract shape matrix beyond two sizes;
- increase the repeat count to release-gate level beyond the five candidate repeats;
- preserve correctness parity at every shape;
- preserve device-output and no-hot-path-host-materialization metadata;
- measure CuPy and non-Torch partner performance if those partners are in scope;
- prove triangle-counting primary-route release coverage instead of relying on adjacent grouped-reduction coverage;
- obtain external review explicitly authorizing measured-catalog promotion.

## Goal-Level Decision Self-Audit

Decision: keep weighted-sum as candidate, not measured.

1. Am I being foolish?
   - No. This avoids turning useful candidate evidence into an overclaim.

2. What actions would make this decision foolish?
   - Treating 2.047x and 1.557x candidate ratios as release-catalog proof.
   - Hiding the positive candidate result as if the surface failed.
   - Letting Goal4632 count this as a measured surface without a promotion gate.

3. Is there another path that avoids being stuck on one idea?
   - Yes. If reviewers require promotion instead, the correct branch is a bounded future promotion-gate rerun, not silent promotion.

4. Can I start a different path that actually solves the problem?
   - Yes. Goal4630 should now make the push-down recognizer fail closed so candidate and measured surfaces cannot be confused by users or release wording.

## Non-Authorization

Goal4629 does not authorize:

- V4 release
- V4 release-candidate status
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy public wording
- Tier-3 callback support
- raw OptiX callback support
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
