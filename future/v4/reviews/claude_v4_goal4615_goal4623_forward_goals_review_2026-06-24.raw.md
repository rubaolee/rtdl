I have everything I need. The existing forward-goals review file is empty — this is the first entry. Here is the full review.

---

## External Review: V4 Forward Goals `goal4615`–`goal4623`

**Reviewer:** Claude Sonnet 4.6 (external)
**Date:** 2026-06-24
**Subject:** Forward goals plan for V4 next work sequence
**Prior reviews consulted:** grouped-i64 candidate review (R1-R4 verified), point-group amendment closure review (A1-A3 verified), V4 README current state confirmed (3 measured, 2 candidates)

---

## Verdict

**`accept_with_required_amendments`**

The plan is structurally sound. The ordering is correct, the failure-mode awareness is explicit, and the separation between candidate evidence and promotion decisions is properly gated. Three required amendments must be applied before implementation may begin; none require restructuring the goal sequence.

---

## Findings by Severity

### REQUIRED — must be applied before any implementation

**R1 — goal4619 exit gate does not establish Claude review as an explicit prerequisite for goal4620 implementation**

goal4619's exit gate is binary (Go/No-Go) and self-contained. That is correct for a feasibility audit. But goal4620 is a native implementation goal, and Global Rule 2 states "Claude review is required before... new native surface implementation." As currently written, a Go finding from goal4619 is structurally ambiguous — it could be read as self-authorizing goal4620 to proceed without a separate Claude review of the verdict. The prior failure mode was exactly this: a self-generated finding being treated as authorization. The exit gate of goal4619 must be amended to include: *"A Go verdict must be submitted to Claude review before goal4620 implementation begins. A No-Go verdict requires Claude review of the fallback candidate before goal4620 begins."*

**R2 — goal4620 fallback route does not name Claude review as a required seat for fallback candidate selection**

The current text reads: "select the next candidate from the inventory by review." It does not specify who reviews. Selecting a fallback implementation candidate is a "major decision" under Global Rule 2. If goal4619 is No-Go, the choice of what to implement next is not a self-authorizing team judgment — it requires Claude review explicitly named in the gate. Amend goal4620 to state: *"If goal4619 is No-Go, fallback candidate selection requires Claude review before implementation begins."*

**R3 — goal4622 kill criteria are unspecified as measurable thresholds**

"Kill criteria" appears as a required task output in goal4622, but no constraints on what the kill criteria must contain are specified here. A spike protocol with kill criteria written post-hoc to match what was observed is not falsifiable. The goals document must commit to requiring that the Tier-3 spike protocol's kill criteria include: (a) at least one measurable overhead threshold stated before any spike implementation runs, (b) a compile-reliability floor for the pinned toolchain, and (c) at least one correctness-parity requirement. Without this, goal4622's "falsifiable spike protocol" claim is not enforceable from the goals level.

---

### NON-BLOCKING — recommended before or during implementation

**N1 — goal4616 "trivial wording/test fix" exception for native code is vague**

The forbidden section reads: "no new native code unless needed for a trivial wording/test fix." A consolidation goal that discovers a native gap could exploit this exception. Narrow it to: no new native code unless it is a comment-only or string-constant change within existing native files, or a test compilation probe that does not add new native API surface.

**N2 — goal4616 exit gate does not guard against claim upgrading during consolidation**

The status ledger task is an audit, not a classification change. But the exit gate only checks that the ledger "matches code/catalog evidence" — it does not explicitly forbid the ledger from resolving wording-debt items or reclassifying candidates. Add: *"The status ledger must not introduce claim status changes not already authorized by existing code, evidence, and prior reviews."*

**N3 — goal4617 and goal4618 exit gates do not explicitly name Claude as a required seat for promotion authorization**

Both exit gates use "External reviewers either authorize... or require keeping candidate status." Global Rule 2 covers this, but the exit gate language should echo it to prevent "3-AI consensus" being read as a path around Claude pre-authorization. Recommended addition to each: *"Claude review is required before a promotion decision is finalized, per Global Rule 2."*

**N4 — goal4623 "development-state publication" is ambiguous**

The exit gate option reads "Development-state publication authorized with no release-speedup wording." Publication to what channel? Internal documentation, a public repo README, and a PyPI release are categorically different authorization decisions. Replace "publication" with "development-state documentation disclosure" or add a scoping clause specifying where disclosure is authorized.

---

## Answers to the Seven Review Questions

**Q1 — Is the goal4615–goal4623 ordering correct, or does any goal need to move?**

The ordering is correct. Consolidation (4616) precedes promotion decisions (4617–4618), which precede catalog hardening (4621) that reflects their results. The 3D feasibility gate (4619) correctly precedes any new implementation (4620). The Tier-3 protocol definition (4622) correctly precedes the release candidate decision (4623), because the RC decision requires knowing Tier-3's classification. The sequential arrangement of 4617 and 4618 is preferable to parallelism because both goals modify the same catalog state — serial ordering avoids race conditions in measured-surface counts and partner classification.

No goals need to move.

**Q2 — Does the plan avoid process churn while respecting review/consensus requirements?**

Yes. The single-control-plane approach is sound. The "goal-level decision audit" section correctly identifies the churn risk and provides an escape hatch ("collapse into next implementation goal and preserve only the evidence gate"). The plan is short enough to be reviewed once and specific enough to be executed against. The sequential structure avoids the need for synchronized multi-branch reviews that were a churn source in prior work. The biggest churn risk would be treating goal4615 as incomplete until Antigravity/third-seat debt is cleared — the plan correctly defers that debt rather than blocking forward motion.

**Q3 — Are grouped-i64 and point-group promotion decisions correctly separated from candidate evidence and amendment closure?**

Yes, with no gaps. goal4617 lists R1-R4 as required work before a promotion decision can be made — not R1-R4 as promoters themselves. goal4618 explicitly forbids treating amendment closure (which I accepted in the point-group amendment closure review) as automatic promotion. Both goals have separate exit gates requiring external reviewer authorization for any promotion. The current review state is:
- grouped-i64: R1-R4 open, POD gate passed, promotion decision pending
- point-group: A1-A3 closed, POD gate passed, promotion decision pending

The goals document correctly treats both as "next step is a separate promotion decision package" rather than "amendment closure authorizes catalog entry."

**Q4 — Is goal4619 the right guard against falsely wrapping the existing 3D fixed-radius host-query route as a V4 device-array surface?**

Yes. The four audit criteria (search point device columns, query point device columns, output device columns, no host query-row materialization in the measured hot path) are exactly the right criteria for distinguishing a true device-array surface from a prepared-search wrapper. The binary Go/No-Go exit gate is appropriate — there is no "partial device-array" category. The "known danger" identified in the current V4 ground truth maps precisely to what goal4619 guards against.

The one gap is addressed in R1: the Go verdict must not be self-authorizing for implementation. The feasibility finding requires Claude review before goal4620 begins. As amended, goal4619 is the correct guard.

**Q5 — Are the Tier-3 constraints strict enough for complex user callbacks?**

The shape constraints are appropriate. "Scalar per-hit reduce only" eliminates shared mutation, dynamic allocation, variable-length output, and recursive/spawned action logic in a single constraint. The rejected-shapes list correctly enumerates what "scalar per-hit reduce" excludes, making the accepted shape legible without requiring interpretation. "Pinned toolchain assumptions" is the right anchor to prevent the spike from drifting across Numba/CUDA versions after initial success.

The specific gap is R3: kill criteria without measurable thresholds are not falsifiable. The constraints are strict enough in shape, but "falsifiable spike protocol" is only falsifiable if the kill criteria are stated as measurable thresholds before any spike run. The goals document must commit to requiring this in the protocol document goal4622 produces.

**Q6 — Are any goals missing correctness parity, POD evidence, claim boundary, or non-authorization gates?**

- **Correctness parity:** Present in goal4617 (R1 includes GPU-mode gate), goal4618 (promotion gate must cover mixed fixture), goal4620 ("compare against the older route"). Not explicitly named in goal4616's exit gate — consolidation shouldn't need it, but see N2.
- **POD evidence:** Correctly required in goal4617 (if promotion proposed), goal4618 (if promotion proposed), goal4620 (candidate-level POD required before next goal). Not required for goal4619 (feasibility audit, not implementation), goal4622 (protocol definition, not execution), or goal4621 (catalog hardening, not new surfaces). The POD scoping is correct.
- **Claim boundary:** goal4621 handles this as its primary task. Individual forbidden sections guard against claim boundary violations in each goal. The non-authorization footer on the goals document itself is comprehensive.
- **Non-authorization gates:** Present and complete. Each goal's forbidden section lists specific non-authorizations. The document-level non-authorization section covers the full V4 danger list (release, promotion, broad speedup, true-zero-copy, Tier-3 support, raw callbacks, C-ABI, app-specific kernels).

Two gaps: N2 (goal4616 exit gate does not guard claim upgrades) and R3 (goal4622 kill criteria not specified as measurable). Both addressed above.

**Q7 — What amendments are required before implementation may begin?**

Three amendments, all to the goals document itself:

1. **(R1)** Add to goal4619's exit gate: a Go verdict must be submitted to Claude review before goal4620 implementation begins; a No-Go verdict requires Claude review of the fallback candidate before goal4620 begins.
2. **(R2)** Add to goal4620's fallback route: if goal4619 is No-Go, Claude review of the fallback candidate selection is required before implementation begins.
3. **(R3)** Add to goal4622's tasks: the spike protocol's kill criteria must be stated as measurable thresholds before any spike implementation runs, including at minimum an overhead ceiling, a compile-reliability floor, and a correctness-parity requirement.

Four non-blocking recommendations (N1-N4) are listed above and should be applied but do not block implementation.

---

## Authorization to Begin goal4616

**Codex may begin goal4616 after the following two conditions are met:**

1. Required amendments R1, R2, and R3 are applied to this goals document.
2. The amended document is recorded under `future/v4/reviews/` as required by goal4615's exit gate.

goal4616 is a consolidation and audit goal with no native implementation. None of the required amendments touch goal4616's structure, tasks, or exit gate. The 3-AI completion consensus for goal4615 should record Antigravity/third-seat as review debt per the procedure stated in goal4615's completion review section — this is not a blocker on beginning goal4616.

goal4617 and later goals may not begin until goal4616 is complete and its exit gate is met.

---

## Non-Authorization

This review does not authorize:

- V4 release or V4.0 release announcement
- Measured-catalog promotion of `v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays`
- Measured-catalog promotion of `v4_point_group_nearest_witness_2d_device_arrays`
- Broad V4 speedup wording or whole-application speedup wording
- True-zero-copy public wording on any surface
- Tier-3 callback support or raw OptiX callback support
- Embedding/C-ABI/non-Python host work
- App-specific native kernels
- CuPy performance claims
- Any implementation before the required amendments are applied and this goals plan is accepted

---

**Summary:** The plan is well-structured and shows genuine failure-mode awareness. Three required amendments tighten the goal4619→4620 handoff, the fallback candidate selection gate, and the Tier-3 kill-criteria commitment. Once applied, Codex may begin goal4616.
