# Goal2123 X-HD-Style Point-Group Nearest Reduction

Date: 2026-05-16

Status: implemented and pod-validated on NVIDIA RTX A5000.

## Purpose

Goal2121 moved exact 2-D Hausdorff distance onto a generic RTDL/OptiX point-group nearest-witness primitive inspired by X-HD's grid/MBR stage. Goal2122 then proved a real large-scale crossover on an RTX A5000: the grouped RT path was slower than CuPy on smaller synthetic sets, but reached 1.33x faster at 524,288 x 524,288 points and 2.21x faster at 1,048,576 x 1,048,576 points.

The remaining avoidable cost was not RT traversal. It was the output contract: each directed pass materialized one nearest-witness row per query point, copied all rows to the host, and then reduced them in Python to the single max-nearest-distance witness that Hausdorff needs.

This goal adds a generic one-row device reduction:

`rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d`

The name deliberately contains no Hausdorff, X-HD, or dataset term. It reduces generic nearest-witness rows by max distance and returns one `RtdlFixedRadiusNeighborRow`: `query_id`, `neighbor_id`, and `distance`.

## What Changed

- Added the OptiX C ABI entry point `rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d`.
- Added a CUDA reduction kernel `reduce_point_group_nearest_max_distance` that runs after the generic point-group RT traversal.
- Added `PreparedOptixPointGroupNearestWitness2D.nearest_max_distance_row(...)` in `src/rtdsl/optix_runtime.py`.
- Added the Python app method `hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(...)`.
- Added the language-lab method key `rtdl_rt_grouped_reduced_nearest_witness`.

## Claim Boundary

Generic engine boundary: `accept`.

The native surface remains app-agnostic: it exposes point groups, nearest witnesses, and max-distance reduction, not Hausdorff logic. Hausdorff remains Python application logic that builds point groups, invokes the generic primitive in both directions, and selects the larger directed result.

Outperform pure CUDA on large synthetic sets: `accept-with-boundary`.

Goal2122 already showed the grouped RT path outperforming a pure CUDA/CuPy exact all-pairs continuation at very large synthetic sizes. Goal2123 moved that crossover earlier because it removes host materialization of per-query rows and avoids constructing Python `Point` tuples on the reduced path. On the A5000 pod, the device-reduced path becomes faster than the CuPy exact all-pairs continuation at 131,072 x 131,072 points and stays faster through 1,048,576 x 1,048,576 points.

Outperform pure CUDA on X-HD paper datasets: `needs-more-evidence`.

The X-HD repository records dataset names and scripts, but the actual large paper datasets were not present in the cloned repository. Matching the paper requires either locating the exact referenced data sources or receiving the same dataset files. Until then, same-dataset speedup remains blocked.

## Remaining X-HD Gaps

- X-HD uses estimators and point-to-MBR bounds to prune source points before full nearest search. This RTDL path currently uses a conservative radius plus optional threshold seeding.
- X-HD routes heavy cells to CUDA because RT intersection shaders are serial inside a ray. This goal does not yet add a heavy-cell CUDA fallback.
- X-HD maintains a device worklist so already-resolved queries drop out. The earlier app-level adaptive worklist was correct but not faster because it paid extra launches and still materialized rows.
- The new reducer addresses the biggest immediate output bottleneck, but a future device worklist would be the next generic primitive if the same-dataset X-HD comparison still falls short.

## Validation Plan

Local/static validation completed:

- `py_compile` for the updated Python files.
- `tests.goal2121_xhd_point_group_hausdorff_optix_enhancement_test`
- `tests.goal2122_xhd_grouped_hausdorff_pod_perf_test`
- `tests.goal2123_xhd_point_group_nearest_reduction_test`

Local Linux validation completed on `192.168.1.20` / GTX 1070 smoke hardware:

- `make build-optix OPTIX_PREFIX=/home/lestat/vendor/optix-dev`
- `tests.goal2121_xhd_point_group_hausdorff_optix_enhancement_test`
- `tests.goal2123_xhd_point_group_nearest_reduction_test`
- Reduced-method smoke: expected exact distance `5.0`, observed `5.0`.

Hardware validation completed on pod `root@69.30.85.189 -p 22108` with key `id_ed25519_rtdl_codex`:

- Rebuild `librtdl_optix.so` on the clean A5000 pod.
- Run correctness smoke for the reduced method against CuPy/CUDA exact results.
- Re-run the synthetic sweep at 4,096 through 1,048,576 points, with progress lines and bounded timeouts.
- If exact X-HD datasets become available, run the same harness over those data.

## A5000 Synthetic Timing

Primary artifact: `docs/reports/goal2123_pod_grouped_reduced_hd_perf_after_pack_cleanup_2026-05-16.json`

Comparison artifact with the older row-materialized RTDL path in the same run: `docs/reports/goal2123_pod_grouped_reduced_hd_perf_2026-05-16.json`

GPU: NVIDIA RTX A5000, driver 570.211.01.

All rows matched the CuPy exact distance at tolerance `1e-6`.

| points per set | CuPy exact sec | reduced RTDL sec | reduced / CuPy |
| ---: | ---: | ---: | ---: |
| 8,192 | 0.505816 | 0.898787 | 1.777x |
| 32,768 | 0.135581 | 0.242093 | 1.786x |
| 65,536 | 0.482721 | 0.518679 | 1.074x |
| 131,072 | 1.913343 | 1.000787 | 0.523x |
| 262,144 | 7.674986 | 2.691339 | 0.351x |
| 524,288 | 30.889076 | 6.677844 | 0.216x |
| 1,048,576 | 124.284452 | 17.361249 | 0.140x |

The meaningful trend begins after CuPy and OptiX have warmed: reduced RTDL remains slightly slower through 65,536, crosses over at 131,072, and reaches about `7.16x` faster than CuPy at 1,048,576 (`124.28 / 17.36`). In the comparison artifact, the reduced path also cuts the older row-materialized RTDL path by roughly `2.42x` at 131,072 and `1.61x` at 1,048,576, even before the Python tuple cleanup.

## Interpretation

This is the first HD RTDL/OptiX path in this lab that beats a pure CUDA-core exact all-pairs continuation at a practically large scale. The key performance shift is not a Hausdorff-specific engine optimization; it is a reusable output primitive:

1. RT cores traverse a much smaller BVH over point-group MBRs instead of one primitive per point.
2. Any-hit code scans only the points inside intersected groups and records one nearest witness per query.
3. A CUDA device reducer computes the max nearest distance and witness IDs before host transfer.
4. Python receives one row per directed pass instead of one row per query point.

The same pattern is useful beyond Hausdorff: generic traversal emits per-query candidates, then generic device reductions convert large row streams into small scalar/witness summaries.

## External Review

- `docs/reviews/goal2124_gemini_review_goal2121_2123_xhd_hausdorff_optix_2026-05-16.md`: `accept` for Goal2121/2122/2123, `accept` for the large-synthetic speedup claim, and `needs-more-evidence` for the exact X-HD paper dataset claim.
- `docs/reviews/goal2125_gemini_review_goal2123_pack_cleanup_perf_addendum_2026-05-16.md`: `accept` for the pack-cleanup boundary, updated A5000 timings, and the statement that reduced RTDL/OptiX beats CuPy at 131,072+ synthetic points while exact X-HD paper dataset evidence remains blocked.
