# Goal 1503: OptiX COLLECT_K_BOUNDED Scaling Probe

## Verdict

`goal1503_optix_collect_k_scaling_probe_recorded`

## Scope

- Device: `NVIDIA RTX 4000 Ada Generation`
- Git commit: `0b975f469ccdef52b508866281a21fa569fd29fe`
- Algorithm classification: `correctness_first_single_thread_device_kernel_o_n2_times_row_width`
- Timing scope: Python wrapper call around native OptiX/CUDA device-pointer execution, including launch and metadata copy overhead, excluding input setup H2D and output verification D2H.

## Cases

- candidates=`8`, unique=`4`, row_width=`2`, median_ms=`0.043385`, parity=`True`
- candidates=`32`, unique=`16`, row_width=`2`, median_ms=`0.128239`, parity=`True`
- candidates=`128`, unique=`64`, row_width=`2`, median_ms=`1.419172`, parity=`True`
- candidates=`512`, unique=`256`, row_width=`2`, median_ms=`21.911725`, parity=`True`

## Claim Boundary

Goal1503 records scaling observations for the experimental Python OptiX COLLECT_K_BOUNDED device-pointer bridge only. It is not a speedup claim, does not prove true zero-copy, and does not authorize whole-app claims, partner tensor handoff, stable primitive promotion, or release action.
