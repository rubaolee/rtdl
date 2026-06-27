# Gemini Task: Review Goal2139 Public Geo Hausdorff Evidence

Please perform an independent read-only review and write the result to:

`docs/reviews/goal2140_gemini_review_goal2139_public_geo_hd_perf_2026-05-16.md`

## Context

Goal2139 extends the RTDL/OptiX exact 2D projected-point Hausdorff benchmark beyond graphics models into public geo data. The original X-HD scripts use local WKT files for county/zipcode/lakes/parks-style inputs. The exact WKT files are not in this repository, so Goal2139 uses reproducible public shapefile analogues:

- Census TIGER/Line 2023 counties vs Census TIGER/Line 2023 ZCTA boundaries.
- Natural Earth 1:10m lakes vs Natural Earth parks/protected lands.

The benchmark converts shapefile vertices into normalized lon/lat point sets, then compares grouped CuPy against the RTDL/OptiX X-HD-style seeded-pruned path. The engine must remain app-agnostic: generic point-group threshold traversal and nearest-witness reduction only, with Hausdorff policy in Python.

## Files To Review

- `scripts/goal2126_public_hausdorff_dataset_perf.py`
- `tests/goal2138_public_geo_harness_test.py`
- `docs/reports/goal2139_public_geo_hausdorff_perf_2026-05-16.md`
- `docs/reports/goal2139_public_geo_pod_a5000/*.json`
- `tests/goal2139_public_geo_hausdorff_perf_test.py`

## Review Questions

1. Does the harness add a bounded, streaming public-geo loader without changing the native engine?
2. Do the artifacts support the stated source scale, especially the Census/ZCTA 8.2M / 51.2M source-vertex finding?
3. Do all rows preserve correctness against grouped CuPy within the artifact/test boundary?
4. Is the performance conclusion accurate and nuanced: detailed Census rows are strong RTDL wins, sparse Natural Earth rows are only modest wins/near-parity?
5. Are the boundaries conservative: no original X-HD WKT reproduction, no full geographic polygon/surface Hausdorff semantics, no MRI/BraTS reproduction, no v2.0 release authorization?

## Required Verdict Format

Use only: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please include per-question verdicts, concrete issues if any, final overall verdict, and an explicit statement that this is an independent Gemini review distinct from Codex.
