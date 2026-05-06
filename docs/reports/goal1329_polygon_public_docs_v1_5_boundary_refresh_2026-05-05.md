# Goal1329: Polygon Public Docs v1.5 Boundary Refresh

Date: 2026-05-05

## Scope

Refresh active public polygon docs so they no longer describe current compact
polygon/Jaccard summary paths as only app-specific native C++ continuations.

## Changes

- Application catalog now names backend-neutral exact area/set-area summary
  plumbing for compact polygon summary paths.
- Feature guide and release-facing examples keep Goal1263 public wording
  bounded, while separating it from current internal v1.5 plumbing.
- Segment/polygon tutorial and feature home pages now describe native bounded
  collection plus backend-neutral area-summary plumbing for current `main`.

## Boundary

This does not authorize public v1.5 release wording, public Jaccard speedup
wording, broad GIS claims, or a monolithic GPU polygon-area/Jaccard kernel
claim.

## Validation

Targeted local gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal1265_polygon_feature_doc_contract_test \
  tests.goal686_app_catalog_cleanup_test \
  tests.goal938_public_rtx_wording_sync_test

Ran 19 tests in 2.219s
OK
```
