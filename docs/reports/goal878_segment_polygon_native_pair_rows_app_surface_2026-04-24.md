# Goal878 Segment/Polygon Native Pair-Row App Surface

Date: 2026-04-24

## Result

Goal878 exposes the Goal873 bounded native OptiX pair-row emitter through the
public `segment_polygon_anyhit_rows` app:

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py \
  --backend optix \
  --output-mode rows \
  --optix-mode native \
  --output-capacity 1000000
```

For claim-sensitive runs, the accepted narrow path is:

```bash
PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py \
  --backend optix \
  --output-mode rows \
  --optix-mode native \
  --require-rt-core \
  --output-capacity 1000000
```

## Boundary

This is an app-surface promotion of a native traversal path, not a speedup
claim. The path is bounded: callers provide `--output-capacity`, and overflow
raises instead of truncating rows. Promotion to a performance claim still
requires the Goal873 strict RTX artifact: CPU row-digest parity, zero overflow,
RTX hardware metadata, and independent review.

Default `--optix-mode auto` remains conservative. The app matrix records OptiX
as exposed because the explicit native mode is now public, while the OptiX
performance class remains `host_indexed_fallback` to prevent default-path
overclaiming.

## Changed Files

- `src/rtdsl/optix_runtime.py`: added
  `segment_polygon_anyhit_rows_native_bounded_optix(...)`.
- `src/rtdsl/__init__.py`: exported the helper.
- `examples/rtdl_segment_polygon_anyhit_rows.py`: wired explicit
  `--backend optix --output-mode rows --optix-mode native` to the bounded native
  emitter and added `--output-capacity`.
- `src/rtdsl/app_support_matrix.py` and `docs/app_engine_support_matrix.md`:
  updated support/readiness/maturity state.
- `docs/application_catalog.md`, `docs/features/segment_polygon_anyhit_rows/README.md`,
  `docs/tutorials/segment_polygon_workloads.md`, and `examples/README.md`:
  documented the new explicit mode and claim boundary.
- `scripts/goal515_public_command_truth_audit.py` and
  `tests/goal824_pre_cloud_rtx_readiness_gate_test.py`: refreshed public
  command coverage and current deferred manifest counts after this app-surface
  promotion.
- Tests updated/added for native app-surface behavior and documentation sync.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal878_segment_polygon_native_pair_rows_app_surface_test \
  tests.goal808_segment_polygon_app_native_mode_propagation_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal707_app_rt_core_redline_audit_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal858_segment_polygon_docs_optix_boundary_test
```

Result: `33 tests OK`.

Broader matrix/manifest gate:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal878_segment_polygon_native_pair_rows_app_surface_test \
  tests.goal808_segment_polygon_app_native_mode_propagation_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal707_app_rt_core_redline_audit_test \
  tests.goal687_app_engine_support_matrix_test \
  tests.goal690_optix_performance_classification_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal803_rt_core_app_maturity_contract_test \
  tests.goal858_segment_polygon_docs_optix_boundary_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal822_rtx_cloud_manifest_claim_boundary_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `60 tests OK`.

Public command audit after doc changes: `valid=True`.

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/optix_runtime.py \
  src/rtdsl/__init__.py \
  examples/rtdl_segment_polygon_anyhit_rows.py \
  tests/goal878_segment_polygon_native_pair_rows_app_surface_test.py
```

Result: OK.

```bash
git diff --check
```

Result: OK.
