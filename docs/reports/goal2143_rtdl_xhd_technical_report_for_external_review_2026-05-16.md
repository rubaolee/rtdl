# Goal2143: RTDL/X-HD Hausdorff Technical Report For External Review

Date: 2026-05-16

Status: technical report for external review

Intended reviewers: X-HD authors and independent RTDL reviewers

## Executive Summary

This report explains how RTDL v2 was used to implement and optimize an exact
2D projected-point Hausdorff-distance application using ideas inspired by
X-HD, while preserving the central RTDL design rule: the native engine remains
app-agnostic and the Hausdorff policy lives outside the engine.

The strongest measured result is:

RTDL/OptiX computes exact 2D projected-point Hausdorff distance and beats an
optimized grouped CuPy raw-kernel baseline on substantial public graphics and
geo point-set workloads on an RTX A5000. Across the accepted evidence rows, the
RTDL/OptiX path shows roughly 6x to 14x speedups on dense graphics and detailed
geo rows, while sparse Natural Earth rows show more modest 1.2x to 1.5x
speedups because fixed launch and preparation overhead dominate.

This is not a claim of full X-HD reproduction. It is not a full 3D surface
Hausdorff implementation, not an MRI/BraTS reproduction, not a reproduction of
the original local X-HD WKT files, and not a universal proof that every CUDA
Hausdorff implementation is slower than RTDL/OptiX.

## The Design Question

RTDL v2 is a Python + partner + RTDL programming model:

- Python owns application policy and orchestration.
- A partner library such as CuPy owns ordinary GPU compute and validation
  baselines.
- RTDL exposes generic ray-tracing traversal and reduction primitives.
- The native engine must not contain app names or app-specific kernels.

The Hausdorff test asks whether this model is strong enough for a real
algorithmic application, not just a small demo. The target function is the
undirected Hausdorff distance between two 2D point sets:

```text
H(A, B) = max(directed(A, B), directed(B, A))
directed(A, B) = max over a in A of min over b in B distance(a, b)
```

The exact output includes the distance, direction, source index, and target
witness index.

## Relationship To X-HD

X-HD motivated the app-level strategy: use spatial organization, threshold
decisions, pruning, and RT traversal to avoid brute-force nearest-neighbor work.
Our implementation applies those ideas to public 2D projected-point workloads.

The mapping is:

| X-HD-inspired idea | RTDL implementation |
| --- | --- |
| Spatial grouping | Python builds uniform point groups with AABB bounds. |
| Seed lower bound | Python samples deterministic source points and computes an exact seed witness. |
| Threshold pruning | RTDL/OptiX writes per-query flags for source points that already have a target group within the seed radius. |
| Exact final witness | RTDL/OptiX reduces the unresolved subset to the max nearest-witness row. |
| Bidirectional HD | Python runs A-to-B and B-to-A and selects the larger directed value. |

The important distinction is that RTDL did not add a native "Hausdorff" engine
path. Native code sees point columns, point-group bounds, radii, flags, and
nearest-witness rows. Python gives those generic operations Hausdorff meaning.

## App-Agnostic Engine Contract

The native OptiX entry points used by the final path are generic:

- `rtdl_optix_prepare_point_group_nearest_witness_2d`
- `rtdl_optix_count_prepared_point_group_threshold_reached_2d`
- `rtdl_optix_write_prepared_point_group_threshold_flags_2d`
- `rtdl_optix_run_prepared_point_group_nearest_witness_2d`
- `rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d`
- `rtdl_optix_destroy_prepared_point_group_nearest_witness_2d`

The corresponding OptiX kernel concepts are also generic:

- `__raygen__point_group_threshold_probe`
- `__intersection__point_group_threshold_isect`
- `__anyhit__point_group_threshold_anyhit`
- `__raygen__point_group_nearest_probe`
- `__intersection__point_group_nearest_isect`
- `__anyhit__point_group_nearest_anyhit`
- `reduce_point_group_nearest_max_distance`

These names are intentionally not `hausdorff_*`, `xhd_*`, `polygon_*`, or
`geo_*`. The engine is a traversal/reduction substrate; the application decides
how to use the substrate.

## User-Level Implementation

The main user-facing implementation is in:

- `examples/rtdl_hausdorff_v2_function.py`

The final RT path is:

- `hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness`
- `_directed_rt_grouped_seeded_pruned_nearest_witness`

The helper structure is:

- `_build_uniform_point_group_columns` sorts target points into deterministic
  uniform groups and emits per-group AABB metadata.
- `_seed_sample_point_columns` selects deterministic source samples, including
  extrema, to get a useful exact lower-bound witness.
- `_pack_point_columns_for_optix` calls `rtdsl.optix_runtime.pack_points` so
  NumPy columns are moved into RTDL packed point buffers without per-row Python
  object construction.
- `PreparedOptixPointGroupNearestWitness2D.threshold_flags` returns the
  source-point mask used by the pruning step.
- `PreparedOptixPointGroupNearestWitness2D.nearest_max_distance_row` returns
  the exact max nearest-witness row for the remaining unresolved candidates.

At the application level, the directed pass is:

1. Pack source columns and target columns.
2. Sort targets into point groups and prepare an OptiX point-group scene.
3. Compute an exact seed distance on a deterministic source sample.
4. Ask RTDL/OptiX for threshold flags at that seed distance.
5. Keep only source points that are still unresolved by the threshold pass.
6. Run exact nearest-witness reduction on that unresolved subset.
7. Repeat for the opposite direction and select the larger directed result.

This preserves exactness because the seed is a real lower bound and the final
distance is computed by exact nearest-witness reduction over the points that
can still improve that bound.

## Why The Current Version Became Fast

The decisive improvement was not a hard-coded Hausdorff native kernel. The
speedup came from three generic improvements working together:

1. Point-group threshold flags:
   RTDL/OptiX can answer "does this source point have a nearby target group
   under this radius?" for all source points with RT traversal.

2. Exact point-group nearest-witness reduction:
   RTDL/OptiX can compute the max nearest-witness row after pruning, without
   returning all per-source witness rows to Python.

3. Vectorized point packing:
   Earlier runs found that X-HD-style pruning left only tiny unresolved
   subsets, but Python/ctypes row packing dominated the runtime. Goal2131 and
   Goal2132 moved `pack_points` to a vectorized NumPy-owner buffer path. After
   this change, the measured time reflected useful RT traversal and reduction
   instead of Python conversion overhead.

The fairness baseline was also strengthened. The comparison baseline is not
naive Python and not an intentionally weak all-pairs CUDA kernel. It is an
optimized grouped CuPy raw-kernel baseline with the same public input data and
the same exact distance check. The CuPy baseline uses CUDA cores and grouped
spatial structure; it does not use OptiX RT traversal.

## RT Traversal Evidence

The RTDL path uses OptiX custom primitive traversal:

- the native backend builds OptiX raygen/miss/intersection/anyhit pipelines;
- point groups are represented as AABB primitives;
- threshold and nearest passes are launched with `optixLaunch`;
- the evidence was measured on an NVIDIA RTX A5000 with driver 570.211.01.

This report calls the path RTDL/OptiX RT traversal or RT-core-facing traversal.
It does not claim profiler-counter proof of physical RT-core occupancy because
Nsight counter evidence was not collected in this round.

## Evaluation Method

The evaluation compares:

- RTDL/OptiX seeded-pruned exact nearest-witness HD;
- optimized grouped CuPy raw-kernel exact HD;
- correctness against the grouped CuPy distance in every artifact row.

The measurement harness is:

- `scripts/goal2126_public_hausdorff_dataset_perf.py`

The benchmark downloads public data, converts inputs to normalized 2D point
sets, runs the grouped CuPy baseline, runs the RTDL/OptiX path, and records
JSON artifacts. Every accepted row includes
`matches_cupy_grouped_grid_seeded_pruned: true`.

The primary hardware was:

- NVIDIA RTX A5000
- driver 570.211.01
- RTDL commit lineage from Goals 2132, 2134, 2136, and 2139

## Dataset Lanes

| Lane | Data source | Scope |
| --- | --- | --- |
| Stanford controls | Stanford 3D Scanning Repository Dragon and Happy Buddha | Vertices projected to XY; control rows for the first exact RTDL/OptiX win. |
| X-HD graphics names | Stanford Dragon, Happy Buddha, Asian Dragon, Thai Statuette | Public model names used by X-HD graphics scripts, projected to XY. |
| Dense graphics stress | Same X-HD graphics names | Up to 1,048,576 requested points to test scaling. |
| Public geo analogues | U.S. Census TIGER/Line 2023 and Natural Earth 1:10m | Public analogues for X-HD county/zip/lakes/parks WKT lanes, normalized lon/lat vertices. |

The public geo loader uses deterministic streaming reservoir sampling for large
shapefiles. In the Census/ZCTA row, the harness observed about 8.20 million
county vertices and 51.22 million ZCTA vertices before sampling.

## Headline Results

| Lane | Strongest representative row | Grouped CuPy | RTDL/OptiX | Speedup |
| --- | --- | ---: | ---: | ---: |
| Stanford control | Dragon vs Happy XY | 3.417380 s | 0.535331 s | 6.38x |
| X-HD graphics | Dragon vs Happy Buddha, 437k, group 4096 | 5.592102 s | 0.591490 s | 9.45x |
| X-HD graphics dense stress | Thai Statuette vs Asian Dragon, 1M, group 8192 | 17.380398 s | 1.248008 s | 13.93x |
| Public geo detailed | Census counties vs ZCTA, 262k, group 1024 | 3.760128 s | 0.301055 s | 12.49x |
| Public geo sparse | Natural Earth lakes vs parks, 162k, group 2048 | 0.113681 s | 0.076850 s | 1.48x |

The sparse Natural Earth row is intentionally included. It is correct and
faster, but it is not a headline speedup row. The workload is too small and
sparse for RT traversal to dominate fixed overhead.

## Full Evidence Summary

| Goal | Dataset lane | Accepted result |
| --- | --- | --- |
| Goal2132 | Stanford Dragon/Happy projected XY controls | 6.10x to 6.38x best-vs-best over grouped CuPy. |
| Goal2134 | X-HD graphics model names at 262k and 437k/524k effective points | 4.08x to 8.66x best-vs-best over grouped CuPy. |
| Goal2136 | Dense X-HD graphics stress | 8.26x to 13.93x over grouped CuPy. |
| Goal2139 | Public geo analogues | Census 6.84x to 12.49x; Natural Earth 1.20x to 1.48x. |

Across these reports, 52 measured artifact rows matched grouped CuPy
correctness within the harness tolerance.

## Reproduction Commands

The public harness expects an OptiX-enabled RTDL build and CuPy on an NVIDIA
host. A representative run shape is:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/path/to/librtdl_optix.so \
python3 scripts/goal2126_public_hausdorff_dataset_perf.py \
  --case-suite xhd-graphics \
  --sample-count 524288 \
  --group-size 4096 \
  --json-out docs/reports/scratch_xhd_graphics_524288_group_4096.json
```

For public geo analogues:

```bash
PYTHONPATH=src:. \
RTDL_OPTIX_LIBRARY=/path/to/librtdl_optix.so \
python3 scripts/goal2126_public_hausdorff_dataset_perf.py \
  --case-suite public-geo \
  --sample-count 262144 \
  --group-size 1024 \
  --json-out docs/reports/scratch_public_geo_262144_group_1024.json
```

The committed evidence artifacts are under:

- `docs/reports/goal2131_public_pod_a5000_seeded_pruned_sweep_packfast/`
- `docs/reports/goal2134_xhd_graphics_pod_a5000/`
- `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/`
- `docs/reports/goal2139_public_geo_pod_a5000/`

## Claim Boundary

| Claim | Status |
| --- | --- |
| RTDL v2 can express an exact 2D projected-point HD application in Python | `accept` |
| RTDL/OptiX uses generic point-group RT traversal for the measured path | `accept` |
| The native engine remains app-agnostic for this work | `accept` |
| RTDL/OptiX beats optimized grouped CuPy on the measured dense graphics and detailed geo rows | `accept-with-boundary` |
| Sparse Natural Earth rows show large RT speedups | `not-claimed` |
| Full X-HD paper reproduction | `not-claimed` |
| Full 3D surface Hausdorff | `not-claimed` |
| MRI/BraTS X-HD reproduction | `not-claimed` |
| Original X-HD local WKT files reproduced exactly | `not-claimed` |
| Universal CUDA-vs-RT speedup | `not-claimed` |
| v2.0 release authorization | `not-authorized-here` |

## Differences From Full X-HD

This work is best read as an RTDL language/runtime case study guided by X-HD,
not as a replacement for X-HD:

- X-HD covers broader input modes and paper-specific benchmark settings.
- This RTDL report covers exact 2D projected-point HD over public graphics and
  geo vertex sets.
- X-HD may include full 3D surface, image/MRI, and local WKT workflows that are
  outside this round.
- RTDL's focus is exposing reusable RT traversal primitives to Python programs
  while preserving a generic native engine.

## Review Questions For X-HD Authors

We would especially value external review on these points:

1. Is the X-HD-inspired mapping from seed/prune/threshold traversal to RTDL's
   point-group API technically faithful enough to describe as X-HD-guided?
2. Are the claim boundaries sufficiently clear to avoid implying full X-HD
   reproduction?
3. Which original X-HD workload should be prioritized next if we want the
   closest possible apples-to-apples follow-up?
4. Would a 3D point or surface variant need a different primitive contract, or
   is the current point-group threshold/witness contract a reasonable base?
5. Are there CUDA baseline optimizations beyond grouped-grid raw kernels that
   should be added before making stronger public comparisons?

## Recommended Next Work

1. Add profiler-counter evidence if we want to state physical RT-core use more
   strongly than OptiX RT traversal.
2. Add a 3D point-set variant before discussing full 3D surface Hausdorff.
3. Reproduce the original X-HD local WKT/MRI lanes if those datasets become
   available under a clear license.
4. Continue improving sparse/small workload batching, because Natural Earth
   shows that overhead can dominate when the candidate set is small.
5. Keep the native engine generic. If a new primitive is needed, it should be
   expressed as a reusable traversal/reduction contract, not a Hausdorff
   special case.

## Artifact Index

- `examples/rtdl_hausdorff_v2_function.py`
- `examples/rtdl_hausdorff_v2_user_benchmark.py`
- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `src/rtdsl/optix_runtime.py`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `docs/reports/goal2132_xhd_seeded_pruned_packfast_a5000_perf_2026-05-16.md`
- `docs/reports/goal2134_xhd_graphics_dataset_perf_2026-05-16.md`
- `docs/reports/goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md`
- `docs/reports/goal2139_public_geo_hausdorff_perf_2026-05-16.md`
- `docs/reports/goal2141_rtdl_hausdorff_application_acceleration_synthesis_2026-05-16.md`
- `docs/reviews/goal2133_gemini_review_goal2131_2132_xhd_packfast_hd_2026-05-16.md`
- `docs/reviews/goal2135_gemini_review_goal2134_xhd_graphics_hd_perf_2026-05-16.md`
- `docs/reviews/goal2137_gemini_review_goal2136_dense_xhd_graphics_stress_2026-05-16.md`
- `docs/reviews/goal2140_gemini_review_goal2139_public_geo_hd_perf_2026-05-16.md`
- `docs/reviews/goal2142_gemini_review_goal2141_hausdorff_synthesis_2026-05-16.md`
