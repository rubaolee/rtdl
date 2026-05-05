# Goal1324: v1.5 Front-Door Docs Refresh

Date: 2026-05-05

## Scope

Refresh the public entry docs after Goal1323 so the front-door documentation
does not still describe v1.5 as only future work.

This is a documentation-only change. It does not authorize a public v1.5
release, does not add public whole-app speedup wording, and does not change any
backend behavior.

## Updated Boundary

- Current released version remains `v1.0`.
- Current `main` has internally pod-verified v1.5 generic primitive subpaths
  for the supported migration inventory.
- Public v1.5 release wording remains unauthorized until a release package and
  claim review explicitly authorize it.
- Whole-app graph, DB, polygon, ranking, clustering, SQL-style materialization,
  exact-distance rows, and force-vector reductions remain outside public
  speedup wording unless a later report explicitly moves them.
- Before v2.1, backend scope remains Embree and OptiX; Vulkan, HIPRT, and Apple
  RT work remains frozen except for existing documentation/history.

## Files Refreshed

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `docs/current_architecture.md`
- `docs/performance_model.md`
- `docs/v1_0_app_acceleration_inventory.md`
- `docs/rtdl/README.md`

Historical release/review artifacts were intentionally left historical.

## Validation

Local targeted public-doc gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1230_v1_0_app_acceleration_inventory_test \
  tests.goal1232_public_doc_map_test \
  tests.goal1244_public_doc_spine_test

Ran 10 tests in 0.002s
OK
```
