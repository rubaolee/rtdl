# Goal 1502: Python OptiX COLLECT_K_BOUNDED Bounds Probe

## Verdict

`goal1502_python_optix_collect_k_bounds_and_dynamic_width_probe_passed`

## Scope

- Python entry point: `rtdsl.optix_runtime.collect_k_bounded_i64_device_optix`
- Native symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `b42ac66332355fc6f3b3e5e957f65a9d8597c54a`

## Bounds

- Overflow valid count: `3`
- Overflow flag: `True`
- Output sentinel preserved on overflow: `True`
- Dynamic row_width=3 row parity: `True`
- Dynamic row_width=3 valid count parity: `True`
- Dynamic row_width=3 overflow parity: `True`
- INT64_MAX pair row parity: `True`
- INT64_MAX pair valid count parity: `True`
- INT64_MAX pair overflow parity: `True`

## Claim Boundary

Goal1502 validates bounds behavior and dynamic row-width behavior for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
