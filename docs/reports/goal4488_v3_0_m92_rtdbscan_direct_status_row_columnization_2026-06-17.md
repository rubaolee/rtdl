# Goal4488 / V3 M92 RT-DBSCAN Direct-Status Row-Columnization

## Conclusion

Goal4488 closes the measured RT-DBSCAN direct-status prepare row-columnization debt found in Goal4487.

The change is app-agnostic: direct-status prepare now builds host `x/y/z` lists directly for common `Point3D`, mapping, and sequence rows instead of first materializing a generic tuple-of-xyz intermediate. It does not add DBSCAN-specific native logic, does not select partners automatically, and does not change signatures.

## Evidence

Hardware: RTX 4000 Ada pod.

Artifacts:

- `docs/reports/goal4487_v3_0_m91_rtdbscan_direct_status_prepare_breakdown_2026-06-17.json`
- `docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.json`
- `docs/reports/goal4488_v3_0_m92_rtdbscan_direct_status_row_columnization_2026-06-17.jsonl`

## M91 Finding

M91 showed direct-status prepare was not dominated by partition sort, AABB reduction, or RT traversal. On 1M RT-DBSCAN rows, the largest phase was Python row extraction:

| Dataset | M91 diagnostic phase total | Dominant phase | Dominant phase sec |
|---|---:|---|---:|
| clustered3d | 0.881s | row_xyz_extract_sec | 0.475s |
| road3d | 0.747s | row_xyz_extract_sec | 0.469s |
| ngsim_dense | 0.861s | row_xyz_extract_sec | 0.462s |

## M92 Result

All production and diagnostic signatures match. All M92 rows use `attribute_xyz_rows_direct` and avoid the generic tuple intermediate.

| Dataset | M91 diagnostic phase total | M92 diagnostic phase total | Speedup | M92 dominant phase |
|---|---:|---:|---:|---|
| clustered3d | 0.881s | 0.408s | 2.16x | coordinate_columns_sec |
| road3d | 0.747s | 0.311s | 2.40x | coordinate_columns_sec |
| ngsim_dense | 0.861s | 0.432s | 1.99x | coordinate_columns_sec |

Production prepare also improved, with the caveat that the first clustered3d production row includes visible CUDA/CuPy cold-start noise:

| Dataset | M91 production prepare | M92 production prepare | Delta | Speedup |
|---|---:|---:|---:|---:|
| clustered3d | 1.408s | 1.022s | -0.385s | 1.38x |
| road3d | 0.785s | 0.310s | -0.475s | 2.53x |
| ngsim_dense | 0.926s | 0.434s | -0.492s | 2.13x |

One-shot `prepare+replay` improved on the rows least affected by first-row cold start:

| Dataset | M90/M91-style prepare+replay | M92 prepare+replay | Reading |
|---|---:|---:|---|
| road3d | about 5.12s | 4.71s | improved |
| ngsim_dense | about 4.47s | 4.06s | improved |
| clustered3d | cold-start-sensitive | 9.51s production / 8.20s diagnostic | do not overread first row |

## Claim Boundary

This is a prepare-path optimization, not a new RT-core speedup claim. The RT-core count-threshold improvement remains Goal4486. Goal4488 removes avoidable Python host row-columnization work before the CuPy direct-status continuation.

Remaining serious debt: add an explicit direct-status entry point for already-owned partner coordinate columns so apps that naturally hold resident `x/y/z` columns can skip coordinate upload too. That should be a generic primitive/partner handoff, not an RT-DBSCAN-only shortcut.
