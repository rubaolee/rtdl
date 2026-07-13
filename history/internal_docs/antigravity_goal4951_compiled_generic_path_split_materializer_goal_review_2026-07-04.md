# Independent Technical Review: Goal4951 Compiled Generic Path-Split Materializer Goal

**Date:** 2026-07-04
**Reviewer:** Antigravity (Advanced Agentic Coding Pair)

## Verdict

`approve_goal4951_compiled_generic_path_split_spike`

Goal4951 is approved to proceed as a minimal, internal compiled spike. The design addresses the measured structural bottleneck in host Python loop overhead without polluting the RTDL core with RayJoin-specific semantics or text formatting.

---

## Executive Summary

Following the closure of Layer 1/2 (where Numba helpers did not yield expected performance wins for RayJoin) and the evaluation of Goal4940 (where a host-columnar Python path-split prototype preserved correctness but introduced significant overhead), Goal4951 targets the only remaining performance path: compiling the generic path-split and record materialization logic itself.

The proposal enforces strict genericity gates (forbidding application-specific terminology in core files) and sets a clear, strict performance gate. Reversion of any experimental wiring is mandatory if correctness or performance gates are missed.

---

## Review Answers

### 1. Does Goal4951 correctly follow from Goal4938/4939/4940/4949/4950?

**Yes.**
- [goal4938_layer3_boundary_relocation_report_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4938_layer3_boundary_relocation_report_2026-07-03.md) relocated the generic output boundary upstream to path-splitting.
- [goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md) proved that the host-columnar Python implementation of [assemble_grouped_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L286) is semantically correct (byte-equal) but introduces a major overhead (writer time rose from `2.56s` to `4.18s`).
- [goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md) officially closed Layer 1/2, noting that the remaining bottlenecks are structural path/output assembly rather than hot PIP traversal.
Thus, compiling the generic path-split materializer is the logical next step.

---

### 2. Is the proposed target the measured structural bottleneck rather than another small Layer 2 tweak?

**Yes.**
As shown in [goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md), Python host materialization (`path_split_materialize_map0 + map1`) consumed `2.39s` out of the total `4.18s`.
The current implementation of [assemble_grouped_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L286) relies on Python list appends and nested CPU loops over `673,371` points and `64,459` chains. Compiling this logic directly addresses this CPU-host overhead.

---

### 3. Are the genericity red lines strong enough to prevent RayJoin-specific output logic from entering RTDL core?

**Yes, with a strict amendment.**
- **Gate A (Source Genericity):** Any new core source files must contain no references to `rayjoin`, `overlay`, `section57`, `author`, `map0`, or `map1`.
- **Generic Schema:** The contract treats descriptors, validity masks, and group IDs as abstract, domain-neutral NumPy columns. No format-specific or application-specific string construction occurs in the core.
- **Required Amendment:** The compiled materializer must not assume a binary map structure (e.g., hardcoded logic assuming two input maps or map indexes 0 and 1). It must accept an arbitrary number of base chains and split events in a fully generalized manner.

---

### 4. Is the non-RayJoin synthetic gate required before RayJoin adapter wiring?

**Yes.**
Under **Gate B (Non-RayJoin Synthetic Correctness)**, the compiled code must pass tests on a purely domain-neutral path-splitting fixture (handling multiple chains, validity masks, descriptor preservation, and point deduplication) before any RayJoin app adapter is wired. This prevents the implementation from being tuned specifically to RayJoin's structure.

---

### 5. Are the correctness and performance gates strict enough?

**Yes.**
- **Correctness:** **Gate C** requires byte-for-byte identity to the reference author results.
- **Performance:** **Gate D** requires the compiled path-split route to beat the same-run plain writer by at least `1.10x` (minimum) or `1.25x` (strong). Since the plain writer baseline is `2.56s`, the compiled route must achieve `< 2.3s` to be accepted. If it fails this, it will be killed and reverted.

---

### 6. Should implementation start if this review passes?

**Yes.**
Resolving the output assembly performance regression is the last remaining obstacle to achieving target performance parity on the RayJoin paper reproduction. Given the strict gates, there is no risk of code regression or domain pollution.

---

### 7. If implementation starts, should the first implementation be a minimal compiled/internal spike rather than public API productization?

**Yes.**
Treating the first pass as an internal spike (e.g., placing compiled functions in an internal module or test helper) prevents committing to public API surfaces until the performance and correctness gates are proven on the POD.

---

## Reviewed Materials Reference

- **Call for Review:** [call_for_review_goal4951_compiled_generic_path_split_materializer_goal_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4951_compiled_generic_path_split_materializer_goal_2026-07-04.md)
- **Goal Proposal:** [goal4951_compiled_generic_path_split_materializer_goal_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4951_compiled_generic_path_split_materializer_goal_2026-07-04.md)
- **Context Reports:**
  - [goal4938_layer3_boundary_relocation_report_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4938_layer3_boundary_relocation_report_2026-07-03.md)
  - [goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4940_rayjoin_path_split_adapter_pod_gate_2026-07-04.md)
  - [goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4950_layer1_2_closure_and_next_step_decision_2026-07-04.md)
- **Core Source File:** [output_assembly.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py)
