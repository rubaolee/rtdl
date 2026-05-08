# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe

## Verdict

`goal1503_optix_collect_k_scaling_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `efa93835baa4a8d706d8b369408768d8789faf42`
- Algorithm classification: `row_width2_parallel_bitonic_sort_single_thread_compaction_with_dynamic_row_width_o_n2_fallback`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, including launch and metadata copy overhead, excluding input setup H2D and output verification D2H.

## Cases

- candidates=`8`, unique=`4`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.038892`, parity=`True`
- candidates=`32`, unique=`16`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.049390`, parity=`True`
- candidates=`128`, unique=`64`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.066184`, parity=`True`
- candidates=`512`, unique=`256`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.143491`, parity=`True`
- candidates=`1024`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.249051`, parity=`True`
- candidates=`1025`, unique=`512`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.266112`, parity=`True`
- candidates=`2048`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.464499`, parity=`True`
- candidates=`2049`, unique=`1024`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.501886`, parity=`True`
- candidates=`4096`, unique=`2048`, row_width=`2`, path=`row_width2_parallel_bitonic_sort`, median_ms=`0.900216`, parity=`True`
- candidates=`4097`, unique=`2048`, row_width=`2`, path=`dynamic_row_width_single_thread_fallback`, median_ms=`1293.445349`, parity=`True`

## Claim Boundary

Goal1503 records scaling observations for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, does not prove true zero-copy, and does not authorize whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
