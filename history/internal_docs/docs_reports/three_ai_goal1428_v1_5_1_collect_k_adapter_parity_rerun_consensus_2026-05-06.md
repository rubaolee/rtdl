# 3-AI Consensus: Goal 1428 v1.5.1 COLLECT_K_BOUNDED Adapter Parity Rerun

## Verdict

Codex, Claude, and Gemini agree that Goal 1428 accurately records the partial
post-adapter parity rerun state.

Accepted:

- Windows optional parity rerun
- Linux required-Embree parity rerun

Still pending:

- required OptiX post-adapter parity rerun

## Consensus Basis

Codex reran the parity package, wrote the summary, and updated the contract
boundary.

Claude review:

- `docs/reports/claude_goal1428_v1_5_1_collect_k_adapter_parity_rerun_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Gemini review:

- `docs/reports/gemini_goal1428_v1_5_1_collect_k_adapter_parity_rerun_review_2026-05-06.md`
- Verdict: `ACCEPT`
- Blocking issues: none

Summary report:

- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_rerun_2026-05-06.md`

External review request:

- `docs/handoff/goal1428_external_review_request_2026-05-06.md`

## Evidence

Windows optional:

- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_windows_optional_2026-05-06.md`
- Result: accepted
- Embree: pass=4, fail=0, skipped=0
- OptiX: pass=0, fail=0, skipped=4
- OptiX was optional in this run

Linux required-Embree:

- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_embree_2026-05-06.md`
- Result: accepted
- Embree: pass=4, fail=0, skipped=0

Linux required-OptiX:

- `docs/reports/goal1428_v1_5_1_collect_k_adapter_parity_linux_optix_2026-05-06.md`
- Result: not accepted
- Exact blocker: `librtdl_optix not found`

Old NVIDIA pod probe:

- `root@213.173.102.217 -p 25443 -i Z:\rtdl-dev\id_ed25519_rtdl_codex`
- Result: `Connection refused`

## Boundary

This consensus does not authorize stable promotion, built generic i64 symbol
validation, speedup wording, zero-copy wording, whole-app claims, release action,
or broad workload wording.

The next required action is to rerun required OptiX adapter parity on a reachable
OptiX environment with `librtdl_optix` available.
