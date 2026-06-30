# Goal 461: v0.7 DB App Demo

Date: 2026-04-16
Author: Codex
Status: Accepted with 2-AI consensus

## Verdict

The v0.7 DB app demo has been added and locally verified.

## Files Added Or Updated

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/rtdl_v0_7_db_app_demo.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal461_v0_7_db_app_demo_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/examples/README.md`

## What The Demo Shows

The demo models a small application called `regional_order_dashboard`.

Input data:

- one denormalized order table owned by the application
- fields: `row_id`, `region`, `channel`, `ship_date`, `discount`, `quantity`,
  `revenue`

RTDL v0.7 operations:

- `conjunctive_scan`: campaign-window discounted small orders become matched
  `row_id` records
- `grouped_count`: small post-window orders become counts by `region`
- `grouped_sum`: web-channel revenue becomes summed revenue by `region`

Execution paths:

- `--backend cpu_reference` runs everywhere and documents the semantic output
- `--backend auto` tries prepared Embree, OptiX, and Vulkan datasets, then
  falls back to CPU reference
- direct `--backend embree`, `--backend optix`, and `--backend vulkan` are
  available when those backend libraries are built

The prepared RT path uses:

- `prepare_embree_db_dataset(..., transfer="columnar")`
- `prepare_optix_db_dataset(..., transfer="columnar")`
- `prepare_vulkan_db_dataset(..., transfer="columnar")`

## Local Verification

Commands run:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal461_v0_7_db_app_demo_test
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_app_demo.py --backend cpu_reference
PYTHONPATH=src:. python3 examples/rtdl_v0_7_db_app_demo.py --backend auto
```

Results:

- unit test: `OK`
- `--backend cpu_reference`: produced expected application JSON rows
- `--backend auto`: selected `embree` on this host
- prepared dataset summary for `--backend auto`: `{"row_count": 7, "transfer": "columnar"}`

Observed app output:

- promo order IDs: `3`, `4`, `5`, `7`
- open order counts by region: east `2`, south `1`, west `2`
- web revenue by region: east `180`, west `240`

## Honesty Boundary

This is a demo of bounded v0.7 DB kernels. It is not a SQL engine, optimizer,
transaction system, storage engine, or DBMS.

## External Review

External review:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal461_external_review_2026-04-16.md`

Verdict: ACCEPT.

Consensus record:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/history/ad_hoc_reviews/2026-04-16-codex-consensus-goal461-v0_7-db-app-demo.md`
