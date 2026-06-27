---

## Decision

Yes. It is technically honest to mark Goal 13 as canceled/superseded by Goal 15, with completed artifacts preserved as valid partial results.

---

## Reasoning

1. **Goal 13 artifacts are real and accepted.** The repo contains frozen, consensus-accepted deliverables: `rayjoin_paper_dataset_provenance.md`, `rayjoin_paper_reproduction_matrix.md`, `rayjoin_paper_reproduction_checklist.md`, and the Section 5.6 scalability analogue (Figure 13/14 slice). The Codex/Gemini Iteration 5 final consensus record explicitly states `Goal 13 Section 5.6 analogue accepted by consensus.` These are not failed work; they are a bounded successful slice.

2. **Goal 13 original scope was never completable at this stage.** The plan document itself acknowledges this is "pre-NVIDIA phase" and that Table 3, Table 4, and Figure 15 remain open. The full scope (all paper tables and figures, on GPU hardware not yet available) could not reach its own acceptance criteria without NVIDIA hardware. Canceling an out-of-reach scope is not failure — it is scoping discipline.

3. **Goal 15 is a strict narrowing, not a replacement of the same work.** Goal 15 does not reproduce Goal 13 work; it adds a different baseline slice (native C++ wrapper vs. RTDL host path, with correctness and overhead measurements). The two goals are complementary, not competing. Goal 15 is now the more actionable next-step baseline precisely because it is concrete and hardware-available today. That makes it the logical successor for active work.

4. **"Superseded" is the correct term, not "failed."** Superseded means the strategic priority shifted to a more tractable goal — not that the prior work was wrong. The artifacts remain in `history/revisions/` and `docs/` with full provenance, and are referenceable by any future GPU-phase goal that resumes the broader paper reproduction.

5. **No technical dishonesty introduced.** The canceled status must be accompanied by wording that: (a) identifies completed slices by name, (b) states the reason as strategic scope shift rather than implementation failure, and (c) names Goal 15 as the active successor baseline.

---

## Required Wording

> **Goal 13 status: Canceled — superseded by Goal 15.**
>
> Reason: Goal 13 targeted full RayJoin paper reproduction on Embree across all paper workloads and figures, which requires NVIDIA/GPU hardware not yet available. The pre-NVIDIA scope has been partially completed. The following Goal 13 artifacts are accepted as valid partial results and are preserved in full:
> - `rayjoin_paper_dataset_provenance.md`
> - `rayjoin_paper_reproduction_matrix.md`
> - `rayjoin_paper_reproduction_checklist.md`
> - Section 5.6 scalability analogue (Figure 13 / Figure 14 Embree slice), accepted by Codex/Gemini consensus 2026-03-31
>
> Goal 15 (native C++ + Embree vs. RTDL + Embree comparison) is now the active baseline for the pre-NVIDIA phase. The remaining Goal 13 open items (Table 3, Table 4, Figure 15) are deferred to a future GPU-phase goal.
>
> This cancellation does not invalidate any accepted Goal 13 artifact.

---

Consensus to cancel Goal 13 as superseded by Goal 15.
