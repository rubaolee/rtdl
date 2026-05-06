## Verdict

**Acceptable as architecture guidance for v1.5.1, with minor required additions.** The report is technically sound on its core claims. The primitive/mechanism separation is correct, the zero-copy overclaiming risk is handled explicitly, and the phased roadmap is preserved in the right order. The gaps below are real but not blockers; they should be resolved before the report is used to drive implementation contracts.

---

## Strengths

**Clean primitive/mechanism separation.** The opening verdict draws the line precisely: `COLLECT_K_BOUNDED` answers *what RTDL produces*; zero-copy answers *how that output moves*. The two dedicated sections ("What Collect Primitives Solve", "What Zero-Copy Solves") hold the line cleanly throughout. This is the hardest conceptual mistake to avoid in this domain and the report avoids it.

**Disciplined zero-copy language.** The CPU-to-GPU subsection explicitly states that true zero-copy is only valid when data is already GPU-resident or externally shareable. CUDA unified/managed memory is named separately and disclaimed as not automatically equivalent to zero-copy. The Claim Boundaries section lists "true zero-copy" explicitly as not claimed. This is exactly the right level of caution.

**Fail-closed overflow semantics are correct.** The rule — if actual_count > K, do not return a partial result, set overflowed=true, and raise — prevents silent truncation and protects downstream score/reduction logic from operating on an incomplete candidate set. This is the right default for a language/runtime primitive. It is not overcautious; partial results here would be a semantic defect, not a performance tradeoff.

**Roadmap phasing is preserved and ordered correctly.** The Architectural Context section names v1.5.1–v1.5.10/v1.6 as Python+RTDL and v1.7–v2.0 as Python+partner+RTDL. The Partner Track Implication section reinforces the dependency: partner track begins only after Python+RTDL has a stable primitive and buffer contract. The two architecture diagrams show the correct insertion point for partner systems. No inversion or conflation with the current track.

**Buffer contract is explicit about what must be declared.** Naming pointer/handle, dtype, shape, stride/layout, device, lifetime owner, mutability, capacity, valid count, and overflow/fail-closed status as required fields is the right shape for an interop contract. This prevents the common mistake of treating a buffer as a raw pointer with implicit semantics.

**Claim Boundaries section is appropriately narrow.** Explicitly listing what is not claimed (promotion complete, backend parity complete, whole-app speedup, true zero-copy, partner integration implemented) is valuable in a document that will be used as an implementation guide. It limits scope creep.

---

## Risks

**K ownership is unspecified.** The primitive contract names `capacity: K` but does not say who sets K, when, or whether K is per-query, per-batch, or per-scene. If the implementation team infers different answers, Embree and OptiX paths will diverge before parity is tested. This is a contract gap, not just a documentation gap.

**Deterministic ordering is listed but not defined.** The report names "deterministic ordering" as one of the semantic problems `COLLECT_K_BOUNDED` solves, but does not state what ordering is required or permitted. Ray traversal across Embree and OptiX will produce different candidate orderings under identical inputs unless a sort or canonical-order rule is applied. If the contract does not specify this, backend parity cannot be verified.

**Duplicate handling is listed but not defined.** Similarly, "duplicate handling" appears in the semantic problem list without a definition. Whether a duplicate means same (left_id, right_id) pair, same geometry ID, or same ray-geometry intersection at different t values determines what the primitive must deduplicate. The contract cannot be implemented without this definition.

**DLPack handoff for v1.7 reads aspirational without a current-capability caveat.** The report states that v1.7 baseline is DLPack-compatible tensor handoff with PyTorch or CuPy as the first practical consumer. This is presented as "current consensus" but is not grounded in a measured capability or a cited decision record. Given the Claim Boundaries section, the risk is limited, but the phrasing "makes sense because..." is slightly stronger than the rest of the report's tone. A hedge or citation to the roadmap consensus document would be appropriate.

**"Row-like content" and row_width are not defined.** The report uses `int64[valid_count, row_width]` and `int64[K, row_width]` but does not state whether row_width is fixed, who defines it, or whether it can vary across query types. If row_width is variable, the buffer contract is not stable. If it is fixed, that should be stated explicitly.

---

## Required Changes

1. **Add a K ownership clause.** State explicitly who sets K (caller, RTDL runtime, scene configuration), at what granularity (per-query, per-batch, per-scene), and what happens if K changes between calls to the same buffer. Without this, the buffer contract is incomplete.

2. **Define ordering semantics for the bounded row result.** State whether the output rows must be sorted (and by what key), are permitted to be in any order, or are backend-defined. If backend-defined ordering is allowed, state that result comparison across backends requires an explicit sort step. This is necessary for backend parity tests to be meaningful.

3. **Define duplicate semantics.** State what constitutes a duplicate for `COLLECT_K_BOUNDED` and whether deduplication is the primitive's responsibility or the caller's. This can be a simple statement (e.g., "duplicate detection is not part of the primitive contract; callers are responsible for deduplication of the result buffer") but it must be explicit.

4. **Add a capability caveat to the DLPack/v1.7 statement.** Qualify the partner track baseline as a direction under evaluation rather than a finalized contract, or cite the decision record where that consensus was established.

5. **Clarify whether row_width is fixed or variable.** If fixed, state the fixed width and who defines it. If variable, explain how the buffer contract accommodates that and how callers discover the row_width at runtime.

---

## Consensus Position

The report correctly identifies the architectural relationship between `COLLECT_K_BOUNDED` and zero-copy buffer design: the primitive defines what RTDL guarantees about bounded row output; the buffer contract defines how that output is owned and moved without unnecessary copies. These are different layers and should remain so through v2.0. The v1.5.1 recommendation — stabilize the primitive and buffer contract before measuring and claiming any copy reduction — is the correct sequencing. The phased roadmap (Python+RTDL first, partner systems after a stable contract exists) is preserved without inversion.

The report is acceptable as architecture guidance once the five required changes above are incorporated. None of the gaps are fundamental design errors; they are contract incompleteness that will cause divergence during implementation if not resolved before coding begins.
