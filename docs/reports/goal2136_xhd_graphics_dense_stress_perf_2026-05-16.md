# Goal2136: Million-Point X-HD Graphics Stress Sweep

Date: 2026-05-16

Harness commit recorded in artifacts: `02ee6ab5a7b8e1a78b961772a8eabb27aa1aa052`

Pod: `root@69.30.85.189 -p 22108`, NVIDIA RTX A5000, driver 570.211.01

## Question

Goal2134 showed that RTDL/OptiX seeded-pruned exact 2D projected-point Hausdorff beats grouped CuPy on the X-HD graphics model names at 262k and 524k requested scales. Goal2136 asks whether that advantage survives a denser stress run with 1,048,576 requested samples and larger grouped-CuPy tile sizes.

The same claim boundary applies: these are public Stanford PLY model names used by the X-HD graphics scripts, projected to XY. This is not a full 3D surface Hausdorff reproduction of the X-HD paper.

## Stress Results

All rows matched grouped CuPy distance within the harness tolerance.

| Effective points | Group | Case | Grouped CuPy s | RTDL/OptiX s | RTDL / CuPy | Speedup |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 437,645 | 4096 | Dragon vs Asian Dragon | 7.803855 | 0.944555 | 0.121x | 8.26x |
| 1,048,576 | 4096 | Thai Statuette vs Happy Buddha | 10.960250 | 0.910133 | 0.083x | 12.04x |
| 437,645 | 4096 | Dragon vs Happy Buddha | 5.769692 | 0.583008 | 0.101x | 9.90x |
| 1,048,576 | 4096 | Thai Statuette vs Asian Dragon | 15.281775 | 1.278425 | 0.084x | 11.95x |
| 437,645 | 8192 | Dragon vs Asian Dragon | 8.910846 | 0.991564 | 0.111x | 8.99x |
| 1,048,576 | 8192 | Thai Statuette vs Happy Buddha | 12.072404 | 0.920446 | 0.076x | 13.12x |
| 437,645 | 8192 | Dragon vs Happy Buddha | 6.245333 | 0.621460 | 0.100x | 10.05x |
| 1,048,576 | 8192 | Thai Statuette vs Asian Dragon | 17.380398 | 1.248008 | 0.072x | 13.93x |

## Interpretation

The denser rows strengthen the Goal2134 trend. Grouped CuPy slows sharply as the model sample size and group size grow, while the RTDL/OptiX seeded-pruned path stays near one second for the million-point dense rows.

The important technical reading is still app-agnostic:

- The native work is generic point-group threshold traversal and nearest-witness reduction.
- X-HD-style seed/prune policy lives in Python.
- No Hausdorff-specific native entry point was added.
- The result suggests that the generic RT traversal primitive becomes more valuable as the candidate set grows.

## Claim Boundary

| Claim | Verdict |
| --- | --- |
| Million-requested-sample stress evidence for X-HD graphics model names | `accept` |
| Exact 2D projected-point Hausdorff against grouped CuPy for these artifacts | `accept` |
| RTDL/OptiX beats grouped CuPy on the measured RTX A5000 projected-XY stress rows | `accept-with-boundary` |
| Full 3D surface Hausdorff reproduction of X-HD | `not-claimed` |
| MRI or geo WKT reproduction | `not-claimed` |
| Universal CUDA-vs-RT speedup | `not-claimed` |
| v2.0 release authorization | `not-authorized-here` |

Artifacts are in `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/`.
