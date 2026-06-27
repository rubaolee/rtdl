# Goal4633 Completion Consensus And Review Debt

Date: 2026-06-25

Status: `goal4633_complete_with_antigravity_review_debt`

Goal:

- promote, retain, or reject
  `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`.

## Verdict

Goal4633 is accepted as complete with recorded review debt:

- decision: `promote_weighted_sum_measured_torch_v4_tier2`
- surface status after Goal4633: `tier2_measured_pod_validated_not_release`
- partner scope: Torch CUDA only
- CuPy scope: declared unmeasured and fail-closed

This does not authorize V4 release.

## Evidence

POD gate:

- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.json`
- `future/v4/evidence/v4_goal4633_weighted_sum_promotion_gate_2026-06-25.md`

Review:

- Claude protocol review:
  `future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_gate_protocol_review_2026-06-24.md`
- Claude completion review:
  `future/v4/reviews/claude_v4_goal4633_weighted_sum_promotion_completion_review_2026-06-25.md`
- Antigravity blocked review debt:
  `future/v4/reviews/antigravity_v4_goal4633_weighted_sum_promotion_completion_review_blocked_2026-06-25.md`

Code/tests:

- `src/rtdsl/v4_weighted_sum_promotion_decision.py`
- `future/v4/v4_goal4633_weighted_sum_promotion_decision_2026-06-25.md`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4.py`
- `tests/v4_goal4633_weighted_sum_promotion_decision_test.py`
- `tests/v4_operator_catalog_test.py`
- `tests/v4_frontdoor_test.py`
- `tests/v4_goal4630_pushdown_recognizer_test.py`
- `tests/v4_ray_triangle_device_array_api_test.py`

## Gate Results

| Rays | Parity | Comparable-Route Ratio |
|---:|---|---:|
| 32768 | true | 2.1459x |
| 131072 | true | 1.6329x |
| 262144 | true | 1.3564x |
| 524288 | true | 1.2011x |

Thresholds:

- per-shape floor: `>=1.20x`
- geomean floor: `>=1.50x`
- observed min: `1.2011325646448796`
- observed geomean: `1.5457333064727565`

The largest row barely clears the threshold, so public wording must describe
this as a bounded comparable-route win, not a large speedup.

## Consensus Handling

Claude accepted promotion after catalog update.

Antigravity CLI returned empty output, so its review is recorded as debt. Under
the owner's rule allowing review debt instead of waiting, engineering proceeds,
but the debt remains visible for later backfill.

Codex applied the catalog/docs/tests update and preserved non-authorization
boundaries.

## Non-Authorization

Goal4633 does not authorize:

- V4 release;
- V4 release-candidate status;
- broad V4 speedup wording;
- whole-application speedup wording;
- all-benchmark speedup wording;
- CuPy performance claims;
- Tier-3 callback support;
- raw OptiX callback support;
- public true-zero-copy wording;
- C ABI / embedding / non-Python host claims;
- app-specific native kernels.
