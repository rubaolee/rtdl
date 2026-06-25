## Amendment Closure Review: V4 Forward Goals

**Reviewer:** Claude Sonnet 4.6 (external)
**Date:** 2026-06-24
**Subject:** Verify R1/R2/R3 applied; rule on goal4616 authorization

---

## Verdict

**`amendments_satisfied_begin_goal4616`**

---

## R1 — goal4619 exit gate must require Claude review before goal4620 begins (both Go and No-Go paths)

**Satisfied.** The amended exit gate reads verbatim:

> *"A Go verdict must be submitted to Claude review before `goal4620` implementation begins. A No-Go verdict requires Claude review of the fallback candidate before `goal4620` begins."*

Both paths are gated. The self-authorization gap is closed.

---

## R2 — goal4620 fallback route must name Claude review as required seat for fallback candidate selection

**Satisfied.** The fallback route now reads:

> *"If `goal4619` is No-Go, select the next candidate from the inventory by Claude review before implementation begins."*

Claude is explicitly named. The team-judgment-only path is closed.

---

## R3 — goal4622 kill criteria must be stated as measurable thresholds before any spike implementation runs, with at minimum overhead ceiling, compile-reliability floor, and correctness-parity requirement

**Satisfied.** The amended tasks section now requires:

> *"kill criteria must be measurable and fixed before any spike implementation runs, including at minimum: an overhead ceiling, a compile-reliability floor for the pinned toolchain, a correctness-parity requirement."*

All three required components are named. The post-hoc falsifiability gap is closed.

---

## Non-Blocking Recommendations N1–N4

All four adequately addressed:

- **N1** — Native code exception narrowed to comment-only/string-constant changes or test compilation probe with no new API surface. Present verbatim in goal4616 forbidden section.
- **N2** — goal4616 exit gate now includes: *"The status ledger must not introduce claim-status changes that are not already authorized by existing code, evidence, and prior reviews."* Guard is present.
- **N3** — Both goal4617 and goal4618 exit gates now include: *"Claude review is required before a promotion decision is finalized."* Explicit seat named in both.
- **N4** — "Development-state publication" replaced with "Development-state documentation disclosure" in goal4623 exit gate. Scoping is resolved.

---

## Authorization

**Codex may begin goal4616.** All three required amendments are applied. All four non-blocking recommendations are adequately addressed. goal4616 is a consolidation and audit goal with no native implementation and no candidate promotion — nothing in R1, R2, or R3 touches its structure. The 3-AI debt for goal4615 should be recorded as review debt per the procedure stated in goal4615's completion review section; it is not a blocker.

goal4617 and later goals remain blocked until goal4616 is complete and its exit gate is met.

---

## Non-Authorization

This review does not authorize: V4 release, measured-catalog promotion of any candidate, broad V4 speedup wording, whole-app speedup wording, true-zero-copy public wording, Tier-3 callback support, raw OptiX callback support, embedding/C-ABI/non-Python host work, or app-specific native kernels.
