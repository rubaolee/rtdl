# Goal 1431 External Review Request: v1.5.1 COLLECT_K_BOUNDED Generic I64 ABI Parity

Please review the Goal1431 evidence package for RTDL v1.5.1 `COLLECT_K_BOUNDED`.

## Question

Can we accept this as measured generic i64 ABI parity evidence for the Embree and OptiX native generic symbols, while still blocking stable primitive promotion, speedup wording, zero-copy wording, whole-app behavior, broad workload claims, and release action?

## Files To Review

- Contract: `src/rtdsl/v1_5_1_collect_k_bounded.py`
- Runner: `scripts/goal1431_v1_5_1_collect_k_generic_i64_abi_parity.py`
- Summary: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_2026-05-06.md`
- Linux Embree report: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.md`
- Linux Embree JSON: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_linux_embree_2026-05-06.json`
- RTX A5000 pod OptiX report: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.md`
- RTX A5000 pod OptiX JSON: `docs/reports/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_pod_optix_2026-05-06.json`
- OptiX rebuild transcript: `docs/reports/goal1431_v1_5_1_collect_k_rebuild_optix_2026-05-06.txt`
- Tests: `tests/goal1431_v1_5_1_collect_k_generic_i64_abi_parity_test.py`

## Measured Scope

- Primitive: `COLLECT_K_BOUNDED`
- ABI symbols: `rtdl_embree_collect_k_bounded_i64`, `rtdl_optix_collect_k_bounded_i64`
- Row layout: row-major `int64_t` candidate rows
- Row width: `2`
- Exact-fit case: deduplicate `((2, 20), (1, 10), (2, 20))` into canonical rows `[1, 10, 2, 20]`
- Overflow case: capacity `1` reports `emitted=2`, `overflowed=1`, and leaves no partial output rows
- Git HEAD for both measured runs: `610e81a776079803e95030d661d28cc6bd995aa5`

## Local Validation

- Windows focused slice: `Ran 40 tests OK`
- Linux focused slice: `Ran 40 tests OK`

## Claim Boundary To Check

This package should be accepted only as generic i64 ABI parity evidence. It must not be treated as stable `COLLECT_K_BOUNDED` promotion, performance evidence, zero-copy evidence, whole-app behavior evidence, broad workload evidence, or a release action.
