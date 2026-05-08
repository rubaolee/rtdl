# Goal 1504: OptiX COLLECT_K_BOUNDED Tiled Overflow Probe

## Verdict

`goal1504_optix_collect_k_tiled_overflow_probe_recorded`

## Scope

- Device: `NVIDIA RTX PRO 4500 Blackwell`
- Git commit: `fd33cad297acaadcb90efd79e240308a81798918`
- Python entry point: `rtdsl.optix_runtime.collect_k_bounded_i64_device_optix`
- Native symbol: `rtdl_optix_collect_k_bounded_i64_device`

## Cases

- candidates=`4097`, unique=`2048`, capacity=`2047`, path=`row_width2_bounded_multi_tile_sort_merge`, valid_count=`2048`, overflowed=`True`, fail_closed_output_preserved=`True`
- candidates=`65537`, unique=`32768`, capacity=`32767`, path=`row_width2_bounded_multi_tile_sort_merge`, valid_count=`32768`, overflowed=`True`, fail_closed_output_preserved=`True`
- candidates=`131072`, unique=`65536`, capacity=`65535`, path=`row_width2_bounded_multi_tile_sort_merge`, valid_count=`65536`, overflowed=`True`, fail_closed_output_preserved=`True`

## Claim Boundary

Goal1504 records overflow/fail-closed behavior for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It does not authorize true zero-copy wording, public speedup wording, whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
