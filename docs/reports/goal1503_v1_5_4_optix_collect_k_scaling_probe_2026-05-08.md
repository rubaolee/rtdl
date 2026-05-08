# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe

## Verdict

`goal1503_optix_collect_k_scaling_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `6619153f1a12e6c8755594848443829e3ba20462`
- Algorithm classification: `row_width2_parallel_bitonic_sort_with_bounded_multi_tile_merge_and_dynamic_row_width_o_n2_fallback`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, including launch and metadata copy overhead, excluding input setup H2D and output verification D2H.

## Cases

- candidates=`8`, unique=`4`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.040270`, parity=`True`
- candidates=`32`, unique=`16`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.046887`, parity=`True`
- candidates=`128`, unique=`64`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.066623`, parity=`True`
- candidates=`512`, unique=`256`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.143811`, parity=`True`
- candidates=`1024`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.250041`, parity=`True`
- candidates=`1025`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.267133`, parity=`True`
- candidates=`2048`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.466704`, parity=`True`
- candidates=`2049`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.504047`, parity=`True`
- candidates=`4096`, unique=`2048`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.904925`, parity=`True`
- candidates=`4097`, unique=`2048`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`1.279891`, parity=`True`
- candidates=`8192`, unique=`4096`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`3.124438`, parity=`True`
- candidates=`8193`, unique=`4096`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`3.887489`, parity=`True`
- candidates=`16384`, unique=`8192`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`11.035919`, parity=`True`
- candidates=`16385`, unique=`8192`, row_width=`2`, path=`dynamic_row_width_single_thread_fallback`, median_ms=`28601.952620`, parity=`True`

## Claim Boundary

Goal1503 records scaling observations for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, does not prove true zero-copy, and does not authorize whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
