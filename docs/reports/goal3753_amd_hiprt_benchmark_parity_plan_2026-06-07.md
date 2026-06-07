# Goal3753 AMD/HIPRT Benchmark Parity Plan

## Purpose

Goal3753 starts the AMD/HIPRT lane after the v2.9 Numba-reference closure. The
question is no longer "do users have no-RawKernel Numba references for custom
logic?" The next question is: which of the ten benchmark apps can realistically
move to AMD/HIPRT, and which generic contracts must be extended first?

The machine-readable plan is in:

`src/rtdsl/v2_10_amd_hiprt_benchmark_parity.py`

It is backed by the existing engine feature matrix and adds the missing
`point_nearest_segment_2d` feature entry for HIPRT/Embree/OptiX/Vulkan/Apple.

## Summary

| Stage | Count | Apps |
| --- | ---: | --- |
| Ready for AMD functional pod | 1 | `robot_collision` |
| Needs generic HIPRT extension | 7 | `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `contact_manifold`, `barnes_hut`, `librts_spatial_index`, `rtnn` |
| Compatibility-only, not AMD perf ready | 2 | `raydb_style`, `triangle_counting` |

## Interpretation

HIPRT proof surfaces already exist, but benchmark parity is not just "can the
backend run some related predicate?" The benchmark apps use stronger v2.x
contracts:

- prepared segment-pair exact count,
- prepared shape-pair active count,
- nearest-witness output columns,
- grouped max-distance reduction,
- fixed-radius grouped stream flags,
- bounded contact witness collection,
- grouped vector force reductions,
- prepared AABB query,
- ranked-summary aggregate and batched prepared sweeps,
- DB grouped count/sum fast paths,
- graph summary fast paths.

Those are generic contracts. They should be added to HIPRT as generic
primitive/runtime extensions, not app-specific native code.

Goal3765 has since moved `robot_collision` beyond the row-only route by adding
`prepared_grouped_visibility_flags_2d` for HIPRT on the NVIDIA CUDA/Orochi path.
That makes the robot-collision AMD lane ready for functional hardware parity,
but still not AMD performance evidence.

## First AMD Work Order

1. `robot_collision`: run AMD functional pod parity first because it now has
   HIPRT row any-hit plus prepared grouped visibility flags.
2. `spatial_rayjoin`: add HIPRT prepared segment-pair count and shape-pair
   active-count parity.
3. `rt_dbscan` and `rtnn`: add HIPRT fixed-radius grouped/ranked stream parity.
4. `hausdorff_xhd`: add nearest-witness output columns plus grouped max
   reduction.
5. `raydb_style` and `triangle_counting`: promote compatibility fallback paths
   into native HIPRT grouped/scalar summary paths before any AMD performance
   claim.

## Boundary

Goal3753 does not authorize AMD performance claims, HIPRT release claims, public
speedup wording, whole-app acceleration wording, RTDL-beats-paper wording, or
app-specific native-engine logic.

It is a planning gate for the next hardware lane. Real AMD evidence still
requires an AMD HIPRT pod.
