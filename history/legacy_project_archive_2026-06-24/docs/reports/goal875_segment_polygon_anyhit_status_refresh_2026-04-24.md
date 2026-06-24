# Goal875 Segment/Polygon Any-Hit Status Refresh

- date: `2026-04-24`
- app: `segment_polygon_anyhit_rows`
- status: `public_docs_refreshed`

## Problem

After Goals 872-874, the project had a stale public-facing statement: the docs
and support matrix still said native pair-row output did not exist. That is no
longer precise.

Current correct state:

- Goal872 added an internal native bounded OptiX pair-row emitter.
- Goal873 added the strict RTX gate for that emitter.
- Goal874 added the gate as a deferred cloud-manifest entry.
- The public `segment_polygon_anyhit_rows` rows path is still host-indexed and
  not promoted.

## Work Completed

Updated current public/status sources:

- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `docs/features/segment_polygon_anyhit_rows/README.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `tests/goal858_segment_polygon_docs_optix_boundary_test.py`
- regenerated `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`

## Public Boundary Now Stated

The updated wording separates implementation from promotion:

- Native bounded pair-row emission exists internally.
- Goal873 strict RTX validation is still required.
- The public rows path stays host-indexed until a real RTX artifact proves CPU
  row-digest parity and zero overflow.
- No public RT-core speedup claim is authorized.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal687_app_engine_support_matrix_test tests.goal705_optix_app_benchmark_readiness_test tests.goal803_rt_core_app_maturity_contract_test tests.goal858_segment_polygon_docs_optix_boundary_test tests.goal759_rtx_cloud_benchmark_manifest_test
```

Result: `32 tests OK`.

```text
PYTHONPATH=src:. python3 -m py_compile src/rtdsl/app_support_matrix.py tests/goal858_segment_polygon_docs_optix_boundary_test.py
git diff --check
```

Result: both passed.
