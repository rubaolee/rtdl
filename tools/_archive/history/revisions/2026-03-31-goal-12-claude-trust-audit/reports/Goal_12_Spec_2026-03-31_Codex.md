# Goal 12 Spec (2026-03-31, Codex)

## Goal

Process the first independent Claude trust audit report, revise the repository
where the report identifies real correctness or consistency gaps, and close the
round only after Claude confirms that the revised repository is an audited
version with no remaining blockers for the audited scope.

## Scope

This round focuses on the discrepancies identified in:

- `trust_audit_2026-03-31.md`

Current expected work items:

1. remove or correctly implement the silent `boundary_mode` behavior for PIP
2. correct the Goal 10 backend-plan/runtime over-claim around BVH/Embree usage
3. fix the LSI Embree all-hits correctness risk
4. integrate Goal 10 workloads into baseline/evaluation infrastructure, if the
   discrepancy is accepted as an actionable gap for the audited baseline

## Required Closure

Goal 12 closes only if:

1. the Claude report is archived in history
2. Codex writes a response/rebuttal
3. Claude provides a revision plan / acceptance bar
4. the repository is revised accordingly
5. Claude re-reviews the revised snapshot
6. the final result is explicit Claude/Codex agreement that the repository is an
   audited version for the scoped concerns
