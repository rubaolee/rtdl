# Goal1340 Polygon Row Metadata Label Refresh

Date: 2026-05-05

## Scope

Refresh active polygon row-mode native-continuation metadata labels so they no
longer report generic `oracle_cpp` labels.

Changed active labels:

- Polygon pair row mode: `native_polygon_pair_exact_rows`.
- Goal877 polygon pair profiler row mode:
  `native_polygon_pair_exact_rows`.
- Goal877 polygon set Jaccard profiler row mode:
  `native_polygon_set_jaccard_exact_rows`.

The Goal877 profiler canonical parity comparison now excludes app diagnostic
contract fields (`generic_area_summary`, `generic_jaccard_summary`, and
`primitive_contract`) that are present in app CPU payloads but not in the
profiler's manually assembled OptiX payload.

## Boundary

- This is metadata/test precision only.
- No public speedup wording is added.
- No new public v1.5 wording is added.
- Summary-mode polygon public boundaries remain unchanged.
- No Vulkan, HIPRT, or Apple RT implementation work is added.

## Local Validation

Commands:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal877_polygon_overlap_optix_phase_profiler_test \
  tests.goal948_polygon_native_continuation_test \
  tests.goal938_public_rtx_wording_sync_test \
  tests.goal1044_public_rtx_cloud_policy_sync_test \
  tests.goal947_v1_rtx_app_status_page_test
PYTHONPATH=src:. python3 -m unittest $(find tests -maxdepth 1 -name 'goal13*_test.py' -exec basename {} .py \; | sed 's/^/tests./')
git diff --check
```

Result:

- Focused tests: 31 tests OK.
- Goal13 sweep: 76 tests OK.
- `git diff --check`: OK.

## Pod Validation

Pending after the source commit is pushed and the pod resets from `origin/main`.
