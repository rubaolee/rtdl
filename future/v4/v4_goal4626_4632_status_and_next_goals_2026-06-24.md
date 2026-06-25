# V4 Goal4626-4632 Status And Next Goals

Date: 2026-06-24

Status label: `goal4629_next__goal4626_4628_complete__goal4630_4632_pending`

This document records the current V4 implementation/review state and appends the next goals to execute. It is a coordination record, not a release authorization.

## Controlling Design

The active V4 design is:

- `future/v4/rtdl_v4_0_three_tier_fused_architecture_design_2026-06-24.md`

The current V4 line is the Python GPU ecosystem RT-core operator line:

- Tier 1: general fallback / orchestration.
- Tier 2: generic fused continuation operators pushed into RT-core traversal when the operator is app-agnostic.
- Tier 3: custom callback spike only, not a V4 release dependency.

The replacement rule for the old "pure app-agnostic" mistake is:

- Allowed: generic continuation operators such as count, threshold, grouped reduction, weighted sum, min/max, ranked summary, and related relation/reduction patterns.
- Forbidden: application-identity kernels such as a DBSCAN kernel, Barnes-Hut kernel, or triangle-counting kernel.

## Completed Goals

### Goal4626 - Section 8 Release Scorecard Protocol

Status: complete.

Artifacts:

- `future/v4/v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md`
- `tests/v4_goal4626_section8_scorecard_protocol_test.py`
- `future/v4/reviews/call_for_review_v4_goal4626_section8_release_scorecard_protocol_2026-06-24.md`
- `future/v4/reviews/goal4626_completion_consensus_and_review_debt_2026-06-24.md`

Result:

- Scorecard gates were frozen for fixed-radius, coverage audit, second Tier-2 gate, weighted-sum decision, push-down recognizer, Tier-3 spike, and release decision.
- Claude required amendments; amendments were applied and accepted.
- Antigravity accepted the initial protocol; amendment recheck was recorded as review debt because the tool returned empty output.
- Internal review accepted.

Important non-authorization:

- No V4 release.
- No broad speedup claim.
- No whole-app claim.
- No Tier-3 product claim.
- No C ABI / embedding claim.

### Goal4627 - Tier-2 Operator Coverage Audit

Status: complete.

Artifacts:

- `src/rtdsl/v4_coverage_audit.py`
- `tests/v4_goal4627_coverage_audit_test.py`
- `future/v4/v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`
- `future/v4/reviews/call_for_review_v4_goal4627_tier2_operator_coverage_audit_2026-06-24.md`
- `future/v4/reviews/goal4627_completion_consensus_and_review_debt_2026-06-24.md`

Result:

- Ten promoted benchmark app families were classified against Tier-2 operator coverage.
- Summary: 1 strong measured, 5 partial measured, 1 candidate, 3 deferred.
- Recommended second-gate target: `raydb_style` with `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`.
- Claude required clarification that triangle-counting remains candidate-bound because grouped-i64 covers an adjacent grouped-reduction dimension, not the dominant any-hit weighted/count path. The amendment was applied and accepted.
- Antigravity was blocked/empty and recorded as debt.
- Internal review accepted.

Important non-authorization:

- Coverage audit is not a release decision.
- Candidate coverage is not measured coverage.
- App coverage is not whole-app speedup.

### Goal4628 - Second Tier-2 Same-Contract Gate

Status: complete.

Artifacts:

- `src/rtdsl/v4_second_gate_scorecard.py`
- `tests/v4_goal4628_second_gate_scorecard_test.py`
- `future/v4/v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md`
- `future/v4/reviews/call_for_review_v4_goal4628_second_tier2_same_contract_gate_2026-06-24.md`
- `future/v4/reviews/goal4628_completion_consensus_2026-06-24.md`

Result:

- Second non-fixed-radius generic Tier-2 operator accepted from existing same-contract POD evidence.
- Primitive: `RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D`.
- Surface: `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`.
- Evidence ratios:
  - width 1, 32768 rays: 166.5457315834383x
  - width 1, 131072 rays: 411.8665310113891x
  - width 16, 32768 rays: 11.270692268822637x
  - width 16, 131072 rays: 21.3693298753451x
  - width 256, 32768 rays: 1.6413506440190897x
  - width 256, 131072 rays: 2.977954183815882x
- Claude and Antigravity both accepted that a fresh POD rerun was not required for Goal4628 because the evidence was same-contract, serious, and already reviewed.
- Internal review accepted.

Important non-authorization:

- This is not a V4 release.
- This is not a broad all-benchmark claim.
- Width-256 is a narrower but still positive win; the evidence must be described shape-by-shape.

## Current Open Goal

### Goal4629 - Weighted-Sum Candidate Promotion/Rejection Decision

Status: next to execute.

Existing evidence:

- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.md`
- `future/v4/evidence/v4_goal4620_ray_triangle_weighted_sum_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/reviews/claude_v4_goal4620_weighted_sum_completion_review_2026-06-24.raw.md`
- `future/v4/reviews/goal4620_completion_consensus_and_review_debt_2026-06-24.md`

Known facts:

- Surface: `v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays`.
- Existing status: `tier2_candidate_goal4620_not_measured`.
- POD hardware: RTX A5000, driver 570.195.03, Torch 2.8.0+cu128, OptiX 8.0.
- Sizes: 32768 and 131072 rays/triangles.
- Repeats: 5 after 2 warmups.
- 32768 ratio: 2.047x, parity true.
- 131072 ratio: 1.557x, parity true.
- Device-output path was used.
- No host scalar read before consumer.
- No host row materialization before consumer.
- CUDA stream pointer was nonzero.

Likely decision to test and review:

- Keep weighted-sum as candidate, not measured-catalog promoted yet.

Rationale to verify:

- The evidence is positive and useful, but it is still only two sizes with five repeats.
- The larger-size ratio is 1.557x, which is promising but not enough to convert the surface into a measured release anchor without a broader shape/capability matrix.
- Goal4620's Claude review explicitly accepted candidate completion and did not authorize measured-catalog promotion.
- Goal4628 already supplies the second measured Tier-2 gate, so there is no need to force-promote weighted-sum.

Expected Goal4629 artifacts:

- `src/rtdsl/v4_weighted_sum_candidate_decision.py`
- `tests/v4_goal4629_weighted_sum_candidate_decision_test.py`
- `future/v4/v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`
- `future/v4/reviews/call_for_review_v4_goal4629_weighted_sum_candidate_decision_2026-06-24.md`
- `future/v4/reviews/goal4629_completion_consensus_2026-06-24.md` or a completion record with explicit review debt if an external tool returns empty output.

## Remaining Goals

### Goal4630 - Push-Down Recognizer Minimum Slice

Purpose:

- Make the V4 programming model concrete: a declarative request should route to an existing generic Tier-2 surface when it matches a known operator and fail closed otherwise.

Expected work:

- Add or tighten a minimal recognizer around `src/rtdsl/v4_operator_catalog.py`.
- Accept only generic relation/reduction operators.
- Reject action-shaped callbacks, application-identity kernels, unsupported custom code, and raw callback claims.
- Document the recognizer as a minimum slice, not a full compiler.

Exit gate:

- Tests prove recognized fixed-radius/grouped-reduction/weighted-sum requests map to the intended catalog state.
- Tests prove unsupported/action-shaped requests fail closed.
- Review accepts that this is a push-down recognizer slice, not a Tier-3 or full DSL compiler.

### Goal4631 - Tier-3 Spike Execution Decision

Purpose:

- Execute or reconcile the Tier-3 Numba/PTX/OptiX callable spike honestly.

Expected work:

- Use existing spike protocol and evidence if sufficient.
- If the existing evidence is insufficient, run the lowest-cost local/POD spike required to settle Stage 1/Stage 2 status.
- Record whether Numba PTX generation works, whether OptiX module linking works, and whether the path is release-supported.

Exit gate:

- Tier-3 is either rejected/deferred or accepted only as an experimental spike.
- No release path depends on Tier-3.
- No claim of "zero overhead", "handwritten OptiX equivalent", or "arbitrary callback support" is made.

### Goal4632 - V4 Release Decision Packet

Purpose:

- Decide what V4 can honestly be called after Goals4626-4631.

Expected work:

- Assemble fixed-radius, second-gate grouped-i64, weighted-sum candidate decision, push-down recognizer, and Tier-3 decision.
- Compare against the frozen Section 8 protocol.
- State one of:
  - V4 release candidate,
  - V4 performance preview,
  - V4 development-state continuation,
  - V4 not authorized.

Exit gate:

- Three-AI consensus or explicit review debt.
- No broad benchmark claim unless all-app evidence exists.
- No public wording that outruns the measured evidence.

## What Is Not Being Done Now

- No new all-benchmark run until the scorecard says it is meaningful.
- No V3/V4 C ABI or embedding work.
- No public release promotion by implication.
- No Tier-3 productization.
- No app-identity kernels.
- No "toy" evidence substitution for same-contract POD evidence.

## Goal-Level Decision Self-Audit

Decision: document the current state and call for review before continuing Goal4629.

1. Am I being foolish?
   - Not if this record remains a control document and does not replace Goal4629 implementation.

2. What actions would make this foolish?
   - Expanding this into another process loop.
   - Asking reviewers to decide implementation details that can be tested locally.
   - Treating review output as progress while Goal4629 remains unexecuted.

3. Is there another path that avoids being stuck on one idea?
   - Yes. The immediate path is to keep this document thin, request review, and proceed to the weighted-sum decision implementation.

4. Can I start a different path that truly solves the problem?
   - Yes. If reviewers disagree with the likely weighted-sum candidate decision, Goal4629 can branch into a bounded promotion-gate rerun instead of a paper debate.

## Requested Reviewer Questions

1. Is the completed-state summary for Goals4626-4628 accurate and not overclaiming?
2. Is Goal4629 correctly framed as a candidate promotion/rejection decision rather than an automatic measured promotion?
3. Are the proposed remaining goals 4630-4632 aligned with the V4 three-tier fused architecture design?
4. Is any required release-blocking goal missing before Goal4632?
5. Does this document preserve all non-authorization boundaries?

