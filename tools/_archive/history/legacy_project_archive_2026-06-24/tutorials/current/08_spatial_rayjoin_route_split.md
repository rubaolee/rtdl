# Spatial RayJoin Route Split

Status: V3 rebuild tutorial, not a release claim.

This lesson teaches why Spatial RayJoin has both a slow standard row and strong
internal hot-route evidence. They are different contracts.

## The Slow Row

The standard all-workload row is:

```text
spatial_rayjoin / rayjoin_all_backend_query_summary = 0.03414924661592695x
```

This is a tiny route-health fixture, not a RayJoin paper-scale row:

| Workload | Result size |
| --- | ---: |
| LSI | 1 row |
| Overlay seed | 0 rows |
| PIP | 6 rows |

The timing protocol is also tiny: `warmup=0`, `repeat=1`.

What to learn:

```text
For tiny fixtures, GPU launch, synchronization, query packing, and prepared
route orchestration can dominate the real work. Choose Embree or CPU-style
paths for this row; do not market it as an OptiX win.
```

## The Useful Topology Row

The Phoenix M5 point-location row is the better V3 topology-stream lesson:

| Field | Value |
| --- | ---: |
| Query points | 100,000 |
| Query generation | backend-parity-filtered random bbox |
| Exact-row tie candidates rejected | 1 |
| Exact mismatches | 0 |
| RTDL OptiX wall speedup vs RTDL Embree | 1.920x |
| RTDL OptiX native traversal speedup vs RTDL Embree | 2.834x |
| RayJoin author Query speedup vs RTDL OptiX native traversal | 3.861x |

What to learn:

```text
RTDL can express the same point-location topology contract and its OptiX
lowering beats its Embree lowering on the RTX pod. RayJoin author RT is still
faster than RTDL OptiX on this row, so this is not an RTDL-beats-RayJoin claim.
```

## The Strong Hot-Route Rows

The authored tiled rows are strong internal OptiX-over-Embree signals:

| Row | Signal |
| --- | ---: |
| `rayjoin_overlay_seed_authored_tiled_x2048` | 30489.613x |
| `rayjoin_lsi_authored_tiled_x2048` | 516.792x |
| `rayjoin_pip_authored_tiled_x2048` | 10.703x |

These rows are useful V3 evidence because they instantiate
`point_location_topology_stream`. They are still internal until a future public
row packet closes the timing basis, M3 phase table, author comparison, and
external review.

## Source Packets

- `docs/rebuild/v3/v3_negative_route_explanations_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md`
- `docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m7_feasibility_2026-06-20.md`

## Claim Boundary

Allowed:

```text
Spatial RayJoin is a strong internal topology-stream candidate with a clear
route split: tiny all-workload route-health row, same-contract M5 topology row,
and authored tiled hot-route rows.
```

Forbidden:

```text
Do not claim RTDL beats RayJoin.
Do not claim RayJoin paper reproduction.
Do not claim full polygon overlay acceleration.
Do not compare the 0.034x tiny row to the 30489x hot row without the contract.
Do not promote Spatial RayJoin to M7 from this tutorial.
```

Read next:

- [Claim Boundaries](06_claim_boundaries.md)
