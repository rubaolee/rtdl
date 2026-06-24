# Goal4393 Claude Review: V3.0 M1 Execution-Graph IR Design

Date: 2026-06-15

Reviewer: Claude (claude-sonnet-4-6)

Artifact: `docs/reports/goal4393_v3_0_m1_execution_graph_ir_design_2026-06-15.md`

IR version reviewed: `rtdl.v3_0.execution_graph_ir.m1`

VERDICT: ACCEPT_WITH_NOTES

---

## Summary

The M1 execution-graph IR design is architecturally sound. It correctly enforces the app-agnostic native engine rule, provides a comprehensive forbidden-token list, makes residency/stream/lifetime/materialization/phase accounting first-class through well-specified field tables, enforces explicit partner selection with best-partner and Numba-reference requirements, forbids raw arbitrary OptiX callbacks as stable API, preserves same-contract comparison requirements, and gates all performance claims behind a defined evidence hierarchy. The M2 scope boundary is correctly drawn.

The design is accepted for M2 to begin. However, four specification gaps would leave M2 implementers making design decisions that should be locked at M1. These gaps must be resolved, either by addendum before M2 dataclass implementation of the affected types or by explicit delegation to a bounded M2 design step with no implementation authority until locked.

---

## Findings By Review Question

### Q1 — Is the IR concrete enough for M2 validators and a no-execution PreparedGraph skeleton?

**Mostly yes, with four gaps (see Required Changes below).**

The following are well enough specified for M2 to begin:

- `GraphValue` — full field table with types, allowed values, and invariants.
- `StreamBinding` — full field table with ordering semantics and evidence invariants.
- `PhaseMarker` — full field table with required, steady-state, and setup flags.
- `MaterializeNode` — required fields and direction enum.
- `ValidationNode` — required fields and invariants.
- `ContinuationNode` — allowed operations are sufficient for M2 enum definition.
- `ExecutionReport` — full required-field list.
- `BackendPlan` — required-field list with key invariants.
- Graph-level field list — sufficient for M2 dataclass skeleton.

The following are not well enough specified for unambiguous M2 dataclass or validator implementation:

- `PreparedGraph` — listed as a public concept and as the main M2 deliverable, but has no field specification anywhere in the document. M2 cannot implement a skeleton without knowing what fields it contains.
- `claim_boundary` — appears in Graph Object and BackendPlan as a "mapping" with no key schema. The invariants reference the mapping (`Graphs must fail validation if they authorize public speedup...`) but a validator cannot enforce this without knowing the key names.
- `partner_policy` — Graph Object requires it but defines it only as "mapping." The PartnerNode invariants express the policy's intent, but the mapping schema needed to validate it is absent.
- Node field sub-structures (`backend_contract`, `lowering_hints`, `capacity_policy` in PrimitiveNode; `omission_justification` in PartnerNode) — listed as required fields but defined only by name, not by type or structure.

Additionally, node type field definitions (PrimitiveNode, PartnerNode) use bullet-point name lists rather than field tables. This inconsistency with the GraphValue and StreamBinding table style means M2 implementers must infer types. This is tolerable for M2's validators but should be corrected before M2 freezes its dataclasses.

### Q2 — Does the design preserve the app-agnostic native engine rule?

**Yes.** The Core Rule section is explicit and complete: the native V3.0 layer may expose generic primitives only; it must not expose native benchmark engines. The Benchmark Mapping section reinforces this by providing a guide that is explicitly marked as pilot-only and forbidden from leaking into V3 public API or native names. The V2 compatibility table correctly scopes legacy artifacts as kept-for-compatibility rather than promoted to V3.

### Q3 — Does the design correctly forbid app-specific V3 public Python API names and V3 native symbols?

**Yes.** The "Forbidden V3 Public API And Native Tokens" section enumerates 19 specific tokens. The legacy `RTExecutionPlan` and `rtdl_plan.schema.json` are explicitly scoped as compatibility-only and must not be extended with V3 app-specific workload enums. The public API candidate list is app-agnostic by construction. The test file `tests/goal4393_v3_0_m1_execution_graph_ir_design_test.py` enforces these boundaries programmatically over current and future V3 source files.

One minor observation: the token `contact` is on the forbidden list. This is correct given the collision/contact workload domain, but `contact` is a common English word that could appear in comment text, error messages, or documentation without domain intent. The design's stated scope ("forbidden in V3 public Python API names and V3 native exported symbols") is narrow enough that this should not cause false positives in practice. No change needed, but M2 implementers should be aware.

### Q4 — Does it make residency, stream binding, lifetime, materialization, and phase accounting first-class?

**Yes.** Each of these appears as a required field in `GraphValue` with explicit allowed values:

- `residency`: six-state enum including `unknown_pending_evidence` as an explicit non-claimed state.
- `lifetime`: six-state enum covering caller, session, borrowed, native, partner, and released authority.
- `stream_binding`: required for device-resident non-opaque values; `StreamBinding` is a separate first-class type.
- `materialization_policy`: four-state enum; `MaterializeNode` makes implicit materialization a validation failure.
- Phase accounting: mandatory ten-phase list with `PhaseMarker` tracking steady-state and setup candidacy.

The `ExecutionReport` records `data_start_residency` and phase timings, making these observable at report time as well.

One weakness: residency transitions across graph execution are not tracked per-node in the design. A device-resident value produced by a PrimitiveNode and consumed by a PartnerNode goes through a stream handoff, but the design does not require that transition to be represented as a MaterializeNode or transfer node unless the data physically moves to host. This is adequate for M1 since M2 is validators-only, but M3 will need to specify intra-graph residency transition accounting.

### Q5 — Does it enforce explicit partner selection, best-partner plus Numba-reference policy, and separated partner timing?

**Yes, completely.** The PartnerNode invariants state:

- Partner selection must be explicit; `auto` is invalid.
- A best practical partner row and a Numba reference row are required for benchmark apps with partner continuation.
- Omitting Numba requires written justification in the pilot document.
- Partner phase time must be separated from RT traversal time.
- Partner work must not be described as RTDL-only performance unless the table explicitly labels the partner.

The `numba_reference_required` and `omission_justification` fields in PartnerNode encode this as schema-level requirements, not just prose guidance.

The binding consensus (Goal4392) confirms these conditions were adopted from prior Claude/Gemini review and are now locked.

### Q6 — Does it forbid raw arbitrary OptiX callbacks as the stable user API?

**Yes.** The PrimitiveNode invariant states: "users must not supply raw arbitrary OptiX callbacks as the public RTDL API." The design permits OptiX lowering to use built-in hit attributes and internal shaders, which is a reasonable carve-out. The distinction between RTDL-managed OptiX internals and a raw callback surface exposed to users is correctly drawn.

### Q7 — Does it preserve same-contract OptiX-vs-Embree comparison requirements?

**Yes.** The `same_contract_key` field appears in PrimitiveNode, BackendPlan, and ExecutionReport. The Same-Contract Comparison Rule section specifies six conditions that must all be true for a comparison to be valid rather than diagnostic-only. The BackendPlan invariant requires `same_contract_key` to match across OptiX and Embree rows. The ValidationNode invariant requires backend comparisons to use the same contract key.

The Embree parity requirement is correctly stated at the PrimitiveNode level: "Embree lowering must expose the same logical inputs and outputs as OptiX when the graph is used for backend comparison."

### Q8 — Does it define enough evidence requirements for same-stream, device-resident, true-zero-copy, and public performance wording?

**Yes.** The Evidence Rule table is specific:

- Same-stream: CUDA events or Nsight stream correlation proving producer and consumer ordering.
- Device-resident: pointer identity or backend-native handle evidence, lifetime authority, no forced host materialization, and transfer counters.
- True zero-copy: device-resident continuation evidence plus proof of no hidden copy or host staging.
- OptiX-vs-Embree speedup: same graph, same contract, same scale, phase split, repeated runs.
- Author-system comparison: author code version, exact dataset, timing basis, correctness contract, and row/count caveats.
- Public V3.0 speedup: M7 release-grade benchmark harness and external review.

The StreamBinding section independently enforces the same-stream gate: `ordering=not_proven` blocks same-stream, device-resident continuation, and true-zero-copy public wording. The `true_zero_copy_claim_authorized` note correctly states this is not a GraphValue field but a derived evidence outcome.

The `ExecutionReport.claim_boundary` field is intended to record what is authorized, but since `claim_boundary`'s key schema is unspecified (see Required Changes), validators cannot currently enforce these gates mechanically.

### Q9 — Is the M2 allowed/not-allowed scope safe?

**Yes.** The M2 scope is well-bounded and conservative:

M2 may: implement dataclasses, pure-Python validators, serialization, static name-forbiddance, no-op PreparedGraph construction, compatibility adapters.

M2 may not: implement native fused kernels, backend execution, app-specific lowering, automatic partner selection, public speedup claim generation, true-zero-copy or same-stream promotion.

This scope keeps M2 firmly in the "design materialization" phase and prevents any execution capability from being introduced prematurely.

### Q10 — Are there blockers that must be fixed before M2 begins?

**No hard blockers for starting M2, but four gaps must be resolved before M2 finalizes its dataclasses for the affected types.** See Required Changes.

---

## Required Changes (Non-Blocking for M2 Start, Blocking for M2 Finalization)

### RC-1: Define PreparedGraph field schema

`PreparedGraph` is listed as a public API concept and is the stated primary M2 deliverable ("no-op PreparedGraph construction that does not execute"). The design does not define what fields PreparedGraph contains.

Required: Add a `PreparedGraph` section with a field table analogous to `BackendPlan` and `ExecutionReport`. Minimum expected fields: `graph_id`, `ir_version`, `validated_graph`, `backend_plan`, `state` (e.g., `prepared`, `invalidated`), `claim_boundary`. This section must exist before M2 freezes its PreparedGraph dataclass.

### RC-2: Define claim_boundary key schema

`claim_boundary` appears as a required mapping in both `Graph Object` and `BackendPlan`. Invariants reference it ("Graphs must fail validation if they authorize public speedup, true-zero-copy, hidden partner selection, automatic backend selection, or app-specific native engine logic"), but M2 validators cannot mechanically enforce these invariants without knowing the key names.

Required: Define the exact boolean keys of `claim_boundary`. At minimum: `public_speedup_authorized`, `true_zero_copy_authorized`, `hidden_partner_selection_authorized`, `automatic_backend_selection_authorized`, `app_specific_native_engine_authorized`. All must default to false.

### RC-3: Define partner_policy mapping structure

`partner_policy` is required in Graph Object and typed as "mapping," but its keys and required values are not defined. PartnerNode invariants express the intent but do not constitute a schema for the mapping.

Required: Define the key schema for `partner_policy`. Suggested structure: `{ "best_partner": string, "numba_reference_required": bool, "numba_omission_justification": string or null, "partner_timing_separated": bool }`. This must be present before M2 implements graph-level partner policy validation.

### RC-4: Complete node type field definitions with types and meanings

PrimitiveNode and PartnerNode list required field names in bullet points only. Fields `backend_contract`, `lowering_hints`, `capacity_policy` (PrimitiveNode) and `omission_justification` (PartnerNode) are referenced but never defined. ContinuationNode has no field list at all.

Required: Either add table-style definitions for all node types matching the GraphValue and StreamBinding format, or add a dedicated addendum defining the sub-structure of `backend_contract`, `lowering_hints`, `capacity_policy`, and `omission_justification` before M2 finalizes those dataclasses. At minimum, ContinuationNode needs its required fields listed (e.g., `node_id`, `operation`, `inputs`, `outputs`, `phase`).

---

## Optional Suggestions (No Gate Effect)

**OS-1: Add explicit PreparedGraph state machine.** M2 will benefit from a simple state enum for PreparedGraph: e.g., `pending_validation`, `validated`, `prepared`, `invalidated`. Without this, M2 implementers will invent their own.

**OS-2: Clarify intra-graph residency transitions for M3 planning.** The design correctly requires MaterializeNode for host materialization but does not specify how device-resident values that change stream ownership within a graph are tracked. A note scoping this to M3 would prevent M2 from making incorrect assumptions about omitting transfer nodes for device-to-device transitions.

**OS-3: Add a note on ContinuationNode identity with PartnerNode.** The invariants rightly state that `continuation.component_union`, `continuation.vector_sum`, and `continuation.frontier_expand` are generic and not application-specific. However, readers building benchmark pilots may conflate these with the PartnerNode requirement. A cross-reference note would help.

**OS-4: Specify whether `evidence_requirements` in Graph Object is caller-supplied or system-derived.** The field is required but its source is ambiguous. If caller-supplied, M2 validators need to cross-check it against the Evidence Rule table. If system-derived at validation time, M2 should not accept it as an input field.

---

## Final Recommendation

VERDICT: ACCEPT_WITH_NOTES

The M1 IR design is a strong, architecturally coherent foundation. Its core contracts — GraphValue, StreamBinding, PhaseMarker, the evidence rule table, the forbidden-token list, the partner policy, the same-contract comparison rule, and the M2 scope boundary — are all well-specified and correctly implement the governance conditions from Goal4384, Goal4387, and Goal4392.

M2 may begin implementation of GraphValue, StreamBinding, PhaseMarker, ContinuationNode, MaterializeNode, ValidationNode, BackendPlan, ExecutionReport dataclasses, and the static name-forbiddance validators. M2 must not finalize PreparedGraph, graph-level claim_boundary validation, or graph-level partner_policy validation until RC-1 through RC-4 are resolved.

RC-1 through RC-4 are required changes but do not constitute a complete rewrite. They can be addressed in a brief design addendum without another full external review cycle, provided the addendum is recorded and the consensus document references it before the state transitions to `v3_0_m1_ir_frozen_m2_skeleton_allowed`.
