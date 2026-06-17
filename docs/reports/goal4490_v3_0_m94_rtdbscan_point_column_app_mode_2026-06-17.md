# Goal4490 / V3 M94 RT-DBSCAN Point-Column App Mode

## Conclusion

Goal4490 wires the Goal4489 caller-owned CuPy coordinate-column prepare path into an explicit RT-DBSCAN app mode:

`optix_rt_core_flags_cupy_point_columns_predicate_direct_status_column_signature_3d`

This closes the app-integration question, but it does not promote the route as the default. When an app already naturally owns CuPy `float64` `x/y/z` device columns, the direct-status handle prepare is 119x-262x faster in this run. When RT-DBSCAN must construct those columns from Python `Point3D` rows and charge that build, the total result is mixed: one-shot `clustered3d` improves, while `road3d`, `ngsim_dense`, and warmed replay are roughly flat or slower.

## Evidence

Hardware: RTX 4000 Ada pod, driver 550.127.08.

Artifacts:

- `docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.json`
- `docs/reports/goal4490_v3_0_m94_rtdbscan_point_column_app_mode_2026-06-17.jsonl`

Protocol:

- 1,048,576 points
- `partition_cell_factor=0.25`
- `direct_status_convergence_mode=single_pass_candidate`
- `one_shot`: `repeat=1`, `warmup=0`
- `warm_replay`: `repeat=3`, `warmup=1`
- Compare current row-prepare predicate direct-status mode against explicit app-constructed coordinate-column mode.

All signatures matched.

## Matrix

| Protocol | Dataset | Row prepare | Column build | Column handle prepare | Charged column prepare | Prepare speedup if columns already owned | Charged prepare speedup | Charged prepared-total speedup |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| one_shot | clustered3d | 0.671s | 0.449s | 0.0026s | 0.451s | 261.61x | 1.49x | 1.16x |
| one_shot | road3d | 0.304s | 0.337s | 0.0025s | 0.339s | 119.54x | 0.90x | 1.00x |
| one_shot | ngsim_dense | 0.437s | 0.443s | 0.0024s | 0.446s | 181.37x | 0.98x | 0.95x |
| warm_replay | clustered3d | 0.430s | 0.446s | 0.0026s | 0.448s | 168.33x | 0.96x | 0.95x |
| warm_replay | road3d | 0.312s | 0.321s | 0.0025s | 0.323s | 125.07x | 0.97x | 0.95x |
| warm_replay | ngsim_dense | 0.425s | 0.446s | 0.0024s | 0.448s | 174.13x | 0.95x | 0.99x |

## Reading

The column prepare primitive is successful: the handle prepare itself drops to about 2.4-2.6 ms at 1M points. That is the right result for a caller-owned device-column contract.

The app-level result is deliberately stricter. If RT-DBSCAN starts from Python point rows, building app-constructed coordinate columns costs about 0.32-0.45 s. That cost can erase the primitive win, especially when the optimized row-columnization path from Goal4488 is already down to roughly 0.30-0.67 s.

Therefore the public rule is:

- Use the point-column prepare path when the application already owns partner coordinate columns for other reasons.
- Do not construct columns solely to claim the Goal4489 speedup unless the column-build time is charged.
- Keep the existing row-prepare predicate direct-status route as the default measured compact-signature route for Python-row RT-DBSCAN inputs.

## Claim Boundary

This is an internal V3 optimization result, not a public RT-core speedup claim. It proves that RTDL now has both the primitive and app surface for caller-owned coordinate columns, and that its accounting is honest when columns are app-constructed.

It does not prove that temporary column construction should be promoted automatically, and it does not authorize hidden partner selection, hidden output-contract selection, or broad DBSCAN-native wording.
