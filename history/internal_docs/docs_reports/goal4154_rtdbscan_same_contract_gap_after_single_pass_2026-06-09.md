# Goal4154 - RT-DBSCAN Same-Contract Gap After Single-Pass

Date: 2026-06-09

Verdict: design-gap-identified

## What We Learned

Goals4149 and 4150 show that `single_pass_candidate` is a real performance win
inside the prepared direct-status component-signature contract. It matches the
stable direct-status loop on the measured packets and roughly halves replay
work.

Goal4153 shows the important boundary: the fast direct-status component
signature is not the same contract as the conservative current RT-DBSCAN route.
The current route carries core/border/noise semantics, while direct-status
component signatures union radius-connected partitions without caller-supplied
vertex predicates. All 15 Goal4153 rows had mismatched signatures.

## Design Problem

The missing generic primitive is not an app-specific DBSCAN engine path. It is a
predicate-aware fixed-radius grouped-union continuation:

- input: fixed-radius candidate pairs or partition-status scans
- input: caller-supplied vertex predicate flags, such as "eligible for union"
- operation: union only predicate-compatible candidate pairs
- operation: assign non-predicate points through an explicit deterministic
  neighbor-root policy
- output: component labels or component-size signatures plus status metadata

For RT-DBSCAN, the app can supply core flags as the predicate. For other
applications, the predicate may mean a different eligibility rule. The engine
must stay generic.

## Next Engineering Target

Build a measured candidate for predicate-aware direct-status grouped union. The
acceptance bar is same-contract parity against the current RT-DBSCAN
core/border/noise route on tested datasets, not just parity against the
component-signature direct-status route.

## Boundary

Goal4154 does not authorize route promotion, release, public speedup wording,
broad RT-core wording, whole-app benchmark claims, paper reproduction, hidden
dispatch, automatic partner selection, automatic partition-cell-factor
selection, automatic convergence-mode selection, app-specific engine logic,
native ABI additions, AMD claims, or true-zero-copy claims.
