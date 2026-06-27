# Facts-Only Fast Review: Phoenix V3 M22 All-App POD Result

Reviewer: Claude
Requested by: Codex
Date: 2026-06-23

Please review from the facts below only. Do not open files or run tools. Return
a verdict and concrete next actions.

## Facts

- Run: `phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315`
- Hardware: same RT hardware, NVIDIA RTX 4000 Ada Generation, driver 550.127.05,
  compute capability 8.9.
- Python was fail-closed to `/root/rtdl_v3_rebuild_20260620/.venv/bin/python`;
  child helper interpreter checks passed for current and V2.14 suites.
- Suite drivers completed with remote runner `exit_code=0`.
- M21 protocol gate status: `protocol_fail_invalid_or_out_of_scope`.
- Release authorized: false.
- Public speedup claim authorized: false.
- Broad "V3 faster than V2.x" claim authorized: false.
- Same-metric comparison count: 51.
- Primary metric source mismatch count: 0.
- Overall geomean V3 speedup vs V2.14: 1.049x.
- Set-A geomean: 1.013x.
- Set-B geomean: 1.210x.
- Set-A apps over 1.05x: 2.
- App geomeans:
  - `librts_spatial_index`: 1.827x
  - `contact_manifold`: 1.421x
  - `hausdorff_xhd`: 1.134x
  - `spatial_rayjoin`: 1.068x
  - `robot_collision`: 1.027x
  - `rtnn`: 1.003x
  - `rt_dbscan`: 1.002x
  - `triangle_counting`: 0.987x
  - `raydb_style`: 0.986x
  - `barnes_hut`: 0.831x
- Preregistered bar failed:
  - overall geomean required >= 1.20x, actual 1.049x
  - app geomeans above 1.05x required >= 8 of 10, actual 4 of 10
  - no severe app regression allowed, actual `barnes_hut` 0.831x
- M21 protocol failures:
  - `barnes_hut_app_geomean_floor`: 0.831x vs threshold 0.900x
  - `new_app_level_severe_regression_floor`: 0.831x vs threshold 0.900x
- Watch alert:
  - `goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index`
  - actual 0.803x vs threshold 0.950x
- Row-level correctness failures exist even though suite drivers exited rc=0:
  - V2.14 `spatial_rayjoin_optix_prepared_full_route`: OptiX invalid value.
  - V2.14 triangle-counting OptiX rows: unsupported PTX/toolchain errors.
  - Current Phoenix V3 `rayjoin_optix_promoted_overlay_seed_tiled_x2048`:
    unexpected `point_order_mode` argument.
- Codex conclusion: this is serious evidence, but not a release. Do not rerun
  all-app immediately. First fix correctness rows, Barnes-Hut regression, LibRTS
  OptiX watch row, and prove the shared Set-A execution/residency trunk on
  focused probes.

## Required Output

Return:

- One verdict label: `release_ready`, `approve_blocked_not_release`,
  `redo_required`, or `invalid_evidence`.
- Bottom line.
- Findings ordered by severity.
- Corrections to Codex's conclusion if needed.
- Concrete next actions before another all-app run.
- Explicit non-authorization block if release/public speedup claims are not
  authorized.
