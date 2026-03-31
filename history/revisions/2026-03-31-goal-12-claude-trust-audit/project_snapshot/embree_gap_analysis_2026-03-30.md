# Embree Gap Analysis

This report describes what the current Embree evaluation reproduces and what remains deferred to the NVIDIA/OptiX phase.

## What Goal 9 Reproduces

- A frozen workload/dataset evaluation matrix across the current six RTDL workloads.
- Reproducible local benchmark artifacts on top of a real native ray tracing engine (Embree).
- Automatic generation of summary tables and figure files from the benchmark outputs.
- CPU-vs-Embree correctness checks before timing claims for every matrix entry.

## What Goal 9 Does Not Claim

- NVIDIA RT-core execution.
- OptiX/CUDA runtime behavior.
- Final RayJoin paper performance parity or direct reproduction of the paper's hardware results.

## Current Local Limitations

- The local dataset fixtures are tiny public subsets; larger cases are deterministic derived tiles or synthetic generators.
- The current precision mode is still `float_approx` rather than a robust or exact arithmetic implementation.
- The overlay workload is still evaluated as compositional seed generation rather than a full polygon overlay implementation.

## Generated Figures

- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/figures/latency_by_case.svg`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/figures/speedup_by_case.svg`
- `/Users/rl2025/rtdl_python_only/build/embree_evaluation/figures/scaling_by_workload.svg`

- All evaluation cases passed CPU-vs-Embree parity checks.
- Fastest Embree case: overlay_authored_minimal at 0.000123s mean.
- Slowest Embree case: ray_synthetic_large at 0.001822s mean.
- Best Embree speedup vs CPU: ray_synthetic_large at 165.14x.
- lsi largest evaluated local case: lsi_county_tiled_x8 (0.000413s Embree mean).
- pip largest evaluated local case: pip_county_tiled_x8 (0.000450s Embree mean).
- overlay largest evaluated local case: overlay_county_soil_tiled_x8 (0.000614s Embree mean).
- ray_tri_hitcount largest evaluated local case: ray_synthetic_large (0.001822s Embree mean).
