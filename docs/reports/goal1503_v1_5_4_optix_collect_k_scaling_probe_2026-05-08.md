# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe

## Verdict

`goal1503_optix_collect_k_scaling_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `9192e4cf5990b41012e3088fb270dfd9aa14fe9b`
- Algorithm classification: `row_width2_parallel_bitonic_sort_with_bounded_multi_tile_merge_and_dynamic_row_width_o_n2_fallback`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, including launch and metadata copy overhead, excluding input setup H2D and output verification D2H.

## Cases

- candidates=`8`, unique=`4`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.039615`, parity=`True`
- candidates=`32`, unique=`16`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.046849`, parity=`True`
- candidates=`128`, unique=`64`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.066705`, parity=`True`
- candidates=`512`, unique=`256`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.143528`, parity=`True`
- candidates=`1024`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.250265`, parity=`True`
- candidates=`1025`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.268094`, parity=`True`
- candidates=`2048`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.465691`, parity=`True`
- candidates=`2049`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.503257`, parity=`True`
- candidates=`4096`, unique=`2048`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.903852`, parity=`True`
- candidates=`4097`, unique=`2048`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`1.651607`, parity=`True`
- candidates=`8192`, unique=`4096`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`3.482476`, parity=`True`
- candidates=`8193`, unique=`4096`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`4.259072`, parity=`True`
- candidates=`16384`, unique=`8192`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`11.404902`, parity=`True`
- candidates=`16385`, unique=`8192`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`13.177320`, parity=`True`
- candidates=`32768`, unique=`16384`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`29.719800`, parity=`True`
- candidates=`32769`, unique=`16384`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`33.005632`, parity=`True`
- candidates=`65536`, unique=`32768`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`77.006049`, parity=`True`

## Claim Boundary

Goal1503 records scaling observations for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, does not prove true zero-copy, and does not authorize whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
