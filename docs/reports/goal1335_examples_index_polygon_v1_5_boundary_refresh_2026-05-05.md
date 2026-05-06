# Goal1335 Examples Index Polygon v1.5 Boundary Refresh

Date: 2026-05-05

## Scope

Refresh the active examples index so polygon-pair and Jaccard compact summary
descriptions match the current backend-neutral v1.5 summary plumbing.

Historical reports, artifact JSONs, and released v1.0 package text are
intentionally unchanged.

## Changes

- Updated `examples/README.md` polygon-pair compact summary wording to use
  backend-neutral native exact-area summary language.
- Updated `examples/README.md` Jaccard compact summary wording to use
  backend-neutral native set-area/Jaccard summary language.
- Extended `tests/goal938_public_rtx_wording_sync_test.py` so the active
  examples index is covered by the polygon/Jaccard stale wording gate.

## Boundary

- v1.0 remains the current public release.
- This does not authorize public v1.5 release wording.
- This does not change reviewed Goal1263 polygon-pair public claim scope.
- Jaccard positive public speedup wording remains unauthorized.

## Local Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal938_public_rtx_wording_sync_test tests.goal646_public_front_page_doc_consistency_test tests.goal655_tutorial_example_current_main_consistency_test tests.goal687_app_engine_support_matrix_test`
  - 20 tests OK.
- `PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')`
  - 76 tests OK.
- `git diff --check`
  - clean.

## Pod Validation

Pod source state:

- reset `/root/rtdl_python_only` from GitHub `origin/main`
- commit: `74452cb3812d9a0d3e151277f9b9cde232410039`

Pod validation:

- active examples/public-doc focused gate:
  `PYTHONPATH=src:. python3 -m unittest tests.goal938_public_rtx_wording_sync_test tests.goal646_public_front_page_doc_consistency_test tests.goal655_tutorial_example_current_main_consistency_test tests.goal687_app_engine_support_matrix_test`
  - 20 tests OK.
