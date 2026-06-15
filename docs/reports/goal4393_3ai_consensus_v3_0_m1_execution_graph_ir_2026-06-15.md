# Goal4393 3-AI Consensus: V3.0 M1 Execution-Graph IR

Date: 2026-06-15

Status: accepted with notes, required changes applied. M1 is frozen. M2 planner-skeleton work is allowed.

## Consensus State

`v3_0_m1_ir_frozen_m2_skeleton_allowed`

## Decision

The V3.0 M1 execution-graph IR design is accepted and frozen.

This consensus authorizes M2 work only in the following scope:

- pure-Python dataclasses or typed records for graph metadata;
- validators for graph values, stream binding, phase markers, node types, claim boundaries, partner policy, and app-name forbiddance;
- serialization to dictionaries or schema-like metadata;
- no-execution `PreparedGraph` construction;
- compatibility adapters that map V2 descriptors into V3 metadata.

This consensus does not authorize:

- native V3.0 fused kernels;
- backend execution;
- app-specific lowering;
- raw arbitrary OptiX callback exposure as stable user API;
- automatic partner or backend selection;
- same-stream, device-resident, or true-zero-copy promotion;
- public V3.0 performance claims.

## Reviewed Artifacts

- M1 IR design: `docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md`
- Review handoff: `docs/handoff/HANDOFF_3AI_GOAL4393_V3_0_M1_EXECUTION_GRAPH_IR_2026-06-15.md`
- Claude review: `docs/reviews/goal4393_claude_review_v3_0_m1_execution_graph_ir_2026-06-15.md`
- Gemini review: `docs/reviews/goal4393_gemini_review_v3_0_m1_execution_graph_ir_2026-06-15.md`
- Regression test: `tests/goal4393_v3_0_m1_execution_graph_ir_design_test.py`

## Reviewer Verdicts

| Reviewer | Verdict | Interpretation |
| --- | --- | --- |
| Codex | ACCEPT_WITH_NOTES | Proposed M1 design and applied required review fixes before consensus. |
| Claude | ACCEPT_WITH_NOTES | Accepted the architecture and M2 start, with four required schema fixes before affected M2 dataclasses finalize. |
| Gemini | ACCEPT | Accepted the IR design and M2 skeleton unlock. |

No reviewer returned `REQUEST_CHANGES`.

## Required Changes Applied

Claude flagged four required changes. They were applied directly to the M1 design before this consensus was recorded:

| Change | Resolution |
| --- | --- |
| RC-1: `PreparedGraph` schema missing | Added a `PreparedGraph` section with field table, state enum, claim boundary, partner policy, phase plan, validation errors, and no-execution invariants. |
| RC-2: `claim_boundary` key schema unspecified | Added an exact `ClaimBoundary` schema with required boolean keys and validation failure on missing or true keys before M7. |
| RC-3: `partner_policy` mapping unspecified | Added `PartnerPolicy` key schema covering explicit partner requirement, best partner, Numba reference, omission justification, separated timing, allowed partners, and no auto-selection. |
| RC-4: node field substructures underspecified | Converted PrimitiveNode, ContinuationNode, and PartnerNode requirements into typed field tables; added `BackendContract`, `LoweringHints`, `CapacityPolicy`, and `omission_justification` invariants. |

## Binding M2 Scope

M2 may implement:

- `GraphValue`
- `ValueKind`
- `Residency`
- `Lifetime`
- `StreamBinding`
- `PhaseMarker`
- `ClaimBoundary`
- `PartnerPolicy`
- `PrimitiveNode`
- `ContinuationNode`
- `PartnerNode`
- `MaterializeNode`
- `ValidationNode`
- `BackendPlan`
- `PreparedGraph`
- `ExecutionReport`
- `GraphValidationError`

M2 validators must enforce:

- app-agnostic V3 public API names;
- no app-specific V3 native symbols;
- all ClaimBoundary keys present and false;
- explicit partner policy and no automatic partner selection;
- Numba reference required for benchmark partner continuation unless a written omission justification exists;
- device-resident values require stream binding unless opaque prepared handles;
- hidden host materialization is invalid;
- backend comparisons require matching `same_contract_key`;
- no public claim authorization.

## Next Authorized Work

The next work item is M2 planner skeleton:

1. create the no-execution V3 graph metadata module;
2. implement the M1 dataclasses and validators;
3. add focused tests for valid and invalid graphs;
4. add static V3 public API/native symbol name gates;
5. keep backend execution and native code blocked until a later reviewed milestone.

## Final Conclusion

M1 is complete. V3.0 may proceed to M2 planner-skeleton implementation, but not to native execution or performance claims.
