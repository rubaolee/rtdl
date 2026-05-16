# Goal2129 Fair Public Hausdorff A5000 Perf

Date: 2026-05-16

Status: fair baseline implemented and measured on RTX A5000.

## Purpose

The earlier public Stanford Hausdorff runs compared RTDL/OptiX grouped-reduced nearest witness against dense CuPy all-pairs. That answered whether RTDL/OptiX can beat brute-force CUDA, but it did not isolate RT traversal value because CuPy did not receive the same spatial pruning idea.

Goal2129 adds a fairer CuPy baseline:

- `cupy_rawkernel`: dense exact all-pairs CUDA baseline.
- `cupy_grouped_grid_rawkernel`: exact CUDA RawKernel baseline that uses the same uniform target grouping and group-AABB lower-bound pruning idea, but no OptiX and no RT cores.
- `rtdl_rt_grouped_reduced_nearest_witness`: RTDL/OptiX grouped target bounds, OptiX traversal, per-group point scanning, and device-side max-nearest reduction.

The corrected pod run excludes warmup from the measured wall-clock fields for all three paths. Older warmup-included Goal2129 scratch artifacts are superseded by `goal2129_public_pod_a5000_steady`.

## Boundary

This is exact 2D point-set Hausdorff on deterministic XY projections of public Stanford Dragon / Happy Buddha PLY vertices.

It is not:

- exact X-HD paper dataset reproduction;
- 3D mesh/surface Hausdorff;
- a release-wide speedup claim;
- proof that RTDL beats all optimized CUDA implementations.

## A5000 Steady-State Results

GPU: `NVIDIA RTX A5000, 570.211.01`

Commit: `934f252dc35cb6c44ba64752c30d025496630ccd`

Lower `RTDL / grouped CuPy` is better for RTDL.

| case | actual n | dense CuPy sec | grouped CuPy sec | RTDL/OptiX sec | RTDL / dense CuPy | RTDL / grouped CuPy | parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Dragon shifted | 8,192 | 0.009614 | 0.021202 | 0.053130 | 5.526x | 2.506x | pass |
| Dragon vs Happy | 8,192 | 0.009292 | 0.014934 | 0.066208 | 7.125x | 4.433x | pass |
| Dragon shifted | 32,768 | 0.066018 | 0.055247 | 0.254037 | 3.848x | 4.598x | pass |
| Dragon vs Happy | 32,768 | 0.060969 | 0.058824 | 0.239280 | 3.925x | 4.068x | pass |
| Dragon shifted | 65,536 | 0.240427 | 0.152544 | 0.579697 | 2.411x | 3.800x | pass |
| Dragon vs Happy | 65,536 | 0.240407 | 0.161012 | 0.549036 | 2.284x | 3.410x | pass |
| Dragon shifted | 131,072 | 0.961751 | 0.499676 | 1.256957 | 1.307x | 2.516x | pass |
| Dragon vs Happy | 131,072 | 0.959780 | 0.512445 | 1.124552 | 1.172x | 2.194x | pass |
| Dragon shifted | 262,144 | 3.859139 | 1.672024 | 2.612294 | 0.677x | 1.562x | pass |
| Dragon vs Happy | 262,144 | 3.892083 | 1.681716 | 2.207206 | 0.567x | 1.312x | pass |
| Dragon shifted | 437,645 | 10.954933 | 4.353292 | 5.259039 | 0.480x | 1.208x | pass |
| Dragon vs Happy | 437,645 | 13.148955 | 5.125753 | 5.465478 | 0.416x | 1.066x | pass |

Artifacts:

- `docs/reports/goal2129_public_pod_a5000_steady/public_hd_8192.json`
- `docs/reports/goal2129_public_pod_a5000_steady/public_hd_32768.json`
- `docs/reports/goal2129_public_pod_a5000_steady/public_hd_65536.json`
- `docs/reports/goal2129_public_pod_a5000_steady/public_hd_131072.json`
- `docs/reports/goal2129_public_pod_a5000_steady/public_hd_262144.json`
- `docs/reports/goal2129_public_pod_a5000_steady/public_hd_524288.json`

## Full-Dragon Group-Size Sweep

The `524288` request uses the full Dragon vertex count, so the actual source count is `437,645`.

This sweep skips dense CuPy and compares grouped CuPy versus RTDL/OptiX at the same `target_points_per_group`.

| group size | Dragon shifted grouped CuPy | Dragon shifted RTDL | RTDL / grouped | Dragon vs Happy grouped CuPy | Dragon vs Happy RTDL | RTDL / grouped |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 256 | 3.252169 | 5.797604 | 1.783x | 3.783389 | 5.671734 | 1.499x |
| 512 | 3.662457 | 5.013515 | 1.369x | 4.166194 | 5.886782 | 1.413x |
| 1,024 | 4.025520 | 5.206066 | 1.293x | 4.754367 | 5.682071 | 1.195x |
| 2,048 | 4.368154 | 5.142583 | 1.177x | 5.087590 | 5.638692 | 1.108x |
| 4,096 | 4.654288 | 5.103053 | 1.096x | 5.543222 | 5.772346 | 1.041x |
| 8,192 | 5.098528 | 5.035266 | 0.988x | 6.141408 | 5.987637 | 0.975x |

Artifacts:

- `docs/reports/goal2129_public_pod_a5000_group_sweep/public_hd_524288_group_256.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/public_hd_524288_group_512.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/public_hd_524288_group_1024.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/public_hd_524288_group_2048.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/public_hd_524288_group_4096.json`
- `docs/reports/goal2129_public_pod_a5000_group_sweep/public_hd_524288_group_8192.json`

Best per engine:

- Dragon shifted: grouped CuPy best `3.252s` at group `256`; RTDL best `5.014s` at group `512`.
- Dragon vs Happy: grouped CuPy best `3.783s` at group `256`; RTDL best `5.639s` at group `2048`.

At the same large group size (`8192`) RTDL narrowly beats grouped CuPy, but that is not the fairest optimized comparison because grouped CuPy is much faster at smaller groups.

## Interpretation

This is a stronger and more honest result than the dense-CuPy comparison:

1. RTDL/OptiX clearly beats dense all-pairs CuPy at large public-data sizes.
2. Once CuPy gets the same broad grid/group pruning idea, the current RTDL/OptiX primitive does not win on these 2D projected point-set cases.
3. The reason is likely structural, not just tuning: the software grouped-grid kernel has a cheap group lower-bound loop and then scans only relevant target cells, while the OptiX path pays custom-primitive traversal, SBT/program overhead, and per-group any-hit/intersection overhead for a 2D point-set problem where a uniform grid is already an excellent accelerator.
4. The current RTDL path still confirms correctness and useful pruning, but we should not claim "RT cores beat optimized CUDA" for this HD harness.

## Design Consequence

For v2.0, the trustworthy claim should be:

> RTDL v2.0 can express an exact public-data Hausdorff workflow and can beat dense all-pairs CUDA/CuPy on large projected point sets, but a fair optimized CuPy grouped-grid baseline remains faster for this particular 2D point-set implementation.

To turn this into a stronger RTDL/OptiX win, the next design work should remain generic and app-agnostic:

- add a more efficient generic nearest-reduction primitive that avoids per-query OptiX any-hit overhead where a cell-grid loop is cheaper;
- support device-resident grouped payloads with less host packing and fewer launch barriers;
- add a multi-level or best-first generic group hierarchy, not just uniform groups;
- test 3D point groups and surface/triangle geometry where RT traversal is more likely to matter;
- keep partner baselines strong so RTDL performance claims stay credible.

## Validation

All rows report parity against both dense CuPy and grouped CuPy where those methods were run. The follow-up artifact test checks the JSON claim boundaries, parity flags, and the key conclusion that grouped CuPy beats the current RTDL path in the best full-Dragon grouped comparison.
