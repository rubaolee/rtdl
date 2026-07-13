# Response To Claude Midcheck Review — Goal4973 Amendments

Date: 2026-07-04

Review accepted:

`history/internal_docs/claude_review_midcheck_v2_14_3_after_goal4972_2026-07-04.md`

## Accepted Findings

### 1. LSI Missing Time Is Probably Amortizable

The review correctly points out:

```text
fresh bounded route   ~= 5.2776s = LSI 2.6887s + downstream ~2.589s
prepared replay route ~= 2.5691s = LSI 0.0090s + downstream ~2.560s
```

This strongly suggests that the `~2.686s` LSI missing time is one-time setup / compile / workspace
cost, not steady-state traversal.

### 2. Downstream Floor Is Persistent

The `~2.56s` downstream cost remains almost unchanged between fresh and prepared replay. Therefore,
even if LSI setup is fully amortized, the binary operator remains bounded by the downstream floor.

### 3. Goal4973 Must Not Only Measure LSI

The original Goal4973 was too narrow. It targeted the LSI producer gap but did not force a
simultaneous decomposition of the persistent downstream floor.

## Amendments Applied

Updated:

`history/internal_docs/goal4973_exact_lsi_producer_cost_decomposition_goal_2026-07-04.md`

Changes:

- renamed scope to "Exact LSI Producer And Downstream Floor Cost Decomposition"
- added the replay arithmetic as a gating premise
- added downstream phase decomposition:
  - reprojection
  - map0/map1 sort
  - vertex PIP wrappers
  - midpoint generation
  - midpoint PIP
  - midpoint face assignment
  - carrier construction
  - downstream consumer
- added explicit separation of:
  - one-time / amortizable setup cost
  - per-overlay fresh cost
  - prepared/replay steady-state cost
- added exit label:
  `steady_state_cost_dominated_by_downstream_floor`

Updated:

`history/internal_docs/call_for_review_goal4973_exact_lsi_producer_cost_decomposition_goal_2026-07-04.md`

Changes:

- updated requested verdict
- added review questions for the persistent downstream floor
- added a review question asking whether the next target should be downstream rather than LSI

## Execution Boundary

Goal4973 remains a measurement/instrumentation goal.

Allowed:

- phase timing instrumentation
- same-process repeated-run diagnostics
- prepared replay downstream floor decomposition
- environment compile-path measurement

Not allowed:

- RayJoin-specific core kernel
- performance headline
- author-speed claim
- Layer 4 / callback / fusion claim
- public release wording change
- optimization implementation before the phase table chooses the branch

## Current Next Step

Run amended Goal4973 after review/authorization.

The expected honest outcome is likely:

```text
LSI setup/compile/workspace is amortizable;
steady-state binary overlay is then dominated by downstream ~2.56s;
next optimization target must be whichever downstream phase dominates.
```

But this must be confirmed by measurement, not assumed.
