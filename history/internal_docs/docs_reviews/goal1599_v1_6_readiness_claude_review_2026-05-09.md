---

## Independent Review: Goal 1599 — v1.6 Python+RTDL Historical Milestone Readiness

---

### Verdict

**ACCEPT** as a readiness/boundary artifact.

The report correctly characterizes the current state as "not ready to publish," names every required gate before closure, and avoids authorizing a release. It is safe to use as a scoping and planning anchor. It is not, and does not pretend to be, release authorization.

---

### Strengths

**Scope alignment is exact.** The "Historical Definition" and "Intended claim" framing matches the stated v1.6 intent precisely — Python+RTDL closure, not Python+partner+RTDL. The roadmap triplet (`v1.5.x` finish → `v1.6` close → `v1.7–v2.0` partner) is stated explicitly and correctly.

**"Must Not Claim" section is comprehensive.** All five categories the user flagged as forbidden (whole-app speedup, broad RTX/GPU acceleration, true zero-copy, partner support, package-install) appear as explicit prohibitions. The threshold-4 OptiX gated-candidate is specifically called out — that is a precision few readiness documents achieve.

**COLLECT_K_BOUNDED handling is conservative.** The report describes its status accurately (experimental promotion track, reduced-copy evidence, gated candidate) and blocks any stable-promotion claim until an explicit release-surface decision is made. It does not conflate "progress toward promotion" with "promoted."

**Copy/memory language is disciplined.** The report distinguishes reduced-copy and host typed-buffer reuse from true zero-copy throughout, and lists harmonizing that language as a blocker. This directly closes the most common source of silent overclaim in RT/GPU projects.

**3-AI consensus gate is preserved.** The closure blockers explicitly require consensus before declaring v1.6 done. The report does not itself constitute or waive that gate.

**Work queues are correctly stratified.** No-pod and pod queues are separated, pod is deferred until local preparation is batched, and the pod batch is scoped to the exact v1.6 surface. This is operationally sound.

---

### Blockers or Required Fixes

These are issues with the report document itself, not with the project state.

**1. "Supported Python applications" is ambiguous in the intended claim (line 12–15).**

> "...path for the RT-shaped primitive portion of *supported Python applications*..."

"Supported Python applications" could be read as "applications we have partnered with" or "a broad class of apps." The intended meaning is "Python programs that call RTDL primitives." Tighten to something like: "Python programs that call RTDL-managed RT primitives" or "Python caller code that invokes RTDL's RT primitive surface."

**2. "app-agnostic native internals if compatibility/proof entry points remain" (line 109) is opaque.**

This blocker will not be actionable for anyone who was not in the original discussion. The report should define what "compatibility/proof entry points" means here — presumably, internal symbols or dispatch paths that carry application-specific names or semantics rather than primitive-level contracts. Without that definition, the auditor doing the native boundary audit has no clear pass/fail criterion.

**3. The "Current Evidence" section reads as a status list, not an evidence checklist.**

Bullets like "has progressed... into a measured promotion track" describe trajectory, not completion. For a readiness artifact this is defensible, but the section should add a header note or sentence clarifying that these items establish *foundation*, not *closure*. Without that, a reader skimming the section could read the bullet list as satisfied requirements rather than in-progress evidence.

---

### Overclaim Check

No overclaims found in the report itself. Checked:

- **"high-performance"** (line 12): scoped to "Embree+OptiX path for the RT-shaped primitive portion" — not asserted broadly. Acceptable.
- **"accelerates...where evidence exists"** (line 92): the hedge "where evidence exists" is present and correctly placed.
- **"reduced-copy evidence"** (line 61): zero-copy language is avoided; the v1.5.3/v1.5.4 separation is cited correctly.
- **"measured Python+RTDL promotion track"** (line 58–62): describes status without claiming promotion. Correct.
- **"OptiX gated-candidate performance experiments"** (line 63): experimental framing is maintained.

The report does not introduce any language that would let a release communicate a broader claim than the stated boundary.

---

### Recommendation

Accept this artifact as a readiness/boundary document. Before any v1.6 publication action:

1. Fix the two language issues above (ambiguous "supported Python applications"; unexplained "compatibility/proof entry points") — both are quick edits.
2. Add a single-sentence clarification to "Current Evidence" that the bullets document foundation, not closure.
3. Proceed with the no-pod work queue as written: release-surface proposal, docs audit, symbol audit, regression tests, pod runbook.
4. Do not initiate pod work or draft public-facing v1.6 language until the release-surface proposal exists and has Claude+Gemini review.

The report's own final line — "do not publish it yet" — is the correct position and should be preserved verbatim in any derivative artifact.
