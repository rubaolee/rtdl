# Goal 1431 v1.5.1 COLLECT_K_BOUNDED Generic I64 ABI Parity Summary

## Verdict

ACCEPTED for the measured generic i64 ABI parity package.

Embree and OptiX built native generic symbols both passed the same direct ctypes ABI checks for canonical exact-fit collection and fail-closed overflow behavior. This closes generic i64 ABI parity evidence for Goal1431, but it does not authorize stable primitive promotion, speedup wording, zero-copy wording, whole-app behavior, broad workload claims, or release action.

## Evidence

- Linux Embree report: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.md`
- Linux Embree JSON: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.json`
- RTX A5000 pod OptiX report: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.md`
- RTX A5000 pod OptiX JSON: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.json`
- OptiX rebuild transcript: `docs/reports/goal1431_v1_5_1_collect_k_rebuild_optix_2026-05-06.txt`

## Run Scope

- Primitive: `COLLECT_K_BOUNDED`
- ABI symbols: `rtdl_embree_collect_k_bounded_i64`, `rtdl_optix_collect_k_bounded_i64`
- Row layout: row-major `int64_t` candidate rows
- Row width: `2`
- Exact-fit case: deduplicate `((2, 20), (1, 10), (2, 20))` into canonical rows `[1, 10, 2, 20]`
- Overflow case: capacity `1` reports `emitted=2`, `overflowed=1`, and leaves no partial output rows
- Git HEAD for both measured runs: `610e81a776079803e95030d661d28cc6bd995aa5`

## Parity Outcome

- Embree: ACCEPTED, both cases passed.
- OptiX: ACCEPTED, both cases passed on the NVIDIA RTX A5000 pod.
- Cross-backend outcome: ACCEPTED for the measured generic i64 ABI parity package.

## Claim Boundary

This artifact is generic i64 ABI parity evidence only. Stable `COLLECT_K_BOUNDED` primitive wording remains blocked until the separate stable-promotion review is completed with the required external AI consensus.
