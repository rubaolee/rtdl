# Goal 464: Codex Review of v0.7 Linux Fresh-Checkout Validation

Date: 2026-04-16
Reviewer: Codex
Verdict: ACCEPT

## Scope Reviewed

Reviewed:

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/goal_464_v0_7_linux_fresh_checkout_validation.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_v0_7_linux_fresh_checkout_validation_2026-04-16.md`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_columnar_repeated_query_perf_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_postgresql_index_audit_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_rtdl_vs_postgresql_rebase_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_app_demo_output_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal464_linux_fresh_kernel_demo_output_2026-04-16.json`

## Findings

No blocking issues found.

The validation follows the fresh-checkout rule: OptiX and Vulkan were missing
before build, then available after `make build-optix` and `make build-vulkan`.
Embree was available immediately through the system runtime.

The test evidence covers both public examples and PostgreSQL-backed correctness:
13 focused DB tests passed with 2 expected skips, and 29 prepared-dataset /
columnar-transfer tests passed.

The performance evidence is honest about the comparison boundary. The fresh
RTDL columnar timing compares against PostgreSQL setup plus repeated-query time,
while the rebase artifact separately reports speedups against best tested
PostgreSQL query modes. All reported RTDL/PostgreSQL hashes match.

The report correctly states the GTX 1070 caveat: this Linux machine validates
native backend functionality and performance but cannot prove RT-core hardware
speedup because the GPU has no RT cores.

## Verdict

ACCEPT. Goal 464 is a valid Linux fresh-checkout validation of the current v0.7
DB package and does not authorize staging or release movement.
