# Goal3689 Independent Gemini Review: Goal3688 Native-PIP RayJoin Composite

**Review Date:** 2026-06-07

**Goal Reviewed:** Goal3688 Native-PIP RayJoin Composite

**Context:** Goal3688 tests whether the Goal3686 generic resident native scalar-count executor can replace the older CuPy PIP correction leg inside the current safe RayJoin count composite. It does not change the rest of the composite: PIP: native resident relation-status corrected scalar count, LSI: existing exact prepared RTDL/OptiX route with host double refinement, overlay seed: existing RTDL/OptiX active-count route. This is an internal candidate route only.

---

## Findings

Yes, it explicitly states that it is an internal candidate route and does not promote a default public RayJoin route or claim paper reproduction. The native PIP leg uses a generic native scalar primitive, preserving app-agnostic boundaries. The report and artifact explicitly disclaim any app-specific native ABI or hidden app policy.

Yes, the runner is explicitly designed to compare against the dense all-CuPy same-contract baseline and fails closed on count mismatch, and all counts matched for the measured packet.

Yes, the A5000 artifact is credible. The source-scoped status was clean (`goal3688_scoped_source_dirty=false`), exact count parity was achieved (`all_counts_match=true`), and the composite speedup of `205.372x` is reported consistently across the report and the artifact for the measured 4096-chain packet.

Yes, the report explicitly avoids all mentioned overclaims. The "Boundary" section clearly lists these as unauthorized claims, and the `summary.json` artifact confirms these disclaimers programmatically.

No immediate "fixes" are required for the candidate route itself. However, there are several "Next Work" items identified in the report that are essential for internal benchmark-summary promotion: external review, testing on additional counts, deciding on the standard PIP leg, and documentation clarity.

---

## Verdict

**Verdict:** accept-with-boundary

**Reasoning:**
The Goal3688 candidate route successfully demonstrates that the generic resident native scalar-count executor (Goal3686) can replace the older CuPy PIP leg within the safe RayJoin count composite. The runner honestly compares against the dense all-CuPy baseline, fails closed on count mismatch, and the A5000 artifact confirms exact count parity and a significant composite speedup (205.372x for the measured 4096-chain packet). The report rigorously adheres to its claim boundaries, explicitly disallowing any overclaims regarding release readiness, public speedup, RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, or true zero-copy. The scoped source was clean, adding to the credibility of the artifact. While there are no immediate "fixes" required, the "Next Work" items (external review, additional count testing, decision on standard PIP leg, and documentation clarity) are essential before broader internal benchmark-summary promotion. Therefore, the route is accepted as a valid internal candidate *within its current, clearly defined boundaries*.
