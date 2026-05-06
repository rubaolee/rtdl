# Goal1333 Polygon Performance Table v1.5 Boundary Refresh

Date: 2026-05-05

## Scope

Refresh the active app support matrix OptiX performance-classification table so
polygon-pair and Jaccard rows describe current backend-neutral v1.5 summary
plumbing instead of stale native C++ grid-cell continuation wording.

Historical reports, artifact JSONs, and reviewed public-claim boundary text are
intentionally unchanged.

## Changes

- Updated `src/rtdsl/app_support_matrix.py` polygon-pair OptiX performance note
  to use backend-neutral native exact-area summary wording.
- Updated `docs/app_engine_support_matrix.md` polygon-pair and Jaccard OptiX
  performance rows to match the current source matrix.
- Extended `tests/goal938_public_rtx_wording_sync_test.py` so active polygon
  matrix/status docs and source cannot reintroduce stale native C++ grid-cell
  continuation wording.

## Boundary

- v1.0 remains the current public release.
- This does not authorize public v1.5 release wording.
- This does not change the reviewed Goal1263 public polygon-pair claim scope.
- Jaccard positive public speedup wording remains unauthorized.
- No pod was required because this is active wording/test cleanup only; a quick
  Git-based pod validation was still run because a pod was already available.

## Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal687_app_engine_support_matrix_test tests.goal690_optix_performance_classification_test tests.goal938_public_rtx_wording_sync_test tests.goal1010_public_rtx_readme_wording_test tests.goal1229_current_main_v1_0_readiness_audit_test`
  - 24 tests OK.
- `PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')`
  - 76 tests OK.
- `git diff --check`
  - clean.

## Pod Validation

Pod source state:

- reset `/root/rtdl_python_only` from GitHub `origin/main`
- commit: `b0f3ed22d13fb888b3aa74d4459b1f93e3366ea1`

Pod validation:

- active app-support/status focused gate:
  `PYTHONPATH=src:. python3 -m unittest tests.goal687_app_engine_support_matrix_test tests.goal690_optix_performance_classification_test tests.goal938_public_rtx_wording_sync_test tests.goal1010_public_rtx_readme_wording_test tests.goal1229_current_main_v1_0_readiness_audit_test`
  - 24 tests OK.
