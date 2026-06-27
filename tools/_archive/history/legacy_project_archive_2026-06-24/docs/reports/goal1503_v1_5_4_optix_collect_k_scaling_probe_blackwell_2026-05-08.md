# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe

## Verdict

`goal1503_optix_collect_k_scaling_probe_recorded`

## Scope

- Device: `NVIDIA RTX PRO 4500 Blackwell`
- Git commit: `fd33cad297acaadcb90efd79e240308a81798918`
- Algorithm classification: `row_width2_parallel_bitonic_sort_with_bounded_multi_tile_merge_and_dynamic_row_width_o_n2_fallback`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, including launch and metadata copy overhead, excluding input setup H2D and output verification D2H.

## Cases

- candidates=`4097`, unique=`2048`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`1.537815`, parity=`True`
- candidates=`65537`, unique=`32768`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`80.058882`, parity=`True`
- candidates=`131072`, unique=`65536`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`181.992388`, parity=`True`

## Claim Boundary

Goal1503 records scaling observations for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, does not prove true zero-copy, and does not authorize whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
