# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe

## Verdict

`goal1503_optix_collect_k_scaling_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `4330892bc8a6d4ddd69cdd04277d25e029f3e738`
- Algorithm classification: `row_width2_parallel_bitonic_sort_with_bounded_multi_tile_merge_and_dynamic_row_width_o_n2_fallback`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, including launch and metadata copy overhead, excluding input setup H2D and output verification D2H.

## Cases

- candidates=`8`, unique=`4`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.039510`, parity=`True`
- candidates=`32`, unique=`16`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.045612`, parity=`True`
- candidates=`128`, unique=`64`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.068277`, parity=`True`
- candidates=`512`, unique=`256`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.143021`, parity=`True`
- candidates=`1024`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.249527`, parity=`True`
- candidates=`1025`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.268072`, parity=`True`
- candidates=`2048`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.465825`, parity=`True`
- candidates=`2049`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.504062`, parity=`True`
- candidates=`4096`, unique=`2048`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.904471`, parity=`True`
- candidates=`4097`, unique=`2048`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`1.948386`, parity=`True`
- candidates=`8192`, unique=`4096`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`3.786936`, parity=`True`
- candidates=`8193`, unique=`4096`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`4.566930`, parity=`True`
- candidates=`16384`, unique=`8192`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`11.706389`, parity=`True`
- candidates=`16385`, unique=`8192`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`12.578249`, parity=`True`
- candidates=`32768`, unique=`16384`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`30.028693`, parity=`True`
- candidates=`32769`, unique=`16384`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`33.379525`, parity=`True`
- candidates=`65536`, unique=`32768`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`77.340215`, parity=`True`
- candidates=`65537`, unique=`32768`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`83.907761`, parity=`True`
- candidates=`131072`, unique=`65536`, row_width=`2`, path=`row_width2_bounded_multi_tile_sort_merge`, median_ms=`189.929321`, parity=`True`

## Claim Boundary

Goal1503 records scaling observations for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, does not prove true zero-copy, and does not authorize whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
