# Goal857 Segment/Polygon OptiX-Mode Perf Surface

Date: 2026-04-23

## Purpose

Goal857 makes the local compact-output perf tooling for the segment/polygon app
family explicitly carry `optix_mode`. Before this change, the scripts could time
the OptiX backend, but they did not record whether a run used the default path,
forced host-indexed fallback, or the experimental native custom-AABB path.

That ambiguity was acceptable for generic local perf exploration, but it is not
acceptable for RT-core promotion work. The segment/polygon family is still
classified as `host_indexed_fallback`, so any local profiling surface used for
future promotion work must make the requested OptiX path explicit.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal726_segment_polygon_compact_summary_perf.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal729_road_hazard_compact_output_perf.py`
- `/Users/rl2025/rtdl_python_only/tests/goal857_segment_polygon_optix_mode_perf_surface_test.py`

## What Changed

### `goal726_segment_polygon_compact_summary_perf.py`

- Added `--optix-mode {auto,host_indexed,native}`.
- The `run(...)` helper now accepts `optix_mode`.
- The script propagates `optix_mode` into both:
  - `rows` execution
  - `segment_counts` execution
- The emitted payload now records:
  - top-level `optix_mode`
  - per-case `optix_mode`

### `goal729_road_hazard_compact_output_perf.py`

- Added `--optix-mode {auto,host_indexed,native}`.
- The `run(...)` helper now accepts `optix_mode`.
- The script propagates `optix_mode` into both:
  - `rows` execution
  - `priority_segments` execution
- The emitted payload now records:
  - top-level `optix_mode`
  - per-case `optix_mode`

## Boundary

This change does **not** promote the segment/polygon family into an active RTX
claim set. It only makes local profiling artifacts honest and replayable.

It still does **not** claim:

- public RT-core speedup for `segment_polygon_hitcount`
- public RT-core speedup for `segment_polygon_anyhit_rows`
- public RT-core speedup for `road_hazard_screening`
- pair-row native OptiX output for `segment_polygon_anyhit_rows`
- whole-app road-hazard OptiX acceleration

## Why This Matters

The next RT step for this family is a focused native-vs-host-indexed promotion
review. Without explicit mode recording, later numbers are not auditable because
an `optix` run alone does not tell the reviewer which implementation path was
actually exercised.

Goal857 fixes that instrumentation gap without changing the public honesty
boundary.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal857_segment_polygon_optix_mode_perf_surface_test \
  tests.goal726_segment_polygon_compact_summary_test \
  tests.goal729_road_hazard_compact_output_test \
  tests.goal820_segment_polygon_rt_core_gate_test
```

Result:

```text
Ran 12 tests in 0.184s
OK
```

Additional local checks:

```text
python3 -m py_compile \
  scripts/goal726_segment_polygon_compact_summary_perf.py \
  scripts/goal729_road_hazard_compact_output_perf.py \
  tests/goal857_segment_polygon_optix_mode_perf_surface_test.py

git diff --check
```

Both passed.

## Verdict

Goal857 is complete locally. It is a tooling and auditability improvement for
the segment/polygon OptiX promotion path, not a promotion itself.
