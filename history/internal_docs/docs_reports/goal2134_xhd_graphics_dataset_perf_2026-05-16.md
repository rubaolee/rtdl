# Goal2134: X-HD Graphics Dataset Names for RTDL/OptiX Hausdorff Performance

Date: 2026-05-16

Harness commit: `02ee6ab5a7b8e1a78b961772a8eabb27aa1aa052`

Pod: `root@69.30.85.189 -p 22108`, NVIDIA RTX A5000, driver 570.211.01

## Question

Goal2132 proved the new X-HD-style seeded-pruned RTDL/OptiX Hausdorff path on two public Stanford projected-XY cases. This follow-up asks whether the same result survives on the graphics dataset names used by the X-HD scripts:

- `dragon.ply` vs `asian_dragon.ply`
- `thai_statuette.ply` vs `happy_buddha.ply`
- `dragon.ply` vs `happy_buddha.ply`
- `thai_statuette.ply` vs `asian_dragon.ply`

The harness downloads the public Stanford 3D Scanning Repository models and projects vertices to XY. This is intentionally not a full 3D surface Hausdorff claim and not a reproduction of the X-HD paper's full input contract.

## Dataset Coverage

| Case | Class | Source models | Effective points at large scale |
| --- | --- | --- | ---: |
| `xhd_graphics_dragon_vs_asian_dragon_xy` | mixed-density | Dragon reconstruction; XYZ RGB Asian Dragon | 437,645 |
| `xhd_graphics_thai_statuette_vs_happy_buddha_xy` | dense-to-medium | XYZ RGB Thai Statuette; Happy Buddha reconstruction | 524,288 |
| `xhd_graphics_dragon_vs_happy_buddha_xy` | medium | Dragon reconstruction; Happy Buddha reconstruction | 437,645 |
| `xhd_graphics_thai_statuette_vs_asian_dragon_xy` | dense | XYZ RGB Thai Statuette; XYZ RGB Asian Dragon | 524,288 |

Dragon's reconstruction contains fewer than the requested 524,288 sampled points, so the large run uses all 437,645 loaded Dragon vertices after XY projection.

## Best-Vs-Best Results

Each row compares the best grouped CuPy time among groups 1024/2048/4096 against the best RTDL/OptiX seeded-pruned time among the same groups. All rows match the grouped CuPy distance within the harness tolerance.

| Scale | Case | Best grouped CuPy | Best RTDL/OptiX seeded-pruned | RTDL / CuPy | Speedup |
| ---: | --- | ---: | ---: | ---: | ---: |
| 262,144 | Dragon vs Asian Dragon | 1.315148 s | 0.319025 s | 0.243x | 4.12x |
| 262,144 | Thai Statuette vs Happy Buddha | 1.506425 s | 0.272750 s | 0.181x | 5.52x |
| 262,144 | Dragon vs Happy Buddha | 1.707804 s | 0.292145 s | 0.171x | 5.85x |
| 262,144 | Thai Statuette vs Asian Dragon | 1.218790 s | 0.298525 s | 0.245x | 4.08x |
| 437,645 | Dragon vs Asian Dragon | 3.407770 s | 0.524885 s | 0.154x | 6.49x |
| 524,288 | Thai Statuette vs Happy Buddha | 4.486585 s | 0.615363 s | 0.137x | 7.29x |
| 437,645 | Dragon vs Happy Buddha | 4.657096 s | 0.537615 s | 0.115x | 8.66x |
| 524,288 | Thai Statuette vs Asian Dragon | 3.549162 s | 0.565921 s | 0.159x | 6.27x |

## Full Group Sweep

| Scale | Group | Case | Grouped CuPy s | RTDL/OptiX s | Ratio |
| ---: | ---: | --- | ---: | ---: | ---: |
| 262,144 | 1024 | Dragon vs Asian Dragon | 1.315148 | 0.329742 | 0.251x |
| 262,144 | 1024 | Thai Statuette vs Happy Buddha | 1.506425 | 0.312839 | 0.208x |
| 262,144 | 1024 | Dragon vs Happy Buddha | 1.707804 | 0.292145 | 0.171x |
| 262,144 | 1024 | Thai Statuette vs Asian Dragon | 1.218790 | 0.298525 | 0.245x |
| 262,144 | 2048 | Dragon vs Asian Dragon | 1.401942 | 0.330534 | 0.236x |
| 262,144 | 2048 | Thai Statuette vs Happy Buddha | 1.675640 | 0.272750 | 0.163x |
| 262,144 | 2048 | Dragon vs Happy Buddha | 1.814607 | 0.325844 | 0.180x |
| 262,144 | 2048 | Thai Statuette vs Asian Dragon | 1.398907 | 0.314267 | 0.225x |
| 262,144 | 4096 | Dragon vs Asian Dragon | 1.562430 | 0.319025 | 0.204x |
| 262,144 | 4096 | Thai Statuette vs Happy Buddha | 1.873641 | 0.287728 | 0.154x |
| 262,144 | 4096 | Dragon vs Happy Buddha | 2.033004 | 0.322538 | 0.159x |
| 262,144 | 4096 | Thai Statuette vs Asian Dragon | 1.581032 | 0.308548 | 0.195x |
| 437,645 | 1024 | Dragon vs Asian Dragon | 3.407770 | 0.536642 | 0.157x |
| 524,288 | 1024 | Thai Statuette vs Happy Buddha | 4.486585 | 0.627338 | 0.140x |
| 437,645 | 1024 | Dragon vs Happy Buddha | 4.657096 | 0.537615 | 0.115x |
| 524,288 | 1024 | Thai Statuette vs Asian Dragon | 3.549162 | 0.579954 | 0.163x |
| 437,645 | 2048 | Dragon vs Asian Dragon | 3.868674 | 0.524885 | 0.136x |
| 524,288 | 2048 | Thai Statuette vs Happy Buddha | 5.305179 | 0.615363 | 0.116x |
| 437,645 | 2048 | Dragon vs Happy Buddha | 5.191756 | 0.606730 | 0.117x |
| 524,288 | 2048 | Thai Statuette vs Asian Dragon | 4.237808 | 0.573314 | 0.135x |
| 437,645 | 4096 | Dragon vs Asian Dragon | 4.283269 | 0.552756 | 0.129x |
| 524,288 | 4096 | Thai Statuette vs Happy Buddha | 5.903337 | 0.659657 | 0.112x |
| 437,645 | 4096 | Dragon vs Happy Buddha | 5.592102 | 0.591490 | 0.106x |
| 524,288 | 4096 | Thai Statuette vs Asian Dragon | 4.680404 | 0.565921 | 0.121x |

## Interpretation

The X-HD-style seeded lower bound plus RTDL/OptiX threshold pruning keeps scaling: grouped CuPy becomes slower as group size and model scale grow, while the RTDL path stays near 0.3 seconds at 262k and 0.52-0.66 seconds at the larger scale.

The strongest lesson is still generic:

- The engine primitive is a generic point-group threshold flag plus generic nearest-witness reduction.
- The Hausdorff policy, source sampling, direction selection, and claim boundary remain in Python.
- The speedup appears on mixed-density and dense public model pairs, not only the earlier Dragon/Happy control pair.

## Claim Boundary

| Claim | Verdict |
| --- | --- |
| Uses the same public graphics model names as the X-HD scripts | `accept` |
| Exact 2D projected-point Hausdorff against grouped CuPy for these artifacts | `accept` |
| RTDL/OptiX beats grouped CuPy on the measured RTX A5000 projected-XY rows | `accept-with-boundary` |
| Full 3D surface Hausdorff reproduction of the X-HD paper | `not-claimed` |
| MRI or geo WKT X-HD dataset reproduction | `not-claimed` |
| Universal CUDA-vs-RT speedup for all Hausdorff datasets | `not-claimed` |
| v2.0 public release speedup authorization | `not-authorized-here` |

Artifacts are in `docs/reports/goal2134_xhd_graphics_pod_a5000/`.
