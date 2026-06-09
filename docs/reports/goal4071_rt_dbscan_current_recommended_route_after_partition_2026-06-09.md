# Goal4071 RT-DBSCAN Current Recommended Route After Partition Preview

Date: 2026-06-09

## Purpose

Goals4065-4070 explored the partition-convergence component-signature preview
and the `device_count_then_emit` memory-pressure option. Goal4071 refreshes the
RT-DBSCAN route-positioning evidence after that work: the key question is
whether the partition preview should displace the current RT-core grouped-stream
Numba signature route.

## Routes Compared

The runner compares four same-profile routes on `clustered3d`, 65,536 points:

- recommended RT-core grouped stream + Numba direct component-size signature;
- prepared partition-convergence CuPy signature with `device_count_then_emit`;
- Numba prepared grid partner baseline;
- CuPy prepared grid partner baseline.

## Boundary

This is route-positioning evidence only. It does not authorize release wording,
paper reproduction, public speedup wording, broad RT-core wording, whole-app
benchmark wording, hidden dispatch, automatic partner selection, app-specific
native engine logic, native ABI addition, or true-zero-copy wording.

## Validation

Added:

- `scripts/goal4071_rt_dbscan_current_recommended_route_after_partition.py`.
- `tests/goal4071_rt_dbscan_current_recommended_route_after_partition_test.py`.
- `docs/reports/goal4071_rt_dbscan_current_recommended_route_after_partition_pod.json`.
- `docs/reports/goal4071_rt_dbscan_current_recommended_route_after_partition_pod.stdout.txt`.

The runner records both raw signature equality and normalized component-size
signature equality. This matters because the recommended full RT-DBSCAN route
reports `cluster_sizes`, while the graph-component-only partition route reports
`component_sizes`; they can agree on the component-size contract while retaining
different app-level signature schemas. The runner also records how much faster
the recommended route is than each candidate on the same profile.

## Pod Evidence

Pod evidence was recorded on RTX 4000 Ada at source commit `c0073cd6`.

| Route | RT Cores | Partner | Elapsed sec | Same Component Sizes | Recommended Faster By |
| --- | --- | --- | ---: | --- | ---: |
| `optix_rt_core_grouped_stream_numba_column_signature_3d` | yes | Numba | 0.094191 | yes | 1.000x |
| `partner_cupy_prepared_partition_convergence_component_signature_3d` with `device_count_then_emit` | no | CuPy | 0.682616 | yes | 7.247x |
| `partner_numba_prepared_grid_components_3d` | no | Numba | 1.208361 | yes | 12.829x |
| `partner_cupy_prepared_grid_components_3d` | no | CuPy | 0.577128 | yes | 6.127x |

Conclusion: the partition-convergence lane remains a useful graph-component
signature candidate and memory-pressure study, but it should not displace the
current recommended RT-core grouped-stream Numba route. On this 65,536-point
clustered profile, the recommended route remains 6.1x-12.8x faster than the
same-component-size opponents and keeps the RT-core path as the benchmark-app
default recommendation. This is internal route-positioning evidence only, not a
public speedup claim.
