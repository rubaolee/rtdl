# Antigravity Review — Goal4954 Binary Overlay Operator Pre-Fusion Program

Date: 2026-07-04
Reviewer: Antigravity (strict)
Review targets:
- [call_for_review_goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/call_for_review_goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md)
- [goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md)
- [goal4953_rayjoin_binary_overlay_operator_contract_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4953_rayjoin_binary_overlay_operator_contract_2026-07-04.md)
- [claude_review_goal4953_binary_overlay_operator_contract_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/claude_review_goal4953_binary_overlay_operator_contract_2026-07-04.md)

---

## Verdict

```text
approve_goal4954_binary_overlay_pre_fusion_program
```

### Authorization Boundary

This approval authorizes **only** the program structure of [Goal4954](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md) and the opening of **only Goal4954-A** (Contract and Measurement Plan).

It does **not** authorize immediate implementation of subsequent subgoals, raw callback support, traversal-side fusion, public API exposure, app-specific RayJoin kernels in RTDL core, or premature performance claims.

---

## Core Evaluation: The Owner Invariant

The central invariant of RTDL governance is:
> RTDL is a general spatial dataflow system; RayJoin is only an app/stress test. Any RTDL core feature must be generic and must have a non-RayJoin proof before promotion. RayJoin-specific adaptation, paper text formatting, AuthorOfficial comparison, and CDB/paper conventions must remain app-owned.

[Goal4954](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4954_binary_overlay_operator_pre_fusion_program_2026-07-04.md) successfully preserves and enforces this invariant through two structural mechanisms:

1. **Explicit Separation of Core vs. App Ownership:**
   - **RTDL Core** is restricted to generic mechanisms (e.g., columnar/device-resident row buffers, generic numeric columns, spatial operator outputs like segment-pair ids, point location labels, descriptors, and generic transforms).
   - **RayJoin App** retains ownership over paper reproduction specifics (e.g., CDB loading, AuthorOfficial comparison, byte-for-byte text formatting, app-level reconstruction, and paper-specific conventions).

2. **Hard Promotion Gate:**
   A strict 5-part promotion gate ensures that no app-specific leaks can occur. Moving any feature from the RayJoin app layer into RTDL core requires a generic name/schema, a description free of RayJoin identity, and a **non-RayJoin consumer or test** using the same mechanism.

---

## Answers to Review Questions

### 1. Does Goal4954 correctly express the owner boundary: "all practical Layer 1/2/3 binary overlay work, but no Layer 4 fusion"?
**Yes.** The program explicitly targets columnar/device-resident operations (reprojection, sort, binary row construction, and downstream consumption) but strictly excludes OptiX callbacks, traversal-side code injection, Numba PTX injection into OptiX traversal, and traversal-side fusion compilers.

### 2. Does it preserve the split between: paper reproduction text-output line as correctness anchor; binary operator line as performance/value benchmark?
**Yes.** The "Required Framing" section defines these two paths as separate lines. The Paper Reproduction Line maintains byte-for-byte compatibility with AuthorOfficial to anchor correctness, while the Binary Operator Line measures real spatial query pipeline performance without the Python/C++ text-dumping overhead.

### 3. Does it correctly incorporate Claude's Goal4953 AM1: removing writer isolates the compute gap but does not close it?
**Yes.** Under "Evidence We Must Preserve", the proposal explicitly notes that removing the writer isolates the compute gap (~2.7s for Python-based reprojection, sort, and LSI-row production vs. ~0.04s for the author's actual overlay compute) but does not close it. Task 2 requires comparing the writer-free path against the author's overlay-compute time rather than the text-dumping benchmark.

### 4. Does the subgoal sequence make sense?
**Yes.** The progression is highly logical:
- **4954-A (Contract/Measurement Plan):** Lays out the schemas and establishes baseline parameters.
- **4954-B (Writer-Free Baseline):** Isolates the exact pre-fusion compute gap.
- **4954-C (Columnar Reprojection/Sort):** Prototypes the performance improvements for the heaviest pre-fusion compute phases.
- **4954-D (Binary Rows + Consumer):** Proves the binary operator pipeline by connecting it to a real downstream consumer.
- **4954-E (Pre-fusion Decision):** Provides a clear final decision point on whether Layer 4 fusion is required.

### 5. Are the non-goals strong enough to prevent accidental Layer 4 work or RayJoin-specific RTDL core logic?
**Yes.** The non-goals section explicitly forbids traversal-side code injection, PTX injection, and hidden app-specific kernels in RTDL core. This is backed by the "System Invariant" section, which forces any core/runtime feature to be explainable without naming RayJoin or paper-reproduction details.

### 6. Does the new System Invariant section make the generic-system boundary enforceable rather than rhetorical?
**Yes.** By detailing what RTDL core may and may not own, the system invariant section provides concrete architectural criteria that can be audited during PR reviews. It establishes a clear boundary between generic spatial primitives and application-specific layout adaptation.

### 7. Does the promotion gate correctly require: generic name/schema; non-RayJoin consumer or test; no paper text or AuthorOfficial semantics in RTDL core; RayJoin-specific adaptation confined to the app layer?
**Yes.** The Hard Promotion Gate outlines all five of these rules as mandatory prerequisites for promoting code to the RTDL core repository.

### 8. If a future 4954 subgoal needs RayJoin-specific fields or output-chain semantics, should that be classified as app-owned rather than RTDL-core progress?
**Yes.** Under Task 4, the document explicitly dictates that any RayJoin-specific fields must live in an app adapter layered on top of generic RTDL columns. If a feature fails the promotion gate, it remains app-owned and is not counted as RTDL core progress.

### 9. Are success/failure criteria decision-forcing and honest?
**Yes.** The criteria force progress to halt if the binary operator cannot be defined without paper text semantics, if the binary route is not faster/different, if the consumer depends on parsing text, or if app-specific code leaks into RTDL core.

### 10. Should this program be approved with `approve_goal4954_binary_overlay_pre_fusion_program`?
**Yes.** The proposal is sound, disciplined, and strictly adheres to the owner's invariants and previous review findings.

---

## Action Items and Next Steps

1. **Open Goal4954-A:** Start the implementation program by designing the binary schema, measurement plans, and downstream consumer choices.
2. **Strict PR Audits:** During Goal4954-A, ensure the proposed schema matches the System Invariant section, maintaining absolute separation between generic RTDL dataflow columns and RayJoin app-specific adapters.
