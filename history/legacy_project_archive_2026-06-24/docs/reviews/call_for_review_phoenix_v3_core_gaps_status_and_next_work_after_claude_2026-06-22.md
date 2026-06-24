# Call For Review: Phoenix V3 Core Gaps, Current Status, And Next Work After Claude Redirect

Date: 2026-06-22
Author: Codex
Intended reviewers: Claude and/or Gemini, under the Phoenix V3 bounded external-review protocol

Protocol:

```text
docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md
```

Related external-review records:

```text
docs/reviews/claude_phoenix_v3_external_review_2026-06-22.md
docs/reviews/phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md
docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md
```

Requested verdict label:

```text
release_ready
approve_blocked_not_release
block_p1
block_p0
```

This packet is not asking for release authorization. It asks whether the
current Phoenix V3 recovery direction, current evidence classification, and
next work order are technically correct for a major V3 runtime release.

## Current Non-Authorization State

```text
phoenix_v3_status: redo_required
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
true_zero_copy_claim_authorized: false
automatic_backend_or_partner_selection_claim_authorized: false
v4_c_abi_or_embedding_scope_authorized_in_v3: false
```

The previous 13-row or 12-row scoped surface is internal evidence only. It is
not a Phoenix V3 major-version release.

## What Changed After Claude's Review

Claude's review gave:

```text
verdict: approve_blocked_not_release
direction_decision: continue_with_redirect
release_authorized: false
major_version_mandate_overridden: false
```

The core diagnosis was accepted: Phoenix V3 had spent too much effort on
per-route hygiene and regression repair. Those fixes are useful, but they can
mostly recover parity with V2.14. They do not prove a major runtime release.

The redirect is to Gap 1: make the productized execution path actually execute
on reusable Set-A runtime probes, then measure material gains from that path.

## Current Core Gaps

| Gap | Current status | Why it still blocks release |
| --- | --- | --- |
| Gap 1: productized execution path | A minimal `prepared_execution_session_runner` exists. It is wired into fixed-radius grouped-stream and AABB native query-handle routes. | Only one current focused route has material pod evidence; grouped-stream runner A/B was neutral. This is not yet broad runtime superiority. |
| Gap 2: residency/no-hidden-copy contract | Internal prepared-session and device-column metadata exist. Self-query refresh now records runner/device-search metadata. | Residency is not yet a release-wide contract with phase accounting across enough probes. Do not call this true zero-copy. |
| Gap 3: generic continuation families | Grouped reduction, component union, topology stream, threshold summary, ranked summary, prepared graph chunk, and AABB query-handle have row-level evidence. | Much of it is still row-scoped or route-specific evidence. It is not yet a generic production continuation runtime. |
| Gap 4: release measurement design | Claude proposed Set A / Set B scorecard. Existing all-app V2.x vs V3 serious run did not clear the old major-version bar. | Set A / Set B classification is not yet frozen as the official bar, and a new all-app run is not justified until at least two Set-A probes show material productized-path evidence. |

Claude's review says Gap 1 is the parent blocker; Gaps 2-4 are downstream.

## Current Evidence Since The Redirect

### M1: Generic Prepared Execution Session Runner

Record:

```text
docs/reports/phoenix_v3_prepared_execution_session_runner_m1_smoke_2026-06-22.md
status: m1_generic_runner_smoke_validated_not_release
```

What it proves:

- A generic runner path exists.
- The runner executes caller-supplied prepared operations.
- It records explicit backend, partner, prepared-session cache/residency,
  phases, validation, and `runtime_executed: true`.
- All release/public/broad/zero-copy/automatic-selection flags remain false.

What it does not prove:

- It does not prove performance.
- It does not prove a benchmark route uses the runner.
- It does not authorize an all-app pod run.

### M1.1: Fixed-Radius Self-Query Primitive Binding

Record:

```text
docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md
status: m1_1_fixed_radius_self_query_runner_binding_validated_not_release
```

What it proves:

- A real generic primitive family flows through the runner.
- The primitive is not app-shaped.
- It uses explicit partner choice and prepared-session cache metadata.

What it does not prove:

- It does not prove performance.
- It was not yet a real benchmark route at M1.1.

### M1.2: Grouped-Stream Runner Route

Records:

```text
docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md
docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md
status: m1_2_runner_route_pod_ab_neutral_not_release
```

What it proves:

- A real grouped-stream Set-A probe route uses the productized runner.
- Same-pod A/B confirms the route executes with stable signatures.
- Metadata records `prepared_execution_session_runner_used: true` and
  `runtime_executed: true`.

Performance result:

```text
geomean before/after speedup: 0.9979x
```

Interpretation:

- This is correct Gap-1 route evidence.
- It is not a performance win.
- It is not enough to justify a full all-app run.

### M2/M2.1: AABB Native Query-Handle Runner Route

Records:

```text
docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md
docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md
status: m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7
```

What it proves:

- A second generic primitive family is routed through the runner.
- The Contact Manifold app is only the harness; the measured route is generic
  AABB candidate streaming through `prepared_execution_session_runner`.
- Same-pod RTX 4000 Ada evidence reports `runtime_executed_count: 50`,
  `cache_hit_count: 49`, and CPU-reference correctness.

Performance result:

```text
OptiX / Embree prepare speedup: 0.700x
OptiX / Embree query median speedup: 1.921x
OptiX / Embree query total speedup: 1.738x
OptiX / Embree broadphase wall speedup: 1.348x
OptiX / Embree cold-plus-collect wall speedup: 1.346x
OptiX / Embree runner wall speedup: 1.337x
```

Interpretation:

- This is a material focused Set-A candidate from the productized runner path.
- It is pending external review and Codex consensus.
- It must not be promoted to M7, public wording, or release evidence before
  bounded review.
- It is still one material Set-A candidate, not V3 release.

## RayDB Grouped-Reduction Procedural Correction

The old grouped-reduction device-column packet had a procedural weakness:
it used a Codex subagent review as if it closed the external-AI side of 2-AI.
That is no longer current authority.

Current replacement records:

```text
docs/reviews/claude_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_review_2026-06-22.md
docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_claude_supersession_consensus_2026-06-22.md
```

Current generated packet status:

```text
current_packet_external_review_status: claude_external_approve_with_required_fixes_p1_applied_2026-06-22
current_packet_2ai_consensus_status: claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22
local_gate_reading: m7_row_evidence_scoped_not_release_after_claude_codex_consensus
```

This correction preserves the exact row-scoped evidence but does not authorize
V3 release, whole-RayDB speedup, true-zero-copy wording, or broad V3-over-V2
wording.

## Proposed Work Order

1. Close external review for the AABB M2.1 focused candidate.
   - Decide whether the 1.346x cold-plus-collect and 1.337x runner-wall result
     is valid Set-A productized-path evidence.
   - Require reviewer acceptance of the slower OptiX prepare phase and exact
     claim shape.
2. Route a second material Set-A family through the runner.
   - Preferred candidates: grouped reduction/component continuation or a
     fixed-radius/RTDBSCAN route that can compound multiple phases.
   - Avoid benchmark-app special casing.
3. Freeze Set A / Set B classification before any all-app run.
   - Set A: residency/multi-phase/continuation-rich probes.
   - Set B: ceiling/single-shot/materializing controls.
4. Run focused same-pod A/B only on runner-backed routes.
   - Do not rerun all apps until at least two Set-A probes show material gains
     from the productized execution path.
5. Only after those conditions, run serious V2.x vs V3 all-app paired evidence.
   - Report Set A and Set B separately.
   - Explain every surprising row in user language.

## Actions To Reject

- Do not continue row-by-row cache hygiene as the main V3 strategy.
- Do not call parity repair a major-version performance breakthrough.
- Do not average residency-rich probes and materializing controls into one
  blended geomean without a frozen classification.
- Do not promote old row evidence into release wording.
- Do not introduce V4/C ABI/embedding/true-zero-copy interop into V3.
- Do not add app-specific native engines just to win benchmark rows.

## Questions For Reviewer

1. Does the current status still map to `approve_blocked_not_release`, or has
   any new evidence moved it to `block_p1` or `block_p0`?
2. Is the AABB M2.1 focused result valid Set-A productized-path evidence, or
   does slower prepare/benchmark harness shape require demotion?
3. Should the Set A / Set B proposal be accepted as the official release-bar
   replacement, amended, or rejected?
4. Which second Set-A route should be prioritized next: grouped reduction /
   component continuation, fixed-radius RTDBSCAN, RTNN ranked summary, Triangle
   prepared graph chunk, or another existing reusable family?
5. Are the four gaps stated correctly, with Gap 1 as the parent blocker?
6. Is any current action drifting into benchmark-app development rather than
   language/runtime work?
7. What exact focused evidence is sufficient before another all-app pod run?
8. Are there any current docs or generated packets that still risk misleading
   users into thinking V3 is release-ready?

## Requested Reviewer Output

Please return:

- one verdict label from the protocol;
- a short release/non-release authorization block;
- highest-severity findings first;
- specific required fixes before the next external review;
- whether the AABB M2.1 candidate can proceed toward M7 review;
- whether the Set A / Set B release bar should become the working bar;
- a clear next-work recommendation.

## Goal-Level Decision Audit

Decision: issue this post-Claude call-for-review packet before treating any
runner-path work as release progress.

1. Was I foolish?
   No for this decision.
2. If yes, what actions made the decision foolish?
   The foolish action would be to treat the AABB focused win, the old row
   surface, or Claude's `continue_with_redirect` as release permission.
3. Was there another path?
   Yes. I could continue implementing without external review, but the user's
   rule requires 2-AI consensus for goal-level decisions and the prior V3
   failure came from over-trusting internal interpretation.
4. Can I now try a different path that actually solves the problem?
   Yes. Keep release blocked, ask reviewers to attack the recovery plan, then
   continue only productized execution-path work that can produce material
   Set-A evidence without app-specific shortcuts.
