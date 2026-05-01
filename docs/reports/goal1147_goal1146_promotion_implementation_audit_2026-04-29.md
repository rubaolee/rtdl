# Goal1147 Goal1146 Promotion Implementation Audit

Date: 2026-04-29

Status: `LOCAL_AUDIT_PASS`

## Implemented Decision

After Gemini accepted Goal1146 and Codex wrote the two-AI consensus report,
the public wording matrix was updated exactly as follows:

- `facility_knn_assignment / coverage_threshold_prepared_recentered`:
  promoted to `public_wording_reviewed`.
- `barnes_hut_force_app / node_coverage_prepared_rich`:
  promoted to `public_wording_reviewed`.
- `robot_collision_screening / prepared_pose_flags`:
  remains `public_wording_blocked`.

## Public Wording Now Authorized

Facility:

```text
RTDL's prepared facility coverage-threshold RTX query sub-path measured
0.111619 s and 80.60x versus the reviewed same-contract CPU oracle baseline.
```

Barnes-Hut:

```text
RTDL's prepared Barnes-Hut node-coverage RTX query sub-path measured 0.222256 s
and 240.56x versus the reviewed same-contract Embree node-coverage baseline.
```

## Boundary Preserved

The implementation keeps the public boundary narrow:

- No ranked KNN assignment claim.
- No facility-location optimization claim.
- No robot public speedup claim.
- No Barnes-Hut opening-rule, force-vector reduction, N-body simulation, or
  whole-app speedup claim.
- No broad RT-core acceleration claim.

## Files Updated

- `src/rtdsl/app_support_matrix.py`
- `scripts/goal947_v1_rtx_app_status_page.py`
- `README.md`
- `docs/v1_0_rtx_app_status.md`
- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/release_facing_examples.md`
- `docs/rtdl_feature_guide.md`
- focused public wording/status tests

## Verification

Commands executed:

```bash
PYTHONPATH=src:. python3 scripts/goal947_v1_rtx_app_status_page.py
PYTHONPATH=src:. python3 scripts/goal1020_public_docs_rtx_boundary_audit.py
PYTHONPATH=src:. python3 scripts/goal1024_final_public_surface_audit.py
PYTHONPATH=src:. python3 -m unittest tests.goal1010_public_rtx_readme_wording_test tests.goal1011_rtx_public_wording_matrix_test tests.goal947_v1_rtx_app_status_page_test tests.goal1020_public_docs_rtx_boundary_audit_test tests.goal1024_final_public_surface_audit_test -v
```

Observed results:

- Goal1020 public docs RTX boundary audit: `valid: True`.
- Goal1024 final public surface audit: `valid: True`.
- Focused public wording/status tests: `20` tests OK.
- `docs/v1_0_rtx_app_status.md` reports `9` reviewed public RTX sub-path
  wording rows.

## Boundary

This audit confirms implementation of the two accepted Goal1146 promotions. It
does not tag a release and does not authorize robot public speedup wording or
whole-app speedup claims.
