# Goal 462: v0.7 DB Kernel App Demo

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The v0.7 DB kernel-form app demo has been added, locally verified, and accepted
with 2-AI consensus.

## Files Added Or Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_v0_7_db_kernel_app_demo.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal462_v0_7_db_kernel_app_demo_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/README.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_462_v0_7_db_kernel_app_demo.md`

## What The Demo Shows

The demo models a small application called
`regional_order_dashboard_kernel_form`.

Input data:

- one denormalized order table owned by the application
- fields: `row_id`, `region`, `channel`, `ship_date`, `discount`, `quantity`,
  `revenue`

Kernel shape:

- `rt.input("predicates", rt.PredicateSet, role="probe")` receives scan
  predicates
- `rt.input("query", rt.GroupedQuery, role="probe")` receives grouped query
  descriptors
- `rt.input("table", rt.DenormTable, role="build")` receives application rows
- `rt.traverse(..., accel="bvh", mode="db_scan")` or
  `rt.traverse(..., accel="bvh", mode="db_group")` discovers encoded row
  candidates
- `rt.refine(...)` applies exact scan, grouped count, or grouped sum semantics
- `rt.emit(...)` returns application JSON rows

Predicate examples:

- one predicate: `discount = 6`
- two predicates: `ship_date between 12 and 15` and `quantity < 20`
- three predicates: `ship_date between 12 and 15`, `discount = 6`, and
  `quantity < 20`

RTDL v0.7 operations:

- `conjunctive_scan`: predicate sets become matched `row_id` records
- `grouped_count`: filtered rows become counts by `region`
- `grouped_sum`: filtered web-channel rows become summed `revenue` by `region`

Execution paths:

- `--backend cpu_python_reference` runs everywhere and documents the semantic
  output
- `--backend auto` tries `embree`, `optix`, `vulkan`, then `cpu`, and falls
  back to CPU Python reference if no native backend runs
- direct `--backend cpu`, `--backend embree`, `--backend optix`, and
  `--backend vulkan` are available when those runtime paths are built

## Local Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal462_v0_7_db_kernel_app_demo_test
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_kernel_app_demo.py --backend cpu_python_reference
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_kernel_app_demo.py --backend auto
```

Results:

- unit test: `OK`
- `--backend cpu_python_reference`: produced valid JSON and expected rows
- `--backend auto`: selected `embree` on this host

Observed app output:

- one-predicate discounted IDs: `3`, `4`, `5`, `7`
- two-predicate campaign-window IDs: `3`, `4`, `5`, `6`, `7`
- three-predicate promo IDs: `3`, `4`, `5`, `7`
- open order counts by region: east `2`, south `1`, west `2`
- web revenue by region: east `180`, west `240`

## Honesty Boundary

This is a kernel-form demo of bounded v0.7 DB workloads. It is not SQL,
joins, transactions, storage, indexing, optimization, or a DBMS.

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal462_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal462-v0_7-db-kernel-app-demo.md`
