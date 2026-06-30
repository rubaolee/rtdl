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
`collect_k_bounded_i64` materialization contract and
`aggregate_frontier_collect_2d` row-collection contract.

## Summary

| Stage | Count | Apps |
| --- | ---: | --- |
| Ready for AMD functional pod | 10 | `hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `robot_collision`, `contact_manifold`, `raydb_style`, `barnes_hut`, `librts_spatial_index`, `rtnn`, `triangle_counting` |
| Needs generic HIPRT extension | 0 | none |
| Compatibility-only, not AMD perf ready | 0 | none |

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
- aggregate-frontier row collection,
- ranked-summary aggregate and batched prepared sweeps,
- DB grouped count/sum fast paths,
- graph summary fast paths.

Those are generic contracts. They should be added to HIPRT as generic
primitive/runtime extensions, not app-specific native code.

Goals3765-3782 have since moved all ten promoted benchmark apps beyond their
initial row-only, missing-contract, or compatibility-only HIPRT routes on the
NVIDIA CUDA/Orochi HIPRT path. In particular:

- Goal3775 makes the matrix's `ray_triangle_closest_hit_3d` HIPRT entry
  executable.
- Goal3776 adds the generic HIPRT `COLLECT_K_BOUNDED` i64 host-native
  materializer and advances `contact_manifold` to AMD functional-pod readiness.
- Goal3777 adds the generic HIPRT `AGGREGATE_FRONTIER_COLLECT_2D` row
  collector and removes the Barnes-Hut hierarchical node-coverage summary gap.
- Goal3779 adds the generic grouped i64 count/sum materializer for the
  RayDB-style lane.
- Goal3780 adds the grouped f64x2 vector-sum materializer for the Barnes-Hut
  lane.
- Goal3781 adds the generic columnar i64 predicate-scan materializer for the
  RayDB-style lane.
- Goal3782 adds the generic canonical graph-cycle scalar count for the
  triangle-counting lane.

Goal3783 then records the closeout sweep: all ten rows are ready for actual AMD
functional pod validation. These are still not AMD hardware or performance
evidence.

## First AMD Work Order

1. Run AMD functional pod parity for all ten ready rows when AMD hardware is
   available.
2. Save the result under the Goal3784 artifact contract:
   `docs/reports/goal3784_amd_hiprt_functional_pod_validation.json`.
3. Only after that functional pass should we design AMD performance comparison
   packets. The current NVIDIA CUDA/Orochi evidence must remain implementation
   evidence, not AMD evidence.

## Boundary

Goal3753 does not authorize AMD performance claims, HIPRT release claims, public
speedup wording, whole-app acceleration wording, RTDL-beats-paper wording, or
app-specific native-engine logic.

It is a planning gate for the next hardware lane. Real AMD evidence still
requires an AMD HIPRT pod.
