# Goal956: Segment/Polygon Native-Continuation Metadata

Date: 2026-04-25

## Verdict

Local implementation complete; peer review pending at the time this report was written.

Goal956 closes the remaining metadata gap for segment/polygon and road-hazard app surfaces. It does not promote any new broad RT-core speedup claim. The change makes each app payload explicit about whether the selected path is using an app-visible native continuation, and whether that path is an accepted RT-core-accelerated app claim.

## Scope

Touched apps:

- `examples/rtdl_segment_polygon_hitcount.py`
- `examples/rtdl_segment_polygon_anyhit_rows.py`
- `examples/rtdl_road_hazard_screening.py`

Touched tests/docs:

- `tests/goal956_segment_polygon_native_continuation_metadata_test.py`
- `examples/README.md`

Existing matrix/docs already described the prepared segment/polygon RTX boundary and were verified by focused tests.

## Implementation

`rtdl_segment_polygon_hitcount.py` now reports:

- `native_continuation_active: true` only for `--backend optix --optix-mode native`
- `native_continuation_backend: optix_native_hitcount_gated` for that path
- `rt_core_accelerated: false`

This is intentionally conservative. The app-level native mode is exposed as a gated native hit-count path, but the accepted claim-review scope remains the prepared compact hit-count profiler evidence, not a broad default-app speedup claim.

`rtdl_road_hazard_screening.py` now reports the same conservative gated metadata:

- `native_continuation_active: true` only for `--backend optix --optix-mode native`
- `native_continuation_backend: optix_native_hitcount_gated`
- `rt_core_accelerated: false`

`rtdl_segment_polygon_anyhit_rows.py` now distinguishes the accepted pair-row path from the gated hit-count reuse path:

- `--backend optix --output-mode rows --optix-mode native` reports `native_continuation_backend: optix_native_bounded_pair_rows` and `rt_core_accelerated: true`.
- Compact `segment_flags` / `segment_counts` with `--backend optix --optix-mode native` report `native_continuation_backend: optix_native_hitcount_gated` and `rt_core_accelerated: false`.
- CPU/reference paths report `native_continuation_backend: none`.

## Honesty Boundary

Allowed wording:

- The bounded native OptiX segment/polygon pair-row emitter is an app-visible RT traversal path for explicit rows mode.
- Segment/polygon hit-count and road-hazard native modes are exposed as gated native-continuation metadata.
- Prepared compact hit-count and prepared road-hazard summary artifacts remain the reviewed claim-review surfaces.

Disallowed wording:

- Broad segment/polygon app speedup claim.
- Unbounded pair-row speedup claim.
- Claiming `segment_counts`, `segment_flags`, or road-hazard default app mode as accepted RT-core accelerated paths.
- Full GIS/routing, polygon overlay, or general geometry-engine claims.

## Verification

Focused gate:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal956_segment_polygon_native_continuation_metadata_test \
  tests.goal820_segment_polygon_rt_core_gate_test \
  tests.goal858_segment_polygon_docs_optix_boundary_test \
  tests.goal878_segment_polygon_native_pair_rows_app_surface_test

Ran 16 tests in 0.002s
OK
```

Syntax gate:

```text
python3 -m py_compile \
  examples/rtdl_segment_polygon_hitcount.py \
  examples/rtdl_segment_polygon_anyhit_rows.py \
  examples/rtdl_road_hazard_screening.py \
  tests/goal956_segment_polygon_native_continuation_metadata_test.py
```

Whitespace gate:

```text
git diff --check -- \
  examples/rtdl_segment_polygon_hitcount.py \
  examples/rtdl_segment_polygon_anyhit_rows.py \
  examples/rtdl_road_hazard_screening.py \
  tests/goal956_segment_polygon_native_continuation_metadata_test.py \
  docs/application_catalog.md \
  docs/app_engine_support_matrix.md \
  examples/README.md \
  docs/features/segment_polygon_anyhit_rows/README.md \
  docs/features/segment_polygon_hitcount/README.md \
  src/rtdsl/app_support_matrix.py
```

Both syntax and whitespace gates passed with no output.

## Next Work

Continue the native-continuation cleanup across apps that still expose materialized row-heavy postprocess stages:

- polygon overlap/Jaccard: continue validating native exact-continuation boundaries against cloud artifact diagnostics
- graph analytics: evaluate whether more graph reductions can move behind native summaries without overclaiming full graph-engine support
- ANN / DBSCAN / Barnes-Hut: keep separating RT candidate-generation or threshold-decision paths from Python-owned ranking, clustering, or force reduction
