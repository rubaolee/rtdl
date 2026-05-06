## Verdict

Conditionally acceptable as a 3-AI consensus roadmap basis. All seven prior guardrails are materially addressed. Three residual issues are real and must be resolved before this document is treated as the final consensus artifact, but none invalidates the two-track structure or the core architectural principles.

---

## Remaining Risks

**1. "Codex" is undefined as a review anchor.**
The external review section requires "Codex plus one or two independent external AI reviews." The term "Codex" is not defined. Over the roadmap horizon it may refer to different tools, versions, or services. If this anchor is ambiguous, the review-count guardrail can be satisfied by two reviews from the same effective source under different labels.

**2. v1.6 closure tier is unassigned.**
The proposal defines two review tiers — "important" (Codex + 1) and "key" (Codex + 2) — but does not explicitly assign v1.6 closure to either tier. v1.6 is described as declaring the first architecture complete and is clearly a public-claim and architecture-boundary decision, which the proposal's own language puts in the "key" tier. The ambiguity allows v1.6 to be closed with only one external review.

**3. No intermediate conformance floor for v1.8.**
The v2.0 measurement gate names exact metric types (conformance pass rate, buffer transfer counts, round-trip latency, baseline comparisons). v1.8 is "partner buffer/execution contract and conformance tests" but carries no minimum pass-rate or metric floor. A v1.8 that ships with 20% conformance cannot be distinguished from a v1.8 that ships with 95%. The measurement discipline introduced for v2.0 should extend at least partially to the milestone that establishes the conformance baseline.

**4. CUDA unified memory is unaddressed in the zero-copy boundary section.** (Minor, non-blocking.)
The zero-copy section correctly separates CPU-contiguous, pinned/staging, and true GPU-resident paths. It does not address CUDA unified memory (`cudaMallocManaged`), which is neither a true GPU-resident zero-copy path nor a host-copy path. This is likely out of scope for v1.5.x but will resurface in the partner track if any adapter uses a PyTorch or CuPy tensor backed by managed memory. Worth a one-line acknowledgment in the zero-copy section to pre-empt overclaiming.

---

## Required Changes

**Change 1 — Define the review anchor by name and tier.**
Replace "Codex" with a concrete, version-stable reference. The simplest fix is to name the three intended reviewers (e.g., Claude, Gemini, and one additional AI system to be named at decision time) and state that any two of the three constitute a valid "Codex + 2" quorum. Alternatively, define "Codex" as the first-party system used for internal review and name it unambiguously. The definition must appear in the Release Gates section, not only in prose.

**Change 2 — Explicitly classify v1.6 closure as a key decision.**
Add a single sentence to the Release Gates section, or to the v1.6 milestone description, stating that v1.6 public closure is a key decision requiring Codex plus two independent external AI reviews, with artifacts saved under `docs/reports/`.

**Change 3 — Add a minimum conformance floor to v1.8.**
The v1.8 milestone description should require that the partner buffer/execution contract conformance suite establish a documented pass-rate baseline, with the exact number recorded in the release artifact. The v2.0 gate can then require that the pass rate meet or exceed that baseline, rather than leaving v1.8 as a free-form "tests exist" checkpoint. Even a floor of "pass rate documented and non-zero" is better than no floor.

---

## Consensus Position

The revised proposal closes the prior guardrail gaps at an acceptable level of specificity for all seven areas:

- **External review definition:** now formal, tiered, and artifact-gated. Residual ambiguity in "Codex" is the only remaining issue.
- **Partner baseline:** DLPack-compatible tensor handoff with PyTorch or CuPy as the first consumer is a concrete, testable baseline. Open-ended partner menu is explicitly prohibited for v1.7.
- **v2.0 measurement:** exact metric types named; no speedup claim allowed without exact-subpath evidence. This is sufficient for a consensus document.
- **Backend support policy:** Embree-only and OptiX-only are acceptable with explicit disclosure; same-contract requirement when both are claimed. This is clear and enforceable.
- **Zero-copy claim boundaries:** per-milestone wording constraints are precise and workable. The managed-memory gap is minor.
- **Semantic-version checkpointing:** the v1.5.10 runway cap and the per-milestone breakpoint check both address the prior concern. The "planning lane, not permission to hide breaking work" language is the right framing.
- **COLLECT_K_BOUNDED bounds testing:** the enumerated test surface (exact K, zero results, full buffers, overflow, deterministic count, fail-closed) in the Release Gates section is complete and matches the prior guardrail.

This document is acceptable as the basis for a 3-AI consensus record **if** the three required changes above are incorporated. If incorporation is deferred, the three open items must be explicitly recorded as unresolved in the consensus artifact saved to `docs/reports/`, so that a future reviewer cannot treat the current text as fully resolved.
