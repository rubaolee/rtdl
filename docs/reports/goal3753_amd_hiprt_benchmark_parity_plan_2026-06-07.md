# Goal3753 AMD/HIPRT Benchmark Parity Plan

## Purpose

Goal3753 starts the AMD/HIPRT lane after the v2.9 Numba-reference closure. The
question is no longer "do users have no-RawKernel Numba references for custom
logic?" The next question is: which of the ten benchmark apps can realistically
move to AMD/HIPRT, and which generic contracts must be extended first?

The machine-readable plan is in:

`src/rtdsl/v2_10_amd_hiprt_benchmark_parity.py`

It is backed by the existing engine feature matrix and adds the HIPRT lane
entries needed by the parity sequence, including the current
`collect_k_bounded_i64` materialization contract.

## Summary

| Stage | Count | Apps |
| --- | ---: | --- |
| Ready for AMD functional pod | 7 | `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `robot_collision`, `contact_manifold`, `librts_spatial_index`, `rtnn` |
| Needs generic HIPRT extension | 1 | `barnes_hut` |
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
- generic bounded witness row materialization,
- ranked-summary aggregate and batched prepared sweeps,
- DB grouped count/sum fast paths,
- graph summary fast paths.

Those are generic contracts. They should be added to HIPRT as generic
primitive/runtime extensions, not app-specific native code.

Goals3765-3776 have since moved `robot_collision`, `spatial_rayjoin`,
`rt_dbscan`, `librts_spatial_index`, `rtnn`, and `hausdorff_xhd` beyond their
initial row-only or missing-contract routes on the NVIDIA CUDA/Orochi HIPRT
path. Goal3775 also makes the matrix's `ray_triangle_closest_hit_3d` HIPRT
entry executable. Goal3776 adds the generic HIPRT `COLLECT_K_BOUNDED` i64
host-native materializer and advances `contact_manifold` to AMD functional-pod
readiness. These are still not AMD performance evidence.

## First AMD Work Order

1. `barnes_hut`: add grouped vector force reductions.
2. `raydb_style` and `triangle_counting`: promote compatibility fallback paths
   into native HIPRT grouped/scalar summary paths before any AMD performance
   claim.
3. Run AMD functional pod parity for the seven ready rows when AMD hardware is
   available.

## Boundary

Goal3753 does not authorize AMD performance claims, HIPRT release claims, public
speedup wording, whole-app acceleration wording, RTDL-beats-paper wording, or
app-specific native-engine logic.

It is a planning gate for the next hardware lane. Real AMD evidence still
requires an AMD HIPRT pod.
