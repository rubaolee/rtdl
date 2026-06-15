# Goal4380 v2.14 Pod Benchmark Execution Evidence

Date: 2026-06-14

Status: current-head execution evidence for the v2.14 draft release packet. This
document does not authorize a release, tag, broad RT-core claim, whole-app
speedup claim, RayJoin-paper reproduction claim, or author-hot-compute parity
claim.

## Executive Readout

The v2.14 non-overlay RT-core-vs-Embree packet now has fresh pod evidence:
11/11 non-overlay rows passed correctness and matrix validation. Each reported
speedup is a per-iteration prepared/hot-phase comparison under the documented
contract, not a whole-application claim.

RayJoin Section 5.7 overlay has fresh local evidence for the exact-ready 2/8
dataset pairs on the pod. Both complete pairs show RTDL OptiX faster than RTDL
Embree under the current route. Full Section 5.7 reproduction remains blocked
because the pod has only 2/8 exact preprocessed CDB overlay inputs.

## Pod And Toolchain

| Item | Value |
| --- | --- |
| Host | `ad938d39a223` |
| GPU | NVIDIA RTX 4000 Ada Generation, 20475 MiB |
| Driver / CUDA runtime reported by `nvidia-smi` | 550.127.08 / 12.4 |
| CPU | AMD EPYC 7702, 1 socket, 64 cores, 128 threads |
| Python | 3.12.3 |
| Source tree | `/workspace/rtdl` |
| Local artifact mirror | `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/` |

The prior Numba/PTX blocker was fixed by making the runner prefer the installed
CUDA 12.4 NVVM/ptxas wheel at
`/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc` for
`NUMBA_CUDA_PREFIX`. That avoids the PTX 8.7 vs driver-supported PTX 8.4 failure
seen when the runner picked the CUDA 12.8 toolchain. The working benchmark path
does not require `NUMBA_CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY=1`.

The RayJoin LSI OptiX route was also repaired. The stale `prepared_optix` route
failed with an OptiX invalid-value error on this pod. The v2.14 runner now uses
`prepared_optix_left_id_dense_count`, which matches the Embree scalar-count
contract and completed the full matrix.

## Non-Overlay Matrix

Evidence:

- `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.json`
- `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/human_scale_same_contract/summary.md`

Validation status: `accept`.

| App | Protocol | OptiX Total | Best Embree Total | Repeats O/E | Per-Iter Speedup | Embree Threads | Public Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `barnes_hut` | same repeat | 1.3808s | 3.6835s | 150/150 | 2.63x | 8 | Prepared node-coverage traversal comparison. |
| `contact_manifold` | same repeat | 2.4028s | 2.9361s | 20/20 | 1.21x | 8 | Modest prepared AABB broadphase gain; not a dramatic whole-app claim. |
| `hausdorff_xhd` | same repeat | 1.6804s | 4.1891s | 200/200 | 2.49x | 8 | Prepared directed-threshold nearest-query comparison. |
| `librts_spatial_index` | duration-bounded | 2.7401s | 3.8976s | 4800/48 | 163.90x | 64 | Prepared AABB-index all-ops contract. |
| `raydb_style` | duration-bounded | 2.9131s | 2.7419s | 5000/240 | 14.05x | 64 | Use per-iteration speedup; totals have different repeat counts. |
| `robot_collision` | duration-bounded | 6.1445s | 2.8996s | 49900/2450 | 9.72x | 8 | Traversal-phase only; not a full hot-loop speedup. |
| `rt_dbscan` | same repeat | 1.2153s | 9.0751s | 90/90 | 8.55x | 64 | RT threshold/core flags plus fixed Numba continuation; disclose handoff difference. |
| `rtnn` | duration-bounded | 4.0488s | 8.8275s | 40/80 | 1.09x | 64 | Modest prepared fixed-radius ranked-summary comparison. |
| `spatial_rayjoin_lsi` | duration-bounded | 1.7566s | 5.1047s | 20000/2000 | 29.93x | 8 | Prepared segment-pair scalar-count comparison. |
| `spatial_rayjoin_pip` | same repeat | 1.4465s | 1.6034s | 2000/2000 | 1.10x | 8 | Prepared PIP scalar-count comparison; small win is expected. |
| `triangle_counting` | duration-bounded | 2.9107s | 3.3402s | 20000/500 | 42.60x | 8 | Prepared weighted any-hit summary comparison. |

## RayJoin Section 5.7 Overlay

Evidence:

- `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.json`
- `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.md`
- `docs/reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_run.json`

Coverage: 2/8 complete, 6/8 skipped because exact inputs are missing.

| Pair | Paper RayJoin Processing (Preprocess) | Local Author RT Process | RTDL OptiX Total | RTDL Embree Total | OptiX-vs-Embree | Count Match |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| County x Zipcode | 0.12s (0.07s) | 5.5215s | 5.7823s | 15.1211s | 2.61x | True |
| Block x Water | 0.23s (0.12s) | 27.9439s | 28.6499s | 53.7928s | 1.88x | True |

The earlier Block x Water "Embree faster" readout is superseded by this fresh
v2.14 run. Under the current route and protocol, RTDL OptiX is faster than RTDL
Embree on both exact-ready overlay pairs.

This still does not prove RTDL hot compute matches the author C++/CUDA/OptiX hot
path. The local author column is process wall time, while RTDL totals are
warm-cache medians under the selected protocol. Paper Table 4 values are
historical reference numbers, not local remeasurements.

Missing exact overlay inputs:

| Pair | Blocker |
| --- | --- |
| `lakes_Africa` x `parks_Africa` | exact CDB pair missing from pod |
| `lakes_Asia` x `parks_Asia` | exact CDB pair missing from pod |
| `lakes_Australia` x `parks_Australia` | exact CDB pair missing from pod |
| `lakes_Europe` x `parks_Europe` | exact CDB pair missing from pod |
| `lakes_North_America` x `parks_North_America` | exact CDB pair missing from pod |
| `lakes_South_America` x `parks_South_America` | exact CDB pair missing from pod |

## Release Consequence

The v2.14 packet can now replace the placeholder non-overlay matrix with fresh
current-head pod evidence. It should still remain unreleased until external
review and maintainer authorization.

The clean public thesis is:

> For the documented prepared contracts, RTDL OptiX/RT-core routes beat the
> same-contract RTDL Embree CPU routes on the fresh non-overlay matrix and on
> the two exact-ready RayJoin overlay rows. Claims remain row-scoped,
> contract-scoped, partner-scoped, and phase-scoped.

Blocked thesis:

> RT cores accelerate every benchmark app as a whole, RTDL reproduces the full
> RayJoin paper Section 5.7 matrix, or RTDL hot compute matches the authors'
> specialized C++/CUDA/OptiX implementation.
