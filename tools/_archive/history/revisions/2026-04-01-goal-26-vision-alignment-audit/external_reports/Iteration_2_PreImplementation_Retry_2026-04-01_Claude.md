---

## Goal 26 Pre-Implementation Scope Review

### Findings by Severity

---

**[CRITICAL] Code-level architecture misnames RayJoin as a backend**

The most serious misalignment is not in the docs — it is structural in the source code itself. The Iteration 1 report identifies code review as a scope item but does not name the specific symbols where RayJoin is hardwired as an architectural concept rather than an application target.

Concrete findings:

- `src/rtdsl/lowering.py:33` — `def lower_to_rayjoin(kernel) -> RayJoinPlan:` and `if kernel.backend != "rayjoin":` — the lowering function and its backend guard treat "rayjoin" as a backend name, contradicting the vision's clear statement that backends are Embree, OptiX, HIP RT, etc. RayJoin is an *application*, not a backend.
- `src/rtdsl/ir.py:7` — `RAYJOIN_PLAN_SCHEMA_ID = "https://rtdl.dev/schemas/rayjoin-plan-v1alpha1.json"` — the core IR schema URI is namespaced under "rayjoin-plan," encoding RayJoin as the permanent target of the IR rather than one application of it.
- `src/rtdsl/api.py:38` — the hardcoded lowering plan description says "Lower traversal and refine stages into **RayJoin-compatible** RT operations." This is embedded in the compiler's self-description.

These are the highest-priority findings because they misrepresent the architecture in ways that will mislead any future developer reading the code, and they encode a naming decision (`backend="rayjoin"`) that is directly contradicted by both `vision.md` and `v0_1_final_plan.md`.

---

**[HIGH] Pre-implementation report underweights code-level risk**

The Iteration 1 report says: *"The main risk is not technical breakage."* This is only true if code changes are limited to docstrings and comments. But if the audit correctly concludes that `lower_to_rayjoin` should be renamed and the schema ID corrected, there *is* breakage risk — tests, imports, and any external artifact that names these symbols. The plan must explicitly decide:

> Is code-level renaming in scope?

If yes: test coverage must be verified before renaming, and any test that passes `backend="rayjoin"` (rather than `backend="embree"` or a generic string) needs to be identified. The risk statement should be revised accordingly.

---

**[HIGH] `scripts/` directory dropped from Iteration 1 scope**

Goal 26's own spec lists `scripts/` as an explicit review target. The Iteration 1 report does not mention it. Scripts are often where the oldest framing leaks through — hardcoded workload names, backend labels, report titles — and they are visible to any user who runs the project. This is a gap that should be restored before implementation begins.

---

**[MEDIUM] Public API surface (`__init__.py`) not listed**

Neither the Goal 26 spec nor the Iteration 1 report mentions `src/rtdsl/__init__.py`. Whatever `import rtdsl` exposes is the face of the DSL. If it re-exports `lower_to_rayjoin`, `RayJoinPlan`, or other RayJoin-named symbols as first-class API, that is a direct framing violation that will affect every user and every example in the docs.

---

**[MEDIUM] Framing decision for goal-specific planning docs is unresolved**

`docs/` contains ~15 goal-specific planning docs (`goal_10` through `goal_25`) that were written under progressively evolving framings. Neither document addresses whether these are in scope. The likely right answer is "explicitly out of scope as historical records," but leaving this implicit means the implementer may either waste time auditing them or miss real misframing that crept into docs that are still referenced by the current README.

---

**[LOW] `rayjoin_artifacts.py` and `goal23_reproduction.py` are correct but unverified as labeled**

Files like `src/rtdsl/rayjoin_artifacts.py`, `paper_reproduction.py`, and `goal23_reproduction.py` are RayJoin-specific by design and appropriate for v0.1. The audit should verify they are clearly labeled as v0.1 application-slice artifacts, not as core DSL infrastructure. The spec says this is in scope but the Iteration 1 report does not call out these files by name.

---

### Scope Revisions

1. **Add a code-symbol audit step** as a named, first-class item: enumerate `lower_to_rayjoin`, `RAYJOIN_PLAN_SCHEMA_ID`, `backend="rayjoin"` guard, and `RayJoinPlan` output type. Decide explicitly whether each should be renamed (preferred), left as-is with a clearly scoped comment, or documented as a known v0.1 simplification.

2. **Restore `scripts/`** to the Iteration 1 scope description. It is already in the spec; the pre-implementation report dropped it.

3. **Add `src/rtdsl/__init__.py`** to the code review list.

4. **Revise the risk statement**: change "main risk is not technical breakage" to "docs-only changes carry no breakage risk; code-level renaming requires test-impact assessment first."

5. **Explicitly resolve the goal-planning-doc question**: recommend treating `docs/goal_10` through `docs/goal_25` as frozen historical records, out of scope for Goal 26 unless a specific doc is still referenced by an active framing doc.

---

`Consensus to begin audit`

The Goal 26 spec is broad enough to catch everything listed above — it explicitly includes `src/rtdsl/` code. The Iteration 1 report's scope needs the revisions above applied before the first implementation step, specifically the code-symbol audit, so that the most critical findings (lowering backend name, IR schema ID) are not treated as optional doc cleanup and are addressed head-on.
