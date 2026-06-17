# Goal4489 / V3 M93 Direct-Status Caller-Owned Point Columns

## Conclusion

Goal4489 adds an app-agnostic direct-status prepare entry point for caller-owned CuPy `float64` `x/y/z` device columns.

When the caller already owns those columns, direct-status prepare no longer performs Python row extraction or host-to-device coordinate upload. The result is a real shared-column handoff, not a hidden DBSCAN shortcut and not automatic partner selection.

## Evidence

Hardware: RTX 4000 Ada pod.

Artifacts:

- `docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.json`
- `docs/reports/goal4489_v3_0_m93_direct_status_point_columns_2026-06-17.jsonl`

All 1M signatures matched row-based direct-status prepare.

| Dataset | Point-column build | Row prepare | Column prepare | Prepare speedup if columns already owned | Row run | Column run |
|---|---:|---:|---:|---:|---:|---:|
| clustered3d | 0.545s | 0.738s | 0.0059s | 124.04x | 5.344s | 5.361s |
| road3d | 0.257s | 0.305s | 0.0037s | 82.73x | 2.084s | 2.068s |
| ngsim_dense | 0.374s | 0.422s | 0.0349s | 12.08x | 1.321s | 1.302s |

The diagnostic prepare phase speedups are consistent:

| Dataset | Phase speedup if columns already owned | Column dominant remaining phase |
|---|---:|---|
| clustered3d | 120.56x | sort_unique_search_sec |
| road3d | 77.09x | partition_aabb_reduce_sec / sort_unique_search_sec |
| ngsim_dense | 11.34x | sort_unique_search_sec |

## Claim Boundary

This evidence only applies when the caller already owns CuPy `float64` `x/y/z` device columns. Point-column construction is reported separately and must not be hidden inside the speedup. If an app only has Python `Point3D` rows, Goal4488 is the applicable row-columnization optimization.

Remaining RT-DBSCAN app work is policy and route integration, not the primitive: use the column entry point only where the app naturally holds partner columns for other work. Do not build columns solely to claim this speedup unless the column build is charged honestly.
