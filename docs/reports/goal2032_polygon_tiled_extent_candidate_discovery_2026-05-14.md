# Goal2032 Polygon Tiled Extent Candidate Discovery

Date: 2026-05-14

Status: development evidence, not v2.0 release authorization.

## Purpose

Goal2030 found that the v2 polygon control rows had become fast at 10k and 12k copies, but still used a dense all-pairs CuPy extent mask. That was a design problem, not a correctness problem: the partner continuation was good, but the candidate-discovery prepass could allocate an `O(left * right)` device matrix and therefore failed at 16k copies on the RTX A5000 pod.

Goal2032 replaces that dense extent prepass with tiled candidate discovery in `examples/rtdl_control_apps_cupy_rawkernel.py`. The new helper scans left and right polygons in configurable row tiles, compares each bounded tile pair, appends only positive candidate indices, explicitly releases CuPy temporary tile allocations, and preserves the same downstream RawKernel continuation and Python-visible polygon semantics.

## Code Change

- Added `RTDL_CUPY_EXTENT_TILE_ROWS`, defaulting to `2048`.
- Added `RTDL_CUPY_EXTENT_RIGHT_TILE_ROWS`, defaulting to the left tile size.
- Added `RTDL_CUPY_EXTENT_FREE_TILE_BLOCKS`, defaulting to enabled, so large sweeps do not accumulate temporary tile arrays in the CuPy memory pool.
- Added `_cupy_extent_candidate_indices(left_columns, right_columns)`.
- Reused that helper in both:
  - `_partner_pair_payload_table_cupy_extent`
  - `_positive_candidate_pairs_cupy_extent`
- Removed the two former dense full-left-by-full-right extent masks from the CuPy extent path.

This is still partner-side work. The RTDL native engine remains app-agnostic; the engine provides generic hit/candidate rows and Python+partner code performs app-level continuation.

## Pod Evidence

Pod:

- GPU: NVIDIA RTX A5000
- Driver: 570.211.01
- Working source label: `936aff2f_plus_goal2032_tiled_extent`
- Artifact directory: `docs/reports/goal2032_polygon_tiled_extent_pod_936aff2f_dirty/`

| Row | Copies | v1.8 Python+RTDL median s | v2 Python+CuPy RawKernel+RTDL median s | Ratio | Correctness |
| --- | ---: | ---: | ---: | ---: | --- |
| polygon_pair_overlap_area_rows | 16,384 | 2.130875 | 0.589334 | 0.277x | matched v1.8 oracle |
| polygon_set_jaccard | 16,384 | 1.638568 | 0.373164 | 0.228x | matched v1.8 oracle |
| polygon_pair_overlap_area_rows | 32,768 | 3.917046 | 1.555126 | 0.397x | matched v1.8 oracle |
| polygon_set_jaccard | 32,768 | 3.474475 | 0.965893 | 0.278x | matched v1.8 oracle |
| polygon_pair_overlap_area_rows | 65,536 | 8.169963 | 4.090093 | 0.501x | matched v1.8 oracle |
| polygon_set_jaccard | 65,536 | 6.671408 | 2.854807 | 0.428x | matched v1.8 oracle |
| polygon_pair_overlap_area_rows | 131,072 | 17.266580 | 13.317402 | 0.771x | matched v1.8 oracle |
| polygon_set_jaccard | 131,072 | 13.721578 | 9.082639 | 0.662x | matched v1.8 oracle |

The important change is the 16k case: Goal2030 recorded that the dense path failed before timing due to device memory pressure. With tiling, both polygon rows complete and preserve oracle parity.

## Interpretation

This is a real v2.0 design lesson. For polygon workloads, the partner continuation needs two layers:

1. A bounded-memory candidate table builder.
2. A GPU continuation over only the compact positive candidate table.

The previous implementation had the second layer but used an unbounded first layer. Tiling fixes that without moving polygon-specific behavior into the RTDL engine.

The 32k, 64k, and 131k pair-overlap ratios move toward parity because more candidate rows are materialized and reduced, so this is not the final polygon story. A 262k one-axis tiled rerun still OOMed because CuPy retained tile temporaries and the right side remained too wide for the first implementation. The follow-up code now uses two-axis tiling and explicit tile-block release; its large pod timing is tracked separately as follow-up development evidence. The next polygon target is a reusable compact/paged candidate table contract that keeps materialization bounded even when positive pairs grow.

## Boundaries

- This does not authorize v2.0 release.
- This does not claim arbitrary polygon overlay acceleration.
- This does not claim broad RT-core speedup.
- This comparison remains intentionally not absolutely fair: v1.8 is Python+RTDL with no user C/C++ extension, while v2 uses Python+CuPy RawKernel+RTDL under the explicit user decision.
- The pod source was `936aff2f` plus the uncommitted Goal2032 tiled extent patch; the final committed source must be retested or treated as equivalent only after commit hash propagation is updated.

## Next Work

- Retest after commit with an exact source commit label.
- Extend the same bounded-memory principle to segment materialized rows.
- Split benchmark timing into candidate-build, RTDL/native, partner-continuation, and host-summary phases.
- Retry fixed-radius after CUDA/NVRTC/driver compatibility is repaired.
