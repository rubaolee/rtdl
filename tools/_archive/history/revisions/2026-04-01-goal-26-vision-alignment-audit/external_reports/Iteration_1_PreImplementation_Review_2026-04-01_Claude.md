The review is complete. Awaiting permission to write the output file. Here is the full assessment:

---

## Goal 26 Pre-Implementation Scope Review

### Findings, Ordered by Severity

**[HIGH] The central IR class is named `RayJoinPlan` — this is not a comment**

The Goal 26 spec says "code comments/docstrings that overfit RTDL to Embree or RayJoin." But the actual overfit is structural: `RayJoinPlan` in `ir.py` is the root IR data model; `lower_to_rayjoin()` in `lowering.py` is the lowering entry point; `backend="rayjoin"` appears six times in `baseline_contracts.py` and as the guard string in `lowering.py`; `schemas/rayjoin_plan.schema.json` is referenced from `plan_schema.py`. None of these are comments. The pre-implementation report names none of them.

The core decision that must be made before implementation: does the audit scope include renaming these, or does it preserve the names and add clarifying comments? Either is defensible — but undecided, this is where the audit will stall or drift.

**[HIGH] `backend="rayjoin"` conflates application domain with execution backend**

"RayJoin" is a formulation strategy and application domain. The execution backends are Embree and OptiX/CUDA. Using `"rayjoin"` as the user-facing backend string fuses these two concepts. This is the deepest conceptual misalignment in the repo and is not named anywhere in the pre-implementation report.

**[MEDIUM] `docs/rtdl/` is entirely absent from the review scope**

The `docs/rtdl/` subdirectory contains `dsl_reference.md`, `programming_guide.md`, `workload_cookbook.md`, and `llm_authoring_guide.md` — four user-facing documents not listed in Goal 26's "What Must Be Reviewed." These are the most likely places to find either overclaiming or underclaiming language.

**[MEDIUM] The pre-implementation report treats this as a wording job**

The report says "wording and structure changes." It should instead categorize each finding type — rename, comment-only, doc-wording — before implementation. Without that, the audit can produce internally inconsistent outputs (e.g., renaming the IR class in one place but not in `codegen.py`'s function signature that takes it as a parameter).

**[LOW] `scripts/` and goal-specific plan docs not enumerated**

All scripts are named `goal15_*`, `goal17_*`, etc. The `docs/` directory has over a dozen goal-specific plan files. The audit should explicitly state whether these are historical artifacts (left as-is) or framing targets.

**[LOW] `api.py:39` docstring uses "RayJoin-compatible RT operations"**

A concrete example of the comment-level overfit the spec is looking for, useful to name explicitly so the implementer knows what to look for.

---

### Scope Revisions

1. Add `docs/rtdl/` to the explicit review list.
2. Add a pre-audit decision point: rename structural names, or comment-only? State the decision explicitly before any code changes.
3. Name the `backend="rayjoin"` conflation as a specific finding requiring a resolution decision.
4. Expand spec language from "comments/docstrings" to "structural names, comments, and docstrings."
5. State explicitly whether goal-specific plan docs are historical artifacts or framing targets.

---

`Consensus to begin audit`
