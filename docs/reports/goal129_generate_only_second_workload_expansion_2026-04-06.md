# Goal 129 Report: Generate-Only Second Workload Expansion

Date: 2026-04-06
Status: accepted

## Summary

Goals 111 and 113 proved that RTDL's generate-only mode was worth keeping, but
only for one workload family:

- `segment_polygon_hitcount`

Goal 129 extends that same narrow product surface to the newly closed second
workload family:

- `segment_polygon_anyhit_rows`

## Code changes

Updated:

- `src/rtdsl/generate_only.py`
- `scripts/rtdl_generate_only.py`

Added:

- `tests/goal129_generate_only_second_workload_test.py`
- `examples/rtdl_generated_segment_polygon_anyhit_bundle/README.md`
- `examples/rtdl_generated_segment_polygon_anyhit_bundle/request.json`
- `examples/rtdl_generated_segment_polygon_anyhit_bundle/generated_segment_polygon_anyhit_rows_cpu_python_reference_authored_segment_polygon_minimal.py`

## What changed

The generate-only system now supports:

- `segment_polygon_hitcount`
- `segment_polygon_anyhit_rows`

The new any-hit generator path:

- emits a runnable RTDL Python file
- builds the accepted deterministic datasets
- runs on:
  - `cpu_python_reference`
  - `cpu`
  - `embree`
  - `optix`
- verifies against `cpu_python_reference` when requested
- supports both:
  - `rows`
  - `summary`

The CLI now accepts:

```bash
python3 scripts/rtdl_generate_only.py \
  --workload segment_polygon_anyhit_rows \
  --dataset authored_segment_polygon_minimal \
  --backend cpu_python_reference \
  --output-mode summary \
  --artifact-shape handoff_bundle \
  --output build/goal129_anyhit_bundle
```

## Validation

Focused generate-only regression:

- `PYTHONPATH=src:. python3 -m unittest tests.goal111_generate_only_mvp_test tests.goal113_generate_only_maturation_test tests.goal129_generate_only_second_workload_test`
  - `10` tests
  - `OK`
  - `2` skipped
  - same existing local Mac `geos_c` linker noise appears before the skipped cases

Generated bundle run:

- `PYTHONPATH=src:. python3 examples/rtdl_generated_segment_polygon_anyhit_bundle/generated_segment_polygon_anyhit_rows_cpu_python_reference_authored_segment_polygon_minimal.py`
  - result:
    - `workload: segment_polygon_anyhit_rows`
    - `backend: cpu_python_reference`
    - `row_count: 2`
    - `verified_against_cpu_python_reference: true`

## Product reading

This is a real improvement, but still a narrow one.

Goal 129 does **not** claim:

- broad general code generation
- many-workload generator coverage
- arbitrary backend/package scaffolding

It only claims:

- the generate-only line now covers a second real v0.2 workload family
- with the same runnable handoff-bundle style that survived Goals 111 and 113

So Goal 129 strengthens the kept generate-only feature without letting it turn
into shallow template sprawl.
