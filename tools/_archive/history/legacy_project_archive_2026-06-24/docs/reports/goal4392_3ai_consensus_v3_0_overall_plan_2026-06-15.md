# Goal4392 3-AI Consensus: V3.0 Overall Plan

Date: 2026-06-15

Status: accepted with notes. V3.0 may proceed to M1 design only. V3.0 implementation remains blocked.

## Consensus State

`v3_0_overall_plan_accepted_m1_design_only_implementation_blocked`

## Decision

The V3.0 overall plan is accepted as the governing post-v2.14 plan.

This consensus authorizes:

- M1 execution-graph IR design work;
- static tests for app-agnostic public API and native naming boundaries;
- review packet preparation for the M1 IR design;
- evidence planning for residency, stream, lifetime, phase, and partner-node contracts.

This consensus does not authorize:

- native V3.0 fused implementation;
- V3.0 planner implementation;
- app-specific public Python API names;
- app-specific native symbols or native engines;
- public V3.0 performance claims;
- same-stream, device-resident, or zero-copy wording without hardware-observable evidence.

## Reviewed Artifacts

- Overall plan: `docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md`
- Review handoff: `docs/handoff/HANDOFF_3AI_GOAL4392_V3_0_OVERALL_PLAN_2026-06-15.md`
- Claude review: `docs/reviews/goal4392_claude_review_v3_0_overall_plan_2026-06-15.md`
- Gemini review: `docs/reviews/goal4392_gemini_review_v3_0_overall_plan_2026-06-15.md`
- Regression test: `tests/goal4392_v3_0_overall_plan_test.py`

## Reviewer Verdicts

| Reviewer | Verdict | Interpretation |
| --- | --- | --- |
| Codex | ACCEPT_WITH_NOTES | Proposed the plan and incorporated reviewer guardrails before consensus closeout. |
| Claude | ACCEPT_WITH_NOTES | Accepted the plan; requested non-blocking tightening around Numba reference policy, pilot hardware evidence, and explicit M1 external review. |
| Gemini | ACCEPT | Accepted the plan and highlighted app-agnostic integrity, evidence standards, and phase-aware accounting. |

No reviewer returned request-changes.

## Changes Applied After Review

Claude's non-blocking notes were folded into the plan:

- Numba reference is now the default requirement for partner-dependent benchmark apps.
- Omitting a Numba reference now requires a written pilot justification.
- M1 milestone exit now explicitly requires external Claude/Gemini review.
- M4, M5, and M6 exits now explicitly require same-contract hardware measurements with OptiX-capable GPU and M3-grade phase accounting.
- The plan now records that Goal4384's release-grade M5 claim gate maps to Goal4392's expanded M7 claim gate.
- The prohibited claim list now also forbids claiming that RT cores always beat CUDA-core partners.

Gemini's verdict line was normalized to the exact gate format without changing its meaning.

## Binding Conditions

The Goal4384 conditions remain binding:

1. v2.14 closeout was a hard precondition for V3.0 implementation and is now satisfied only for M1 design unlock.
2. M1 must produce a frozen execution-graph IR design document before M2 code starts.
3. App-specific names are forbidden in the public Python API surface and native symbols.
4. The RTDBSCAN fused-continuation pilot must prove cross-app reuse by at least one non-DBSCAN workload.
5. Same-stream partner claims require hardware-observable evidence before public wording.
6. No V3.0 public performance claim is authorized until the release-grade benchmark harness is complete and externally reviewed.

Goal4392 adds these clarifications:

- implementation may not proceed past M1 until the M1 IR design is frozen and externally reviewed;
- public V3.0 performance claims may not proceed until M7;
- partner-dependent benchmark apps must include both the best practical partner and a Numba reference, unless omission is justified in writing;
- M4-M6 pilots require same-contract hardware measurements with M3-grade phase accounting.

## Next Authorized Work

The only V3.0 work now authorized is M1 design:

1. write the execution-graph IR design document;
2. define graph values, node types, residency, stream binding, lifetime, phase marker, partner-node, and backend-lowering contracts;
3. define forbidden public API and native naming tests;
4. define evidence standards for same-stream, device-resident, and zero-copy wording;
5. define partner-dependent benchmark table policy;
6. send the M1 design to Claude and Gemini for review before any implementation starts.

## Final Conclusion

The V3.0 overall plan is now finished enough to open M1 design. It is not a green light for implementation. The next gate is the frozen M1 execution-graph IR design with external review.
