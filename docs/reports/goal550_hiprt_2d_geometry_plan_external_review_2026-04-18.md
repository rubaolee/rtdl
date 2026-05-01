# Goal 550: HIPRT 2D Geometry Lowering Plan — External Review

Date: 2026-04-18
Reviewer: Claude (Sonnet 4.6)
Verdict: **ACCEPT**

## Summary

The plan is technically sound and ready for implementation. No blockers.

## Strengths

**Lowering design is correct.** Using HIPRT AABB-list custom primitives with Z fixed at 0 is the canonical approach for projecting 2D geometry into a 3D RT pipeline. The separation of HIPRT-backed broad-phase candidate discovery from exact custom-intersection refinement is the right architecture — it keeps the heavy traversal on GPU and the geometry-specific logic in per-primitive kernels.

**Probe ray patterns are appropriate.** Segment-as-ray with `maxT=1`, point-as-epsilon-probe, and polygon-as-boundary-segment-set are all coherent with how custom primitives and HIPRT traversal work. These patterns will compose correctly with multi-hit row emission.

**Integrity constraints are explicit and enforceable.** The prohibition on silent `rt.run_cpu_python_reference` fallback and the requirement that HIPRT must own the heavy candidate/refinement work (not just broad phase) are the right guardrails. These prevent the "pretend-HIPRT" problem the plan calls out explicitly.

**Execution order is sound.** Starting with `segment_intersection` (simplest, exercises multi-hit emission) before scaling to `overlay_compose` and `point_nearest_segment` is the right pedagogical and de-risking sequence.

**Performance position is honest.** Correctness-first, no RT-core speedup claims on GTX 1070, and deferred benchmarking until after correctness passes are all appropriate for this hardware profile.

**Bounded constraints are conservative and safe.** Explicit overflow errors instead of silent truncation, uint32_t geometry counts, and documented per-query buffer ceilings give the implementation clear invariants to test against.

## Minor Notes

- `point_nearest_segment` is correctly flagged as potentially correctness-first and not performance-forward if candidate expansion requires broad traversal. The plan's documentation requirement for this case is sufficient — no design change needed.
- `overlay_compose` depends on LSI and PIP patterns being validated first; the execution ordering already accounts for this.

## Blockers

None.

## Conclusion

ACCEPT. The plan defines a correct, honest, and implementable approach for all seven 2D workloads. It may proceed to implementation after 3-AI consensus is complete. Codex: ACCEPT. Claude: ACCEPT.
