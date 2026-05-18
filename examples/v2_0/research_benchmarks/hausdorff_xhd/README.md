# Hausdorff / X-HD Study

This directory contains the RTDL v2.0 Hausdorff application and benchmark
harnesses used for X-HD-inspired experiments.

| File | Purpose |
| --- | --- |
| `rtdl_hausdorff_distance_app.py` | release-facing Hausdorff-style nearest-neighbor composition |
| `rtdl_hausdorff_v2_function.py` | serious RTDL/CuPy/CUDA/OpenMP comparison entry point |
| `rtdl_hausdorff_v2_language_lab.py` | method sweep and language-lab harness |
| `rtdl_hausdorff_v2_user_benchmark.py` | user-level benchmark helpers |

Boundary: this is a serious performance study, not a universal claim that RTDL
beats every exact Hausdorff implementation on every dataset.
