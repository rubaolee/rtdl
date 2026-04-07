# Goal 129: Generate-Only Second Workload Expansion

Date: 2026-04-06
Status: accepted

## Goal

Take the existing narrow generate-only line and extend it to the newly closed
second workload family:

- `segment_polygon_anyhit_rows`

This goal counts only if the result is:

- runnable
- verified against `cpu_python_reference`
- exposed through the same generate-only product surface
- still narrow and disciplined

It does **not** count as success if it expands generate-only mode into a broad
multi-workload sprawl.

## Required outcomes

1. add `segment_polygon_anyhit_rows` to the supported generate-only workload set
2. extend the CLI to request that workload directly
3. add focused tests for the generated any-hit program and handoff bundle
4. publish one worked generated bundle example

## Final outcome

Goal 129 is now closed as a narrow generate-only expansion:

- `segment_polygon_hitcount` remains supported
- `segment_polygon_anyhit_rows` is now also supported

The generated any-hit program:

- emits `segment_id, polygon_id` rows
- can run in `summary` or `rows` mode
- can verify itself against `cpu_python_reference`
- is available as a tracked handoff bundle under `examples/`

So the generate-only line is now stronger than Goals 111 and 113 without
changing its narrow product boundary.
