# V4 `goal4620` Completion Consensus And Review Debt

Date: 2026-06-24
Author: Codex
Status: `goal4620_complete_candidate_not_promoted`

## Verdict

`goal4620` is complete only as a Tier-2 candidate implementation:

- surface:
  `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`
- status:
  `tier2_candidate_goal4620_not_measured`
- measured promotion:
  not authorized
- release status:
  not authorized

This record closes `goal4620` bookkeeping and authorizes proceeding to the
next numbered V4 goal. It does not authorize V4 release, public speedup wording,
or measured-catalog promotion.

## Consensus Seats

### Seat 1: Codex Implementation And Self-Audit

Codex implemented the weighted-sum candidate after the aggregate-tree fallback
was rejected by Claude as not a generic RT-core Tier-2 surface.

Implemented scope:

- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4_operator_catalog.py`
- `src/rtdsl/v4.py`
- `future/v4/examples/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py`
- `scripts/v4_ray_triangle_weighted_sum_device_output_validation.py`
- `scripts/v4_catalog_regression_gate.py`
- V4 docs, tests, and evidence files listed in the completion review packet

Completion packet:

- `future/v4/reviews/call_for_review_v4_goal4620_weighted_sum_completion_2026-06-24.md`

### Seat 2: Claude

Review file:

- `future/v4/reviews/claude_v4_goal4620_weighted_sum_completion_review_2026-06-24.raw.md`

Verdict:

- `accept_goal4620_complete_candidate_not_promoted`

Claude accepted candidate completion and explicitly did not authorize:

- measured-catalog promotion
- V4 release or release-candidate status
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy wording
- OptiX 9.1 scope
- CuPy performance claims
- Tier-3 callback work
- C ABI / embedding / non-Python-host work
- app-specific native kernels

Claude advisory:

- The catalog gate label `candidate_measured` was ambiguous.

Closure:

- The label was changed to `candidate_gate_passed`.
- The catalog gate was rerun on the POD after the label change.
- Current code/evidence no longer use `candidate_measured` for the
  weighted-sum candidate.

### Seat 3: Internal Third-Seat Reviewer

Reviewer:

- Descartes
- agent id: `019efc25-06a1-7193-a00c-6e89557330f4`

Verdict:

- `accept_goal4620_complete_candidate_not_promoted`

Summary:

- Weighted-sum remains candidate-only with `measured_partners: ()`.
- Front door reports five measured surfaces plus one candidate.
- POD parity passes at both measured ray counts.
- Catalog gate uses `candidate_gate_passed`, not `candidate_measured`.
- Claude amendments are closed.
- No release, true-zero-copy, broad-speedup, C ABI, callback, or app-specific
  kernel authorization is granted.

## Antigravity Review Debt

Antigravity CLI was attempted but returned exit code `0` with empty stdout in
print mode and full review mode.

Debt record:

- `future/v4/reviews/antigravity_v4_goal4620_weighted_sum_completion_review_blocked_2026-06-24.md`

This Antigravity debt is not counted as a completed external review. It may be
backfilled later through Antigravity GUI or a working CLI path. It does not
block proceeding because the user allowed explicit review debt when needed, and
the third-seat review was obtained for completion bookkeeping.

## Evidence Used

Primary POD candidate gate:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`

Summary:

| Rays | Parity | Device-Output Median (s) | Host-Scalar Median (s) | Same-Contract Ratio |
|---:|---|---:|---:|---:|
| 32768 | true | 0.000068050 | 0.000139300 | 2.047x |
| 131072 | true | 0.000146613 | 0.000228226 | 1.557x |

Catalog integration gate:

- `future/v4/evidence/v4_goal4620_catalog_gate_gpu_32768_include_weighted_sum_candidate_2026-06-24.json`
- `future/v4/evidence/v4_goal4620_catalog_gate_gpu_32768_include_weighted_sum_candidate_2026-06-24.md`

Summary:

- status: `passed`
- examples: `10`
- measured examples: `5`
- candidate examples: `1`
- weighted-sum candidate status: `candidate_gate_passed`
- release authorized: `false`

## Goal-Level Decision Audit

1. Am I being foolish by marking `goal4620` complete?
   No, because the record is narrow: candidate implementation complete, not
   measured promotion and not release.
2. What would make this decision foolish?
   Treating the same-contract candidate ratios as broad V4 performance proof,
   or treating one candidate gate as catalog promotion.
3. Is there another path that avoids being stuck on one thought?
   Yes. Keep the candidate unpromoted, record Antigravity debt, and proceed to
   `goal4621` catalog hardening before any release decision.
4. Can I start a different path that actually solves the problem?
   Yes. The next useful path is not more `goal4620` process work; it is
   `goal4621`, which hardens the catalog so users and reviewers cannot confuse
   measured, candidate, and deferred surfaces.

## Non-Authorization

This consensus does not authorize:

- V4 release
- V4 release candidate
- measured-catalog promotion
- broad V4 speedup claims
- whole-application speedup claims
- true-zero-copy public wording
- OptiX 9.1 claims
- CuPy performance claims
- Tier-3 callback support
- raw OptiX callback support
- C ABI / embedding / non-Python-host work
- app-specific native kernels

## Next Goal

Proceed to `goal4621`:

- Tier-2 catalog hardening
- measured/candidate/deferred status cleanup
- claim-boundary metadata normalization
- clean current V4 front door for users

