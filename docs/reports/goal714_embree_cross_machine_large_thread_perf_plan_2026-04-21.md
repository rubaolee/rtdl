# Goal 714: Embree Cross-Machine Large Thread Performance Harness

Date: 2026-04-21

Status: implementation in progress

## Purpose

Goal 714 prepares the Linux and Windows large-scale multithreaded Embree app
performance run requested after Goal 713.

The needed artifact is not another smoke app gate. It is a repeatable harness
that can run on Linux and Windows, sweep `RTDL_EMBREE_THREADS`, check
CPU-reference parity, and record honest app-level wall-clock timing.

## Harness

Script:

- `/Users/rl2025/rtdl_python_only/scripts/goal714_embree_app_thread_perf.py`

Focused harness test:

- `/Users/rl2025/rtdl_python_only/tests/goal714_embree_app_thread_perf_test.py`

The harness records:

- host platform, CPU count, Python version;
- selected app group and app name;
- copy scale for apps that expose `--copies`;
- CPU-reference canonical output hash;
- Embree canonical output hash for each thread setting;
- `RTDL_EMBREE_THREADS` requested value and effective thread count;
- repeat count, median/min/max/sample wall-clock seconds;
- speedup versus `threads=1` when a one-thread baseline is included.

## Honesty Boundary

These are whole-app CLI timings. They include Python startup, JSON
materialization, and app postprocess. They are not pure native Embree traversal
phase timings.

For apps with `direct_cli_native_assisted` support, such as polygon overlap and
Jaccard after Goal 713, only the candidate-discovery phase is Embree-backed;
exact area/Jaccard refinement remains CPU/Python.

## Intended Remote Runs

Linux:

```sh
PYTHONPATH=src:. python3 scripts/goal714_embree_app_thread_perf.py \
  --host-label linux-lx1 \
  --groups spatial_point,segment_polygon,polygon_overlap,ray,db,graph \
  --copies 1024 \
  --threads 1,2,4,8,auto \
  --min-sample-sec 2 \
  --max-repeats 10 \
  --output docs/reports/goal714_embree_app_thread_perf_linux_2026-04-21.json
```

Windows:

```bat
set PYTHONPATH=src;.
py -3 scripts\goal714_embree_app_thread_perf.py ^
  --host-label windows-32thread ^
  --groups spatial_point,segment_polygon,polygon_overlap,ray,db,graph ^
  --copies 1024 ^
  --threads 1,2,4,8,16,32,auto ^
  --min-sample-sec 2 ^
  --max-repeats 10 ^
  --output docs\reports\goal714_embree_app_thread_perf_windows_2026-04-21.json
```

The first remote run may reduce copies or groups if a host times out. Any such
reduction must be recorded in the final report.
