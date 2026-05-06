# Goal1330 App Support Matrix Polygon v1.5 Boundary Refresh

Date: 2026-05-05

## Scope

Refresh the app support matrix source and public-facing matrix doc so polygon
pair and polygon-set Jaccard wording no longer hard-codes the stale
`native C++ exact area/set-area continuation` phrasing.

## Changes

- Updated `src/rtdsl/app_support_matrix.py` polygon-pair and Jaccard notes to
  describe backend-neutral native exact-area and set-area/Jaccard summary
  plumbing in compact summary mode.
- Updated `docs/app_engine_support_matrix.md` to match the machine-readable
  matrix boundary.
- Preserved the Goal1263 and Goal1262 public claim boundaries:
  - polygon-pair may describe only the reviewed bounded RT-assisted
    candidate-discovery plus exact-area continuation sub-path;
  - Jaccard remains correctness-ready at chunk 1024 but slower than Embree,
    with no positive public speedup wording.
- Added a regression assertion in
  `tests/goal938_public_rtx_wording_sync_test.py` to keep active public docs
  on backend-neutral v1.5 wording.

## Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal687_app_engine_support_matrix_test tests.goal938_public_rtx_wording_sync_test tests.goal958_public_app_native_continuation_schema_test tests.goal821_public_docs_require_rt_core_test tests.goal1265_polygon_feature_doc_contract_test`
  - 23 tests OK.
- `PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')`
  - 76 tests OK.
- `git diff --check`
  - clean.

## Pod Validation

Pod command supplied by user:
`ssh root@213.173.108.215 -p 14800 -i ~/.ssh/id_rdtl_ed25519`.

Local key note: `/Users/rl2025/.ssh/id_rdtl_ed25519` was not present, so the
pod was accessed with the existing RTDL Codex key
`/Users/rl2025/.ssh/id_ed25519_rtdl_codex`.

Pod source state:

- cloned from GitHub `https://github.com/rubaolee/rtdl.git`
- commit: `e533c4e1a4bce0e7df6d2c6a30b116cae98ca202`

Pod validation:

- focused doc/matrix gate:
  `PYTHONPATH=src:. python3 -m unittest tests.goal687_app_engine_support_matrix_test tests.goal938_public_rtx_wording_sync_test tests.goal958_public_app_native_continuation_schema_test tests.goal821_public_docs_require_rt_core_test tests.goal1265_polygon_feature_doc_contract_test`
  - 23 tests OK.
- first `goal13*` sweep failed because the fresh pod lacked `libgeos_c`
  (`/usr/bin/ld: cannot find -lgeos_c`), which is required by the native
  polygon oracle.
- installed pod dependencies with `apt-get install -y libgeos-dev pkg-config`.
- reran `goal13*` sweep:
  `PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')`
  - 76 tests OK.
