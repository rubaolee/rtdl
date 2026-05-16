# Goal2131: X-HD Sample-Seeded Pruning for RTDL/OptiX Hausdorff

Date: 2026-05-16

Status: implementation ready for pod validation

## Purpose

Goal2129 made the comparison fair by adding an optimized grouped CuPy baseline. That baseline still beat the current RTDL/OptiX grouped nearest-witness path on the largest public projected-XY cases, so Goal2131 adds the next X-HD-inspired optimization without changing the RTDL app-agnostic engine rule.

The core technique is sample-seeded threshold pruning.

The new path is exact, not a threshold approximation:

1. Run a small exact RTDL/OptiX nearest-witness pass over a deterministic source sample to obtain a real Hausdorff lower-bound witness.
2. Run a generic point-group threshold-flags pass with that radius to mark source points that already have a target within the current lower bound.
3. Skip those safe points, because they cannot increase the directed Hausdorff maximum.
4. Run the exact point-group nearest-witness max reduction only on the remaining unsafe subset.
5. Take the maximum of the sample witness and unsafe-subset witness.

This mirrors the X-HD idea of using lower bounds and unresolved queues, but the native ABI remains generic.

## Native Surface

Added one generic OptiX native operation for generic point-group threshold flags:

```text
rtdl_optix_write_prepared_point_group_threshold_flags_2d
```

It takes a prepared point-group scene, query points, a radius, and a threshold, and returns one threshold-reached flag per query. It is intentionally not named after Hausdorff, Frechet, X-HD, or any application.

The existing count-only operation remains available:

```text
rtdl_optix_count_prepared_point_group_threshold_reached_2d
```

## Python Surface

`PreparedOptixPointGroupNearestWitness2D.threshold_flags(...)` exposes the per-query mask to Python as a NumPy array.

`pack_points(ids=..., x=..., y=..., dimension=2)` now uses a vectorized structured NumPy owner buffer for column inputs. This removes the previous per-point Python ctypes construction cost for large point arrays and benefits generic point workloads beyond Hausdorff.

The new user-facing HD path is:

```python
hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness(...)
```

It is available through the public method string:

```text
rtdl_rt_grouped_seeded_pruned_nearest_witness
```

The public Stanford perf harness now records:

```text
rtdl_rt_grouped_seeded_pruned_nearest_witness
rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio
```

## Claim Boundary

Engine app-agnostic boundary: `accept`

Outperform optimized grouped CuPy: `needs-pod-evidence`

| Claim | Verdict | Notes |
| --- | --- | --- |
| Engine app-agnostic boundary | `accept` | Native operation is a generic point/group/radius threshold mask. |
| Exact HD semantics | `accept-with-test` | Exactness follows from the lower-bound plus unsafe-subset reduction argument; local structural tests cover wiring. |
| RT-core usage | `accept-with-pod-validation` | The path uses the existing OptiX prepared point-group BVH traversal and must be rebuilt on the RTX pod. |
| Outperform dense CuPy | `expected` | Goal2129 already showed the grouped RT path beats dense CuPy at large public scales. |
| Outperform optimized grouped CuPy | `needs-pod-evidence` | This is the active Goal2131 performance target. |
| X-HD paper dataset equivalence | `needs-more-evidence` | Current public harness uses Stanford projected-XY point sets, not the exact X-HD paper dataset suite. |

## Next Validation

Run the focused local tests, rebuild `librtdl_optix.so` on the A5000 pod, then re-run the public Stanford sweep with grouped CuPy and both RTDL paths. The release-significant row is whether `rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio < 1.0` on the largest cases.
