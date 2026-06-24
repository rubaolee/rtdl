# Goal 127 Report: Second Workload Family Any-Hit Rows Closure

Date: 2026-04-06
Status: accepted locally

## Summary

Goal 126 selected `segment_polygon_anyhit_rows` as the second v0.2 workload
family. This report closes the first real implementation package for that
family.

The new family emits:

- one `(segment_id, polygon_id)` row per true segment/polygon hit

instead of:

- one `(segment_id, hit_count)` row per segment

This makes it a distinct emitted workload family built on the same
segment/polygon geometric core as `segment_polygon_hitcount`.

## What was added

- new predicate:
  - `rt.segment_polygon_anyhit_rows(exact=False)`
- new Goal 10 reference kernel:
  - `segment_polygon_anyhit_rows_reference`
- Python reference execution support
- oracle/native runtime support for:
  - CPU oracle
  - Embree
  - OptiX
  - Vulkan
- baseline-contract and evaluation-matrix registration
- user-facing example:
  - `examples/rtdl_segment_polygon_anyhit_rows.py`

## Validation

Local validation completed:

- `python3 -m py_compile ...` over the updated Python surface: passed
- `PYTHONPATH=src:. python3 -m unittest tests.goal10_workloads_test tests.baseline_contracts_test tests.rtdsl_language_test tests.test_core_quality`
  - result:
    - `105` tests
    - `OK`
    - `1` skipped
- `PYTHONPATH=src:. python3 examples/rtdl_segment_polygon_anyhit_rows.py --backend cpu_python_reference --dataset authored_segment_polygon_minimal`
  - result:
    - `row_count: 2`

Representative authored rows:

- `(segment_id=1, polygon_id=10)`
- `(segment_id=2, polygon_id=11)`

## Current boundary

This goal closes the family on the local code surface, but one environment
limit remains on this Mac:

- native CPU/oracle builds still hit the existing missing `geos_c` linker
  dependency here

So the accepted local closure is strongest on:

- lowering
- schema validation
- Python reference execution
- authored runtime parity tests where the environment permits them

## Conclusion

`segment_polygon_anyhit_rows` is now a real RTDL workload family in the codebase.

It is not merely selected in a roadmap anymore. It has:

- predicate surface
- lowering surface
- runtime bindings
- baseline coverage
- language/test coverage
- a user-facing runnable example
