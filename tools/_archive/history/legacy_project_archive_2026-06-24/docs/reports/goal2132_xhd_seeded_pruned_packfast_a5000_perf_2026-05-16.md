# Goal2132: RTDL/OptiX X-HD Seeded-Pruned Hausdorff Beats Optimized CuPy

Date: 2026-05-16

Commit: `8bb02b585dcb91c68378fc465b1b9c4850990f13`

Hardware: NVIDIA RTX A5000, driver 570.211.01

## Question

After Goal2129 made the baseline fair, optimized grouped CuPy still beat the earlier RTDL/OptiX grouped nearest-witness path. Goal2132 reruns the full public Stanford projected-XY Hausdorff benchmark after two changes:

- Generic RTDL/OptiX point-group threshold flags, so the app can prune source points that cannot improve the current Hausdorff maximum.
- Vectorized NumPy-owner point packing for `pack_points`, including the OptiX copy, so large Python point columns no longer pay per-row ctypes construction.

## Result

The new RTDL v2 path is exact and matches grouped CuPy on both public cases. Best-vs-best, it outperforms optimized grouped CuPy by about 6x.

| Case | Best grouped CuPy | Best RTDL/OptiX seeded-pruned | RTDL / CuPy | Speedup |
| --- | ---: | ---: | ---: | ---: |
| Stanford Dragon XY shifted | 2.994052 s | 0.491084 s | 0.164x | 6.10x |
| Stanford Dragon vs Happy XY | 3.417380 s | 0.535331 s | 0.157x | 6.38x |

## Full Group Sweep

| Case | Group | Grouped CuPy s | RTDL/OptiX seeded-pruned s | Ratio |
| --- | ---: | ---: | ---: | ---: |
| Dragon shifted | 128 | 2.994052 | 0.616375 | 0.206x |
| Dragon shifted | 256 | 3.343166 | 0.517156 | 0.155x |
| Dragon shifted | 512 | 3.717182 | 0.565748 | 0.152x |
| Dragon shifted | 1024 | 4.008881 | 0.491084 | 0.122x |
| Dragon shifted | 2048 | 4.509305 | 0.532710 | 0.118x |
| Dragon shifted | 4096 | 4.696846 | 0.569456 | 0.121x |
| Dragon vs Happy | 128 | 3.417380 | 0.679905 | 0.199x |
| Dragon vs Happy | 256 | 3.758479 | 0.583227 | 0.155x |
| Dragon vs Happy | 512 | 4.203885 | 0.601304 | 0.143x |
| Dragon vs Happy | 1024 | 4.711412 | 0.549406 | 0.117x |
| Dragon vs Happy | 2048 | 5.140844 | 0.612616 | 0.119x |
| Dragon vs Happy | 4096 | 5.525203 | 0.535331 | 0.097x |

## Why It Wins Now

The X-HD-style pruning was already strong: inspection showed only tens of unsafe points remained out of roughly 438k source points. Before the vectorized packing fix, the runtime was dominated by Python-side conversion of NumPy columns into ctypes point rows. After the fix, the RTDL path spends its time on the actual useful work:

- a sample exact seed,
- RT-core-backed point-group threshold traversal,
- exact max-nearest reduction only for the unsafe subset.

The key lesson is not “hard-code Hausdorff into the engine.” The useful generic primitive is a point-group threshold mask plus exact witness reduction; the Hausdorff policy lives in Python.

## Claim Boundary

| Claim | Verdict |
| --- | --- |
| Exact 2D projected-point Hausdorff for these public datasets | `accept` |
| Uses RTDL/OptiX RT traversal | `accept` |
| Beats optimized grouped CuPy on the measured A5000 public projected-XY benchmark | `accept-with-boundary` |
| Beats all possible CUDA implementations | `not-claimed` |
| Matches X-HD paper datasets and 3D surface setting | `not-claimed` |
| General RT-core speedup for every Hausdorff dataset | `not-claimed` |

Artifacts are in `docs/reports/goal2131_public_pod_a5000_seeded_pruned_sweep_packfast/`.
