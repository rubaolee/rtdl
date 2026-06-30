# Goal3153: Compact-Mask Front-Door Block-Size Guard

Date: 2026-06-03

Status: `complete`

## Purpose

Goal3152's Claude review accepted Goal3151 and noted one non-blocking hardening item: the new v2.8 `block_size` pass-through for `compact_mask_i64` did not validate positive values before delegating to the lower Numba primitive.

Goal3153 closes that note in the generic v2.8 front-door layer.

## Change

- Added `_resolve_compact_mask_block_size(block_size)` in `src/rtdsl/v2_8_segmented_typed_stream_adapter.py`.
- Default remains `256` when `block_size is None`.
- Explicit positive values still pass through to `run_numba_compact_mask_i64(...)`.
- `block_size <= 0` now raises `ValueError("block_size must be positive for compact_mask_i64")` before the lower primitive is called.

This is intentionally generic and scoped only to `compact_mask_i64`. It does not change app semantics, benchmark aliases, or partner selection policy.

## Claim Boundary

- `release_authorized: False`
- `public_speedup_claim_authorized: False`
- `rt_core_speedup_claim_authorized: False`
- `true_zero_copy_claim_authorized: False`
- `paper_reproduction_claim_authorized: False`
- `automatic_partner_selection_allowed: False`
- `app_specific_engine_logic_allowed: False`

## Validation

Local validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3153_compact_mask_block_size_guard_test tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test
Ran 43 tests in 1.022s
OK
```

Pod validation:

```text
Pod SSH: ssh root@69.30.85.131 -p 22063 -i id_ed25519_rtdl_codex
GPU: NVIDIA A40
Driver: 570.211.01
Checkout: /root/rtdl_goal3151
Commit: 327ab084c1d389e9c23562200a5fd9b58adc4de7
Command: PYTHONPATH=src:. python3 -m unittest tests.goal3153_compact_mask_block_size_guard_test tests.goal3151_v2_8_benchmark_front_door_adoption_audit_test tests.goal3147_compact_mask_front_door_test tests.goal3111_v2_8_segmented_typed_stream_adapter_test tests.goal2999_triangle_counting_numba_compact_mask_wiring_test tests.goal3002_rayjoin_numba_compact_mask_wiring_test
Ran 43 tests in 0.502s
OK
```
