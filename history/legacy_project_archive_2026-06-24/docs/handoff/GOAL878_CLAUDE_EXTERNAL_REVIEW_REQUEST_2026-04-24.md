# Goal878 Claude External Review Request

Please independently review Goal878 and write a verdict to
`docs/reports/goal878_claude_external_review_2026-04-24.md`.

Review these files:

- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/__init__.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `src/rtdsl/app_support_matrix.py`
- `docs/app_engine_support_matrix.md`
- `docs/application_catalog.md`
- `docs/features/segment_polygon_anyhit_rows/README.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `examples/README.md`
- `tests/goal878_segment_polygon_native_pair_rows_app_surface_test.py`
- `tests/goal808_segment_polygon_app_native_mode_propagation_test.py`
- `tests/goal820_segment_polygon_rt_core_gate_test.py`
- `tests/goal707_app_rt_core_redline_audit_test.py`
- `tests/goal705_optix_app_benchmark_readiness_test.py`
- `tests/goal858_segment_polygon_docs_optix_boundary_test.py`
- `docs/reports/goal878_segment_polygon_native_pair_rows_app_surface_2026-04-24.md`

Questions:

- Does the public app now correctly route
  `--backend optix --output-mode rows --optix-mode native` through the bounded
  native OptiX pair-row emitter instead of the host-indexed fallback?
- Is the `--output-capacity` overflow policy honest and safe enough for a
  public explicit native mode?
- Do the docs avoid claiming speedup before Goal873 strict RTX artifact review?
- Are the support/readiness/maturity matrix changes conservative and
  internally consistent?

Return `ACCEPT` or `BLOCK` with concrete blockers if any.
