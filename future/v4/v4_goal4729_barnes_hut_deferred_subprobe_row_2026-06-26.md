# V4 Goal4729 Barnes-Hut Deferred/Subprobe Row

Date: 2026-06-26

Status: `complete_pending_external_review_debt`

Decision: `barnes_hut_closed_as_deferred_subprobe_not_complete_app_route`

## Purpose

Goal4729 closes `barnes_hut` for the current complete 10-app matrix as a
deferred/subprobe row. This keeps the real aggregate-frontier progress, while
blocking the false conclusion that V4 has a complete Barnes-Hut app-level route.

Machine-readable row:

- `future/v4/evidence/v4_goal4729_barnes_hut_deferred_subprobe_row_2026-06-26.json`

## What Is Real Progress

Goal4676/4677 promoted:

```text
v4_aggregate_frontier_device_columns_2d_prepared_runner
```

Measured result:

| Metric | Result |
| --- | ---: |
| V4 frontier-only hot over V2.14 | 302.998x |
| V4 full hot over V2.14 | 310.024x |
| V4 full wall over V2.14 | 200.826x |
| V4 full hot over V3.0.2 | 0.998x |

This is a real V2.14 host-frontier bottleneck removal through a clean V4 front
door.

## Why It Is Not A Barnes-Hut App Win

Barnes-Hut needs a complete aggregate-tree weighted-vector force workflow, not
only frontier production. The fused weighted-vector contract currently records:

- device-resident output columns: true;
- hot-path host materialization: false;
- `uses_optix_trace`: false;
- runtime status: CUDA device accumulation, not RT-core traversal.

Therefore the current evidence does not authorize:

- whole-app Barnes-Hut speedup;
- V4-over-V3 speedup;
- RT-core speedup;
- paper reproduction;
- app-specific native engine logic.

## Conclusion

`barnes_hut` is closed for the current matrix as:

```text
closed_deferred_subprobe_not_complete_app_route
```

## Reopen Condition

Only reopen this row as a performance row if a complete app-level generic
aggregate weighted workflow is bound and measured. Aggregate-frontier subprobe
evidence alone is insufficient.

## Next

Proceed to Goal4730: assemble the complete 10-app V2.14-vs-V4 matrix and
interpret the release gate.

## Validation

Local validation:

- `py -m unittest tests.v4_goal4729_barnes_hut_deferred_subprobe_row_test tests.v4_goal4677_aggregate_frontier_promotion_test tests.v4_goal4724_remaining_app_route_gap_audit_test`

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal avoids turning a legitimate aggregate-frontier operator win
   into a complete Barnes-Hut app or RT-core speed claim.

2. If yes, what action made the decision stupid?
   Not applicable. The stupid action would be hiding the V3.0.2 parity caveat or
   the fact that weighted-vector force workflow is not a complete app route.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Keep aggregate-frontier as bounded operator evidence, and reopen
   Barnes-Hut only for a complete generic weighted workflow.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4730 can now assemble the complete 10-app matrix with all five
   previously incomplete rows closed honestly.

## Non-Authorization

Goal4729 authorizes no POD spend, no final V4 tag, no public speed claim, no
Barnes-Hut speedup claim, no whole-app high-performance claim, no broad
V4-over-V2.14 claim, no V4-over-V3 speed claim, no RT-core speedup claim, no
paper reproduction claim, no app-specific native kernel, no arbitrary callback
support, and no hidden V2/V3 fallback.
