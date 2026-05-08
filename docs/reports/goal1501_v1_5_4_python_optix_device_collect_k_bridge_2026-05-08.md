# Goal 1501: Python OptiX Device COLLECT_K_BOUNDED Bridge

## Verdict

`goal1501_python_optix_device_collect_k_bridge_validated`

## Scope

- Python entry point: `rtdsl.optix_runtime.collect_k_bounded_i64_device_optix`
- Native symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Required opt-in: `allow_experimental=True`
- Default behavior: refuses without explicit opt-in
- Pod: `root@213.173.108.6 -p 17339`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Native evidence commit: `6f953c4434147abd29b9c88dda1f72f14b23b233`

## Result

The Python wrapper was run against real CUDA device pointers with input rows `[(2, 20), (1, 10), (2, 20), (3, 30)]`. It returned `valid_count=3`, `overflowed=False`, and the output device buffer copied back for verification as `[(1, 10), (2, 20), (3, 30)]`.

## Transfer Accounting

- H2D transfers before backend execution reported by backend: `0`
- D2H metadata transfers after backend execution reported by backend: `2`
- Internal device transfers reported by backend: `0`

## Claim Boundary

Goal1501 validates the Python opt-in wrapper for the measured OptiX `COLLECT_K_BOUNDED` device-pointer symbol only. It does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
