# V4 Goal4633 Weighted-Sum Promotion Decision

Date: 2026-06-25

Status: `promote_weighted_sum_measured_torch_v4_tier2_with_antigravity_review_debt`

Surface:

- `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`

## Decision

The Goal4633 POD promotion gate passed its frozen numeric thresholds. Claude
accepted measured-catalog promotion after catalog update. Antigravity CLI
returned empty output and is recorded as review debt, so the surface is promoted
under the owner's review-debt rule while the debt remains visible for later
backfill.

Current decision:

- `promote_weighted_sum_measured_torch_v4_tier2`

Current surface status remains:

- `tier2_measured_pod_validated_not_release`

## Evidence

POD:

- host: `0256b71980f1`
- GPU: `NVIDIA RTX A5000`
- driver: `570.195.03`
- Python: `3.12.3`
- Torch: `2.8.0+cu128`

Artifacts:

- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json`
- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md`
- `future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_gate_protocol_review_2026-06-24.md`
- `future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_completion_review_2026-06-25.md`
- `future/v4/reviews/antigravity_v4_goal4633_weighted_sum_promotion_completion_review_blocked_2026-06-25.md`
- `future/v4/reviews/goal4633_completion_consensus_and_review_debt_2026-06-25.md`

## Result Matrix

This is a same-operator comparable-route measurement: existing host-scalar
materialization path versus V4 device-resident output path. It is not a pure
kernel-vs-kernel speedup figure.

| Rays | Triangles | Parity | Device-Output Median (s) | Host-Scalar Median (s) | Comparable-Route Ratio |
|---:|---:|---|---:|---:|---:|
| 32768 | 32768 | true | 0.0000750888 | 0.0001611300 | 2.1459x |
| 131072 | 131072 | true | 0.0001438316 | 0.0002348572 | 1.6329x |
| 262144 | 262144 | true | 0.0002434943 | 0.0003302824 | 1.3564x |
| 524288 | 524288 | true | 0.0004368126 | 0.0005246699 | 1.2011x |

Gate summary:

- all shapes completed: `true`
- parity all passed: `true`
- no hot-path host materialization: `true`
- min ratio: `1.2011325646448796`
- geomean ratio: `1.5457333064727565`
- required per-shape floor: `>=1.20x`
- required geomean floor: `>=1.50x`
- threshold result: `passed`

Important caveat:

- the largest row barely clears the per-shape threshold (`1.2011x` versus
  `1.20x`), so this should be described as a bounded route win, not a large
  speedup.

## What This Proves

The gate proves:

- the weighted-sum device-output route preserves correctness parity across the
  frozen four-shape matrix;
- it avoids host scalar materialization before the consumer;
- the host-materialization route is slower than the device-resident output
  route at all frozen shapes under this POD run;
- the frozen promotion thresholds passed.

## What This Does Not Prove

This does not prove:

- whole-application speedups;
- all-benchmark speedups;
- CuPy performance;
- Tier-3 callback support;
- public true-zero-copy support;
- C ABI / embedding support;
- app-specific native-kernel authorization.

## Required Completion Audit

Measured-catalog promotion has been applied with recorded review debt:

1. Claude accepted the evidence and boundary wording.
2. Antigravity CLI empty output was recorded as review debt.
3. Catalog, front door, docs, and tests now count weighted-sum as measured Torch
   CUDA V4 Tier-2 surface.
4. The review debt remains visible and does not authorize V4 release.

## Code And Tests

Code:

- `src/rtdsl/v4_weighted_sum_promotion_decision.py`
- `scripts/v4_ray_triangle_weighted_sum_device_output_validation.py`

Tests:

- `tests/v4_goal4633_weighted_sum_promotion_gate_protocol_test.py`
- `tests/v4_goal4633_weighted_sum_promotion_decision_test.py`

## Non-Authorization

Goal4633 does not authorize:

- V4 release;
- V4 release-candidate status;
- broad V4 speedup claims;
- whole-application speedup claims;
- all-benchmark speedup claims;
- CuPy performance claims;
- Tier-3 callback support;
- raw OptiX callback support;
- public true-zero-copy wording;
- C ABI / embedding / non-Python host claims;
- app-specific native kernels.
