# Goal 21 Iteration 1 Pre-Implementation Report

## Proposed Program Decomposition

This work should be split into three goals instead of one oversized reproduction round.

### Goal 21

Freeze:

- the paper artifact matrix
- dataset provenance
- local reduced-size runtime profiles
- unresolved blockers

### Goal 22

Address only the semantic/runtime/reporting gaps required by that matrix.

### Goal 23

Execute the bounded local Embree runs and generate the final reproduction report.

## Why This Split Is Necessary

1. It keeps the review loop honest.
   Dataset claims, workload claims, and runtime claims should not all move at once.

2. It makes the `5–10 minute` runtime budget enforceable.
   The profile policy should be frozen before implementation and runs.

3. It prevents accidental scope creep.
   Goal 22 should only fix blockers that Goal 21 actually names.

## Proposed Goal 21 Outputs

1. a frozen paper-artifact mapping
2. a provenance ledger for datasets
3. reduced local profiles for:
   - `lsi`
   - `pip`
   - `overlay`
   and any other paper-required slices
4. a blocker list for Goal 22

## Review Questions

1. Is the 3-goal decomposition technically sound?
2. Is Goal 21 the correct first step?
3. Is the `5–10 minute` local-budget rule reasonable?
4. Should implementation begin with Goal 21?
