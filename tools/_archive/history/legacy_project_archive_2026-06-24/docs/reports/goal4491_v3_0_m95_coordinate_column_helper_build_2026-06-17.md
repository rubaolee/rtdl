# Goal4491 / V3 M95 Coordinate-Column Helper Build

## Conclusion

Goal4491 removes a redundant full-row `hasattr(z)` pre-scan from the generic `point_rows_to_partner_coordinate_columns_3d` helper and routes coordinate extraction through the same first-row-shape pattern used by the optimized direct-status row-columnization path.

This is a small but real cleanup: on the 1M RT-DBSCAN rows, coordinate-column build improves by 1.04x-1.11x. It does not change the M94 conclusion that app-constructed columns are not a default route promotion.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Artifacts:

- `docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.json`
- `docs/reports/goal4491_v3_0_m95_coordinate_column_helper_build_2026-06-17.jsonl`

Baseline: Goal4490 one-shot app-constructed coordinate-column build time.

| Dataset | Goal4490 build | Goal4491 median build | Speedup |
|---|---:|---:|---:|
| clustered3d | 0.449s | 0.424s | 1.06x |
| road3d | 0.337s | 0.303s | 1.11x |
| ngsim_dense | 0.443s | 0.428s | 1.04x |

## Reading

The optimization removes avoidable host scanning and broadens the helper to support attribute rows, mapping rows, 3-tuples, and id/x/y/z sequences. The effect is intentionally modest because the dominant remaining work is still Python-row extraction and host-to-device upload.

Use this as hygiene for app-constructed coordinate columns, not as a new speedup claim. Caller-owned device columns remain the real high-performance contract.
