# Goal 212: v0.4 Full Audit

## Objective

Perform one full-slice audit of the entire `v0.4` nearest-neighbor line:

- code
- docs
- process / closure trail
- verification evidence

## Scope

Audit the `v0.4` line from Goal 196 through Goal 211, covering:

- `fixed_radius_neighbors`
- `knn_rows`
- contracts
- DSL/lowering
- truth paths
- native CPU/oracle
- Embree
- external baselines
- public examples
- bounded scaling note
- preview release surface
- workload / research foundations page
- goal-by-goal report and review trail

## Non-Goals

- no `v0.4` tag or release claim in this goal
- no GPU nearest-neighbor closure
- no new workload family

## Acceptance

- one consolidated verification slice is rerun
- one consolidated audit report is written
- one external AI audit reviews the whole `v0.4` line
- the audit states clearly whether the current `v0.4` line is:
  - internally consistent
  - honestly documented
  - ready for final release packaging work or still blocked
