# Goal 1502: Python OptiX COLLECT_K_BOUNDED Bounds Probe

## Verdict

`goal1502_python_optix_collect_k_bounds_probe_passed`

## Scope

- Python entry point: `rtdsl.optix_runtime.collect_k_bounded_i64_device_optix`
- Native symbol: `rtdl_optix_collect_k_bounded_i64_device`
- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `4bf53d111faa691fcaf8896cc2bdb822a47bdcfd`

## Bounds

- Overflow valid count: `3`
- Overflow flag: `True`
- Output sentinel preserved on overflow: `True`
- Unsupported row_width refused: `True`

## Claim Boundary

Goal1502 validates bounds behavior for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
