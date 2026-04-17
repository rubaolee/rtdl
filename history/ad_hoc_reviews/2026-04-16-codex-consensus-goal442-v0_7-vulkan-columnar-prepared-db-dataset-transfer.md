# Codex Consensus: Goal 442 v0.7 Vulkan Columnar Prepared DB Dataset Transfer

Date: 2026-04-16

## Verdict

ACCEPT.

Goal 442 has the required 2-AI consensus:

- Codex review: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_review_2026-04-16.md`
- Claude external review: `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal442_external_review_2026-04-16.md`

## Basis

The Vulkan backend now has an additive native columnar prepared DB dataset
transfer ABI:

- `RtdlDbColumn`
- `rtdl_vulkan_db_dataset_create_columnar`

The Python public API exposes it through:

- `prepare_vulkan_db_dataset(..., transfer="columnar")`

The default remains `transfer="row"`.

Correctness passed on Linux after rebuilding the Vulkan backend for:

- `conjunctive_scan`
- `grouped_count`
- `grouped_sum`

The Linux 200k-row prepare-time gate shows columnar transfer improving Vulkan
prepare time by about 3.08x to 3.36x over the row-struct transfer path.

## Boundary

This consensus closes Vulkan columnar transfer. Together with Goals 440 and
441, all three RT backends now have columnar prepared DB dataset transfer paths.
RTDL remains a bounded workload-kernel/runtime system, not a DBMS or arbitrary
SQL engine.
