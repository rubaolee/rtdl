# Goal 799 Segment/Polygon OptiX Local Readiness Audit

Date: 2026-04-23

Status: local-first cloud-cost gate complete

## Purpose

This goal audits whether the segment/polygon application family should enter
the next paid NVIDIA RTX cloud run.

The answer is **not yet as an active benchmark entry**.

## Files Checked

- `/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_hitcount.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_segment_polygon_anyhit_rows.py`
- `/Users/rl2025/rtdl_python_only/examples/rtdl_road_hazard_screening.py`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_workloads.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/optix/rtdl_optix_api.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/app_support_matrix.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal761_rtx_cloud_run_all.py`
- `/Users/rl2025/rtdl_python_only/tests/goal761_rtx_cloud_run_all_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal692_optix_app_correctness_transparency_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal705_optix_app_benchmark_readiness_test.py`

## Findings

`segment_polygon_hitcount` has two OptiX implementation paths:

- default path: host-indexed fallback;
- explicit native path: enabled only when `RTDL_OPTIX_SEGPOLY_MODE=native`.

The native path builds polygon AABB acceleration and launches the OptiX
`__raygen__segpoly_probe`, `__intersection__segpoly_isect`, and
`__anyhit__segpoly_anyhit` pipeline. It is real OptiX traversal, but it is not
the public default.

`segment_polygon_anyhit_rows` remains host-indexed in the current OptiX API.
It does not have a promoted native any-hit rows path today.

The older Goal 120 evidence remains important: the native hit-count path was
correct, but did not produce a meaningful performance win and remained much
slower than PostGIS for large rows. Therefore it should not consume cloud time
as a default benchmark unless we are explicitly measuring the experimental
native path against host-indexed and PostGIS baselines.

## Changes Made

`/Users/rl2025/rtdl_python_only/scripts/goal761_rtx_cloud_run_all.py` now
supports per-entry `env` overrides from the manifest and includes those
overrides in each command result. The command cache key includes both the
command and the environment overrides, preventing accidental reuse across
different runtime modes.

`/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py`
now records a deferred segment/polygon native candidate:

- path name: `segment_polygon_hitcount_native_experimental`;
- env: `RTDL_OPTIX_SEGPOLY_MODE=native`;
- status: deferred, not in active `entries`;
- activation gate: only promote after a focused native-vs-host-indexed-vs-PostGIS
  correctness/performance harness passes on RTX hardware and the readiness
  matrix is updated.

## Verification

Local focused tests:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal705_optix_app_benchmark_readiness_test \
  tests.goal692_optix_app_correctness_transparency_test
```

Result:

- `18` tests;
- `OK`.

Compile check:

```bash
cd /Users/rl2025/rtdl_python_only
python3 -m py_compile \
  scripts/goal759_rtx_cloud_benchmark_manifest.py \
  scripts/goal761_rtx_cloud_run_all.py \
  tests/goal761_rtx_cloud_run_all_test.py
```

Result:

- `OK`.

Manifest refresh:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal759_rtx_cloud_benchmark_manifest.py \
  > docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json
```

Dry-run guard:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --only segment_polygon_hitcount \
  --output-json docs/reports/goal799_segment_polygon_not_active_dry_run_2026-04-23.json
```

Result:

- `entry_count: 0`;
- `unique_command_count: 0`;
- `status: ok`.

This proves the deferred native segment/polygon candidate is documented but not
accidentally included in the paid cloud benchmark batch.

## Release Boundary

This goal does not promote segment/polygon to an RTX app-speedup claim.

Allowed statement:

- RTDL has an explicit experimental native OptiX hit-count path for
  segment/polygon behind `RTDL_OPTIX_SEGPOLY_MODE=native`, and the cloud runner
  can now record such env-gated commands reproducibly.

Disallowed statements:

- segment/polygon is now an active RTX benchmark candidate;
- segment/polygon any-hit rows are native OptiX traversal today;
- segment/polygon has demonstrated RTX speedup;
- road hazard screening has demonstrated RTX speedup.

## Next Step

The next local-first app-performance pass should audit graph OptiX in the same
style: identify whether a hidden native path exists, decide whether it is
promotable, and only add it to a paid cloud batch after a clear local readiness
gate exists.
