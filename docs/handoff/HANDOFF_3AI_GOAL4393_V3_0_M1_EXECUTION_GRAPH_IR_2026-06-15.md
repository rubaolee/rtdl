# Goal4393 V3.0 M1 Execution-Graph IR Review Handoff

Date: 2026-06-15

Requested review: independent Claude/Gemini review for M1 freeze.

## Primary Artifact

- `docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md`

## Prior Binding Context

- `docs/reports/goal4392_3ai_consensus_v3_0_overall_plan_2026-06-15.md`
- `docs/reports/goal4392_v3_0_overall_plan_2026-06-15.md`
- `docs/reports/goal4387_v3_0_m1_design_only_unlock_2026-06-15.md`
- `docs/reports/goal4384_v3_0_preflight_3ai_consensus_2026-06-14.md`

## Review Request

Please review the M1 execution-graph IR design as the gate that decides whether M2 planner skeleton implementation may begin.

Use exactly one verdict line:

- `VERDICT: ACCEPT`
- `VERDICT: ACCEPT_WITH_NOTES`
- `VERDICT: REQUEST_CHANGES`

REQUEST_CHANGES blocks M2.

## Questions To Answer

1. Is the IR schema concrete enough for M2 to implement validators and a no-execution `PreparedGraph` skeleton?
2. Does the design preserve the app-agnostic native engine rule?
3. Does the design correctly forbid app-specific V3 public Python API names and V3 native symbols?
4. Does it make residency, stream binding, lifetime, materialization, and phase accounting first-class?
5. Does it require explicit partner selection, best practical partner plus Numba reference, and separated partner timing?
6. Does it forbid raw arbitrary OptiX callbacks as the stable user API?
7. Does it preserve same-contract OptiX-vs-Embree comparison requirements?
8. Does it define enough evidence requirements for same-stream, device-resident, true-zero-copy, and public performance wording?
9. Is the M2 allowed/not-allowed scope safe?
10. Are there blockers that must be fixed before M2 begins?

## Expected Output Files

Claude should write:

- `docs/reviews/goal4393_claude_review_v3_0_m1_execution_graph_ir_2026-06-15.md`

Gemini should write:

- `docs/reviews/goal4393_gemini_review_v3_0_m1_execution_graph_ir_2026-06-15.md`

The review should include:

- verdict line;
- top findings;
- required changes, if any;
- optional suggestions;
- final recommendation.
