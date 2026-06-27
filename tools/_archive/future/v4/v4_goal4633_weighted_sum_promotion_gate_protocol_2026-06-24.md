# V4 Goal4633 Weighted-Sum Promotion Gate Protocol

Date: 2026-06-24

Status: `goal4633_protocol_predeclared_claude_approved_with_amendment`

## Objective

Decide whether `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays` can move from
`tier2_candidate_goal4620_not_measured` to a measured Torch CUDA V4 Tier-2
operator surface.

This goal does not reinterpret Goal4620 or Goal4629. It creates a new
predeclared promotion gate with fixed evidence requirements, runs it, and then
records one of three outcomes:

- `promote_weighted_sum_measured_torch_v4_tier2`
- `keep_weighted_sum_candidate_not_promoted`
- `reject_weighted_sum_for_v4_0`

## Why This Goal Is Next

The Antigravity remaining-debt audit closed the procedural/review debt and left
engineering/release blockers only. The highest-leverage concrete blocker is:

- weighted-sum is still candidate-only;
- `triangle_counting` coverage remains candidate-bound through this surface;
- existing candidate evidence is positive but too narrow for promotion:
  - 32768 rays/triangles: `2.047x`, parity passed;
  - 131072 rays/triangles: `1.557x`, parity passed;
  - repeat count was candidate-level only: 5 repeats after 2 warmups.

This is a V4 route because weighted-sum is a generic Tier-2 fused continuation
operator. It is not an app-identity kernel.

## Frozen Surface

- Operator: `ray_triangle_any_hit_weighted_sum`
- API surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- Partner in this goal: Torch CUDA only
- Current status: `tier2_candidate_goal4620_not_measured`
- Candidate evidence:
  - `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
  - `future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`

CuPy remains declared unmeasured and fail-closed. This goal does not authorize
CuPy claims.

## Same-Operator Comparable-Route Comparison

For each shape, compare:

1. `device_output_frontdoor`
   - uses the V4 device-output graph executor;
   - writes the weighted hit sum into a Torch CUDA `uint64[1]` output scalar;
   - must not read the scalar to host before the consumer.

2. `host_scalar_route`
   - uses the existing prepared native weighted-sum route;
   - returns a Python host scalar.

The measured ratio is:

`host_scalar_route_median_seconds / device_output_frontdoor_median_seconds`

This is a same-operator comparable-route measurement. It measures the cost of
the host-materialization path versus the device-resident output path. It is not
a pure kernel-vs-kernel speedup figure, and it does not authorize whole-app or
all-benchmark claims.

## Frozen Promotion Matrix

Run on an RTX POD with CUDA Torch available:

| Ray Count | Triangle Count | Warmups | Repeats |
|---:|---:|---:|---:|
| 32768 | 32768 | 5 | 30 |
| 131072 | 131072 | 5 | 30 |
| 262144 | 262144 | 5 | 30 |
| 524288 | 524288 | 5 | 30 |

The first two rows rerun the candidate shapes with release-level repeats. The
last two rows expand scale coverage.

## Required Telemetry

The output JSON must record:

- hardware and driver identity;
- OptiX ABI/version if available;
- Python, Torch, CUDA availability, GPU name;
- shape matrix and repeat/warmup counts;
- all raw timings per route;
- median/min/max per route;
- same-operator comparable-route ratio per shape;
- correctness parity per shape;
- expected weighted sum, device-output value, and host-scalar value;
- `device_output_used: true`;
- `host_materialization_in_hot_path: false`;
- `host_scalar_read_before_consumer: false`;
- `weighted_sum_downloaded_to_host_in_hot_path: false`;
- `cuda_stream_ptr_nonzero: true` when exposed by metadata;
- `true_zero_copy_authorized: false`.

## Promotion Gate

Promote only if all conditions hold:

1. all shapes run successfully;
2. correctness parity passes on every shape;
3. `host_materialization_in_hot_path` is false on every shape;
4. `host_scalar_read_before_consumer` is false on every device-output route;
5. every shape has same-operator comparable-route ratio `>= 1.20x`;
6. the geomean same-operator comparable-route ratio across the four shapes is `>= 1.50x`;
7. no candidate/release wording boundary is violated;
8. external review explicitly accepts measured-catalog promotion or the review
   debt is recorded without changing the non-release boundary.

## Failure / Retention Gate

Keep candidate, not promoted, if:

- parity passes;
- the surface remains useful and correctly bounded;
- but any promotion threshold fails, the matrix is incomplete, or required
  telemetry is missing.

Reject for V4.0 if:

- parity fails;
- the surface cannot run on the release POD environment;
- metadata proves hot-path host scalar materialization is unavoidable;
- or the operator requires app-specific semantics.

## Required Artifacts

Expected new artifacts:

- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_<timestamp>.json`
- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_<timestamp>.md`
- `future/v4/v4_goal4633_weighted_sum_promotion_decision_<timestamp>.md`
- optional update to `src/rtdsl/v4_operator_catalog.py` only if promotion passes;
- optional update to `src/rtdsl/v4_weighted_sum_candidate_decision.py` or a new
  `src/rtdsl/v4_weighted_sum_promotion_decision.py` to preserve the decision;
- tests that assert the decision and prevent silent candidate/measured drift.

## Goal-Level Decision Self-Audit

Decision: make weighted-sum promotion the next engineering goal.

1. Am I being foolish?
   - No. This targets an identified engineering blocker, not process churn.

2. What actions would make this foolish?
   - Promoting from the old 5-repeat candidate evidence.
   - Choosing thresholds after seeing the new run.
   - Calling this a whole-app or broad V4 speedup result.
   - Counting CuPy or Tier-3 as supported.

3. Is there another path that avoids being stuck on one idea?
   - Yes. If the promotion gate fails, keep or reject weighted-sum and move to
     the next coverage blocker instead of massaging the threshold.

4. Can I start a different path that truly solves the problem?
   - Yes. This path directly reduces the measured/candidate coverage gap. If it
     fails, the result still clarifies the V4 release boundary.

## Non-Authorization

Goal4633 protocol does not authorize:

- V4 release;
- V4 release-candidate status;
- public broad speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- public true-zero-copy wording;
- CuPy performance claims;
- Tier-3 callback support;
- raw OptiX callback support;
- C ABI / embedding / non-Python-host claims;
- app-specific native kernels.
