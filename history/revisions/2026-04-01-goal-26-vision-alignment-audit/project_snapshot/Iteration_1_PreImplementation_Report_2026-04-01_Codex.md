# Iteration 1 Pre-Implementation Report

## Proposed Scope

Goal 26 is a full-project framing audit and revision round.

It will review:

- project framing docs
- `docs/rtdl/` user-facing language docs
- current status docs
- architecture notes
- key runtime/compiler files in `src/rtdsl/`
- `src/rtdsl/__init__.py`
- relevant scripts and history/dashboard artifacts

The round is not about adding new backends. It is about making the repository internally consistent with the current project vision:

- RTDL is broader than RayJoin
- RTDL is broader than Embree
- RTDL v0.1 is still a RayJoin-focused vertical slice
- the currently real local execution backend is Embree only

The main code-level audit targets now explicitly include:

- `RayJoinPlan`
- `lower_to_rayjoin(...)`
- schema names/IDs carrying `rayjoin`
- `backend="rayjoin"` as a user/compiler-facing concept

Goal 26 must decide whether those are:

- acceptable v0.1-local names with clarifying comments, or
- structural misframings that should be renamed now

## Expected Revisions

- wording and structure changes in top-level docs
- architecture clarification where the current IR/runtime is still overly RayJoin-shaped
- possibly structural-name changes if the audit concludes current names are no longer acceptable
- cleanup of any stale comments or docs that imply current multi-backend realization when only future intent exists
- dashboard/history consistency updates if needed

## Risk

The main risk is semantic drift, but code-level renaming would also create real breakage risk:

- overclaiming current backend generality
- underdescribing the long-term backend-unification goal
- mixing whole-project ambition with v0.1-local reality
- renaming structural symbols without fully updating their uses in tests, docs, codegen, schemas, and reports

## Requested External Review

Claude should judge whether this scope is strong enough for a true vision-alignment audit rather than a README cleanup.

Gemini should monitor whether the process remains aligned with the stated whole-project and v0.1 hierarchy.

Historical goal-specific planning docs should be treated as archived artifacts by default unless they are still referenced by active framing docs.
