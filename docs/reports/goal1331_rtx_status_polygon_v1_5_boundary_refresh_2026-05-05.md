# Goal1331 RTX Status Polygon v1.5 Boundary Refresh

Date: 2026-05-05

## Scope

Refresh active RTX status surfaces so polygon-pair and polygon-set Jaccard
status wording no longer uses stale `native C++ exact area/set-area
continuation` phrasing.

Historical reports and copied pod artifacts are intentionally unchanged.

## Changes

- Updated `scripts/goal947_v1_rtx_app_status_page.py`, the generator for the
  active v1.0 RTX status page.
- Regenerated `docs/v1_0_rtx_app_status.md` from the updated generator.
- Updated `docs/v1_1_optix_status.md` to distinguish the reviewed Goal1263
  bounded polygon-pair claim from current internal v1.5 backend-neutral native
  area-summary plumbing.
- Extended `tests/goal938_public_rtx_wording_sync_test.py` so the active v1.0
  and v1.1 RTX status pages are covered by the backend-neutral wording gate.
- Updated the stale Goal1010 assertion for the current 13 reviewed RTX
  sub-path wording rows after Goal1263.

## Boundary

- v1.0 remains the current public release.
- This does not authorize public v1.5 release wording.
- Goal1263 polygon-pair wording remains bounded to RT-assisted LSI/PIP
  positive candidate discovery plus exact area continuation.
- Jaccard remains correctness-ready/diagnostic with OptiX slower than Embree
  and no positive public speedup wording.

## Validation

- `PYTHONPATH=src:. python3 -m unittest tests.goal938_public_rtx_wording_sync_test tests.goal947_v1_rtx_app_status_page_test tests.goal1010_public_rtx_readme_wording_test tests.goal1228_v1_0_positioning_docs_test`
  - 22 tests OK.
- `PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')`
  - 76 tests OK.
- `git diff --check`
  - clean.

Pod validation is pending for the pushed commit.

