# Call For Review: V4 Goal4703 Specialized Tier-3 Reliability Matrix POD Result

Date: 2026-06-25

Requested verdict labels:

- `accept_goal4703_reliability_gate_pass_continue_goal4704`
- `accept_with_required_amendments_before_goal4704`
- `reject_goal4703_reliability_gate_repair_required`

## Context

Goal4702 froze the reliability protocol for constrained specialized Tier-3:
20 attempts, 4 callback variants, 5 attempts per variant, dense/sparse/no-hit
correctness datasets, `>=0.95` compile/link/launch success floor, deterministic
cache checks, and Goal4698 stage-specific failure classification.

Goal4703 ran that matrix on the POD.

## Review Inputs

- Completion record:
  `future/v4/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.md`
- POD JSON:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.json`
- POD markdown:
  `future/v4/evidence/v4_goal4703_specialized_tier3_reliability_matrix_pod_2026-06-25.md`
- Result contract:
  `src/rtdsl/v4_goal4703_specialized_tier3_reliability_result.py`
- POD script:
  `scripts/v4_goal4703_specialized_tier3_reliability_matrix_pod.py`
- Goal4702 protocol:
  `future/v4/v4_goal4702_specialized_tier3_reliability_protocol_2026-06-25.md`

## Facts To Verify

- 20/20 compile/link/launch attempts succeeded.
- All 4 callback variants were covered.
- Dense, sparse, and no-hit correctness datasets were covered.
- Correctness passed for every attempt/dataset row.
- Cache checks match the frozen artifact-level contract:
  same PTX/toolchain/symbol repeats the same key; changed PTX or changed
  toolchain changes the key.
- The record does not claim public Tier-3 support or performance.

## Reviewer Questions

1. Does Goal4703 satisfy the Goal4702 reliability protocol?
2. Is the artifact-level cache interpretation correct, given that separately recompiled Numba PTX text is observed to vary?
3. Should source-level PTX canonicalization become a required future support-hardening item?
4. Is Goal4704, bounded support wording/docs gate, the right next goal?
5. Does this result remain correctly non-authorizing for release, public Tier-3 support, arbitrary callbacks, and performance claims?

## Non-Authorization

This review must not authorize public Tier-3 support, arbitrary callbacks, raw
OptiX callback support, V4 release wording, broad speedup claims, whole-app
speed claims, or final release. It can authorize only whether Goal4703 passed
the reliability gate and whether Goal4704 may proceed.

