# Goal3859 - RT-DBSCAN Numba Grouped-Stream Route

Date: 2026-06-08

Status: internal engineering evidence, accepted locally pending external review.

## Purpose

Goal3859 replaces the current RT-DBSCAN Numba scale-profile route with a faster generic grouped-stream continuation:

- old current route: `optix_rt_core_flags_numba_prepared_grid_column_signature_3d`
- new current route: `optix_rt_core_grouped_stream_numba_column_signature_3d`

The reason is precise. Goal3858 showed that RT-DBSCAN's old Numba reference implementation spent most of the hot time outside the native RT traversal: threshold flags were produced by OptiX, but the component continuation still used a Numba grid pass plus a column-signature pass. The existing CuPy grouped-stream path was already much faster because it used RTDL's generic prepared OptiX grouped-union primitive and only left the final label/signature work to the partner.

Goal3859 gives the Numba reference implementation the same generic grouped-stream route.

## Implementation

The implementation adds a Numba variant of the generic fixed-radius graph component continuation:

- `PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D`
- `prepare_optix_numba_radius_graph_grouped_stream_continuation_3d`
- `radius_graph_components_3d_optix_numba_prepared_grouped_stream_partner_columns`

The public v2.8 fixed-radius graph component front door now supports explicit user-selected partners:

```text
("cupy", "numba")
```

There is still no automatic partner selection. A user must choose the partner. Unsupported partners fail closed.

The RT-DBSCAN benchmark app gained two explicit modes:

- `optix_rt_core_grouped_stream_numba_components_3d`
- `optix_rt_core_grouped_stream_numba_column_signature_3d`

The scale-profile registry now uses the no-row column-signature mode for RT-DBSCAN, keeping Python row materialization out of the benchmark row.

## Native Boundary

This goal does not add a DBSCAN-specific native engine path.

The native side remains the generic OptiX grouped-union primitive:

```text
rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs
```

The DBSCAN-specific interpretation remains in the benchmark app and partner continuation layer. The front-door module stays app-agnostic and uses generic fixed-radius graph component terminology.

## A5000 Evidence

Pod:

```text
ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519
```

Local copied artifact directory:

```text
docs/reports/goal3859_rt_dbscan_numba_grouped_stream_a5000/
```

Focused same-input comparison at 65,536 clustered 3D points:

| Route | Hot elapsed sec |
| --- | ---: |
| old Numba threshold + prepared grid column signature | 0.263306 |
| existing CuPy grouped-stream column signature | 0.105692 |
| new Numba grouped-stream column signature | 0.107497 |

Observed ratios:

| Comparison | Ratio |
| --- | ---: |
| new Numba grouped-stream vs old Numba threshold route | 2.449x faster |
| new Numba grouped-stream vs CuPy grouped-stream | 1.017x as slow |

The new Numba route matched both the old Numba signature and the CuPy grouped-stream signature:

```text
all_match: true
```

The full ten-app scale-profile refresh also passed with the new registry route:

```text
all_pass: true
json_pass_count: 10
rt_dbscan hot elapsed: 0.110094 sec
rt_dbscan path: optix_rt_grouped_stream_numba_radius_graph_column_signature_3d
rt_dbscan partner: numba
```

## Remaining Work

The new route still has bounded overhead that is not hidden:

- the prepared native scene is still built from host point rows;
- the all-core clustered workload still computes a cached threshold/count column before the grouped-union route;
- the final column-signature step still runs as a separate partner pass;
- the evidence is A5000 internal engineering evidence, not a public release claim.

The next meaningful RT-DBSCAN performance step is not app-specific native DBSCAN. It is either:

- a generic all-items grouped-union mode that can skip the core-flag threshold pass when the caller contract proves every point is eligible, or
- a more general device-resident fixed-radius component/signature primitive that keeps the summary continuation fully inside the generic RTDL runtime.

## Claim Boundary

This goal does not authorize:

- release action;
- public speedup wording;
- whole-app acceleration claims;
- broad RT-core claims;
- paper reproduction claims;
- true zero-copy claims;
- automatic partner selection claims;
- app-specific native-engine logic.

The accepted claim is narrower: for the internal A5000 RT-DBSCAN scale row, the explicit `numba` grouped-stream route is faster than the old Numba threshold/grid route and nearly matches the existing CuPy grouped-stream route while keeping the native primitive generic.

