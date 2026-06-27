# Goal594 Planning Review — Claude (Sonnet 4.6)

Date: 2026-04-19

Reviewing: `docs/reports/goal594_v0_9_2_apple_rt_performance_plan_2026-04-19.md`

## Verdict: ACCEPT with conditions

The plan's evidence-first framing, explicit non-goals, and forbidden-wording policy are correct. The structure earns an ACCEPT. The four conditions below address concrete risks that could stall the release or introduce subtle correctness bugs.

---

## What the Plan Gets Right

- Baseline numbers are already recorded and public (8.8x, 1664x, 9.5x vs Embree). The plan does not pretend the current state is good.
- Each sub-goal has an explicit correctness gate before performance is claimed.
- Non-goals prevent the three historically common failure modes: silent CPU fallback, premature "optimized" branding, and scope inflation from the adaptive-engine hold.
- The three-tier release wording (always acceptable / evidence-conditional / forbidden) is precise and enforceable.
- A 3-AI consensus gate before any public performance wording change is a strong guard for a repo with a public audience.

---

## Risk 1 — Goal595 (Harness) Is an Unlabeled Prerequisite

**Risk:** Goals 596, 597, and 598 each claim "expected benefits" relative to repeated-call overhead, but the plan does not sequence Goal595 as a hard prerequisite. If 596/597/598 are worked first, there is no agreed baseline harness to verify the claimed benefit and regression detection is ad hoc.

**Recommendation:** Explicitly mark Goal595 as a prerequisite for 596/597/598 in the implementation sequence. No performance benefit claim in 596/597/598 is verifiable without the harness output. If any goal is deferred, defer them in reverse order: 598, then 597, then 596, not 595.

---

## Risk 2 — Goal597 Iterative Nearest-Hit Needs a Concrete Epsilon and Pass-Ceiling Policy

**Risk:** The plan describes advancing each ray's `minDistance` beyond its last accepted hit to count additional intersections. Two sub-risks:

1. **Epsilon choice.** A too-small epsilon re-hits the same primitive (double-count). A too-large epsilon skips co-planar or near-coincident triangles (under-count). The plan says "strict parity tests" but does not specify how epsilon is chosen or whether it is geometry-relative or absolute.
2. **Pass ceiling.** The plan documents "a documented ceiling" but gives no formula. Without it the implementation could silently truncate hit counts on dense workloads, and the ceiling is whatever the first author picks.

**Recommendation:** Before implementation starts, record in the Goal597 ticket (or a short design note) the specific epsilon policy (e.g., `max_t * 1e-5` relative, or `1e-6` absolute, with a documented rationale) and the pass ceiling (e.g., `min(triangle_count, 256)`). The parity test fixtures must include at least one co-planar case and one dense-hit case to exercise both failure modes.

---

## Risk 3 — Goal598 Could Be a Pass-Magnifying Dead-End Without a Stopping Criterion

**Risk:** The plan correctly notes MPS `Any` does not supply a defined primitive index, and iterative nearest-hit returns one primitive per pass. For dense all-pair segment-intersection (N left segments × M right segments), iterative nearest-hit could require up to M passes to enumerate all hits for one left segment. If M is large this could be worse than the current per-right-segment AS rebuild loop, not better.

**Recommendation:** Before committing implementation time to the optimized MPS path, bound the break-even point: at what (left_count, right_count, density) does iterative nearest-hit require more dispatches than the current O(right_count) loop? If that analysis shows the MPS path cannot win for representative workloads, write the technical-stop document immediately and spend the time on Goal599 and Goal600 instead. The plan already allows this exit — use it early if the math doesn't work out.

---

## Risk 4 — Goal597 Correctness-Fail Path Is Implicit

**Risk:** The plan says Goal597 delivers a single-AS path "if correctness is proven." It does not say what ships if correctness cannot be proven. A reader could infer the release blocks.

**Recommendation:** Add one explicit sentence to the plan: if Goal597 iterative correctness cannot be proven within the release window, v0.9.2 ships with the existing O(triangle) path plus a documented note that hit-count optimization is deferred to v0.9.3. This prevents the release from silently blocking on a hard algorithmic problem and keeps the release boundary clear.

---

## Summary

| Sub-goal | Status | Gate |
| --- | --- | --- |
| Goal595 Harness | Accept | Must be sequenced first |
| Goal596 Prepared closest-hit | Accept | Correctness parity on bounded fixtures |
| Goal597 Optimized hit-count | Accept with Risk 2 condition | Requires epsilon + ceiling policy before implementation |
| Goal598 Segment-intersection | Accept with Risk 3 condition | Bound break-even before committing implementation time |
| Goal599 Doc refresh | Accept | After code and measurements only |
| Goal600 Pre-release gate | Accept | Strong gate; keep 3-AI consensus requirement |

The overall plan direction is correct. The four conditions above are the gap between "proposed" and "ready to execute." None of them require re-scoping the plan — they require small, written decisions before the first line of implementation code is committed.
