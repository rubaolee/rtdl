# V4 Goals4721-4723 Final Release Path

Date: 2026-06-26

Status: `planned_and_partially_actionable`

## Current Starting Point

Goal4720 converged the machine state:

- V4 front door: Python eDSL/operator-pushdown release candidate.
- Measured surfaces: `10`.
- Current candidates: `0`.
- Full V4 local test suite: `435 OK`.
- Catalog dry-run gate: `passed`.
- Formal public tag: still blocked by external 3-AI review debt.

## Goal4721 External Review Closure Packet

Purpose: close the review debt for the current Goal4717-4720 release-candidate
state without reopening old process churn.

Inputs:

- `future/v4/reviews/call_for_review_v4_goal4720_release_candidate_guardrail_convergence_2026-06-26.md`
- Goal4717, Goal4718, Goal4719, Goal4720 reports and evidence.

Exit gate:

- At least one external reviewer verdict is recorded immediately if available.
- If not available, keep explicit debt open and continue only work that does
  not require final tag authorization.
- Final public tag remains blocked until the required 3-AI final release rule is
  satisfied or the user explicitly changes the rule.

Forbidden:

- creating fake internal reviewers;
- treating review debt as approval;
- asking reviewers to approve broad app-level speed wording.

## Goal4722 Clean-Tree And Release-Packaging Gate

Purpose: prove the local source tree can be packaged and that public examples,
docs, and tests still work from the release surface.

Tasks:

- Run full V4 tests after Goal4720 changes.
- Run catalog dry-run gate and store evidence.
- Run public examples that do not require CUDA.
- Build a source/wheel package if local build tooling is available.
- Record any packaging blockers explicitly instead of hiding them.

Exit gate:

- V4 tests pass.
- Public no-CUDA examples pass.
- Package build either passes or records a concrete missing-tool/blocker with
  exact command output and next action.
- No stale public docs say old `8 measured + 1 candidate` state.

Forbidden:

- tagging with uncommitted evidence unaccounted for;
- silently ignoring package build failure;
- adding new performance claims during packaging.

## Goal4723 Final Tag Decision

Purpose: decide whether the repository can tag V4.0.0.

Inputs:

- Goal4720 machine convergence.
- Goal4721 external review closure.
- Goal4722 clean/package gate.
- Current `README.md`, `docs/current_v4_status.md`, tutorials, examples, and
  future/v4 front door docs.

Exit gate for tag:

- External review debt closed.
- Clean/package gate passed or its only blockers are explicitly accepted by the
  user.
- Public wording exactly matches the bounded release-candidate truth:
  Python eDSL/operator-pushdown, 10 measured surfaces, custom predicate
  early-exit, no broad legacy all-app speedup.

If the gate passes:

- tag as a bounded V4 Python eDSL/operator-pushdown release.

If the gate fails:

- do not tag;
- record exact blockers and continue engineering.

## Expected Time

If external review is available quickly:

- Goal4721: 1-3 hours.
- Goal4722: 2-5 hours depending on package tooling and no-CUDA example drift.
- Goal4723: 1-2 hours after review and package evidence.

If external review is delayed:

- engineering can continue under review debt, but final tag remains blocked.

## Non-Authorization

This plan does not authorize broad V4 speedup wording, whole-application
speedups, all-benchmark speedups, public true-zero-copy claims, arbitrary
callbacks, raw OptiX callbacks, blanket CuPy performance claims, C ABI,
embedding, non-Python host bindings, app-specific native kernels, or final tag
without the required review/packaging gates.
