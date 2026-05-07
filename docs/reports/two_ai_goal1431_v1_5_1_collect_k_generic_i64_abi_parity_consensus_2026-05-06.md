# 2-AI Consensus: Goal1431 v1.5.1 COLLECT_K_BOUNDED Generic I64 ABI Parity

## Verdict

ACCEPTED as measured generic i64 ABI parity evidence for the Embree and OptiX native generic symbols.

This is not a stable primitive promotion, speedup claim, zero-copy claim, whole-app claim, broad workload claim, release action, or public release-surface expansion.

## Consensus Basis

- Codex implementation and audit: accepted after Windows and Linux focused validation both reported `Ran 40 tests OK`.
- Gemini external review: accepted in `docs/reports/gemini_goal1431_v1_5_1_collect_k_generic_i64_abi_parity_review_2026-05-06.md`.
- Claude external review: attempted but unavailable because of quota, recorded in `docs/reports/claude_goal1431_v1_5_1_collect_k_generic_i64_abi_parity_unavailable_2026-05-06.md`.

## Evidence Package

- Summary: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_2026-05-06.md`
- Linux Embree report: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.md`
- RTX A5000 pod OptiX report: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.md`
- OptiX rebuild transcript: `docs/reports/goal1431_v1_5_1_collect_k_rebuild_optix_2026-05-06.txt`
- Guard test: `tests/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_test.py`

## Claim Boundary

Goal1431 accepts only the measured ABI parity package:

- `rtdl_embree_collect_k_bounded_i64`
- `rtdl_optix_collect_k_bounded_i64`
- row-major `int64_t` rows
- row width `2`
- canonical exact-fit collection
- fail-closed overflow without partial output rows

Stable `COLLECT_K_BOUNDED` promotion remains blocked until the separate stable-promotion review completes with the required external AI consensus.
