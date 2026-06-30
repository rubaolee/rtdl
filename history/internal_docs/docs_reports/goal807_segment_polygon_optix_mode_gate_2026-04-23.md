# Goal807 Segment/Polygon OptiX Native-Mode Gate

## Result

Goal807 adds a replayable gate for the `segment_polygon_hitcount` OptiX native-mode candidate.

This goal does not promote segment/polygon to an NVIDIA RT-core app claim. It creates the missing harness needed before promotion can be considered.

## What Changed

- Added `/Users/rl2025/rtdl_python_only/scripts/goal807_segment_polygon_optix_mode_gate.py`.
- Added `/Users/rl2025/rtdl_python_only/tests/goal807_segment_polygon_optix_mode_gate_test.py`.
- Updated `/Users/rl2025/rtdl_python_only/scripts/goal759_rtx_cloud_benchmark_manifest.py` so the deferred segment/polygon RTX candidate points at the Goal807 gate rather than a raw app invocation.
- The gate compares:
  - CPU Python reference.
  - OptiX host-indexed mode through `--optix-mode host_indexed`.
  - OptiX native custom-AABB mode through `--optix-mode native`.
  - Optional PostGIS baseline when `--include-postgis` is supplied.
- The gate writes JSON containing status, per-path timing, row digests, parity against CPU reference, and strict failures.

## Intended Cloud Command

```bash
PYTHONPATH=src:. python3 scripts/goal807_segment_polygon_optix_mode_gate.py \
  --dataset derived/br_county_subset_segment_polygon_tiled_x256 \
  --include-postgis \
  --strict \
  --output-json docs/reports/goal807_segment_polygon_optix_mode_gate_rtx.json
```

If PostGIS is not installed on the RTX host, rerun without `--include-postgis` and keep the resulting report bounded as CPU-reference parity only.

## Activation Rule

`segment_polygon_hitcount` can only move from deferred RTX candidate to active RTX benchmark target after:

- `optix_native` runs successfully.
- `optix_host_indexed` runs successfully.
- Both OptiX paths match the CPU Python reference row digest.
- PostGIS parity is recorded where PostGIS is available.
- An independent review accepts the native-mode correctness and timing evidence.

## Boundary

This is a readiness and replayability goal. It does not authorize a public NVIDIA RT-core speedup claim.

## Local Verification

Completed locally:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal807_segment_polygon_optix_mode_gate_test tests.goal806_segment_polygon_optix_mode_surface_test tests.goal759_rtx_cloud_benchmark_manifest_test -v
python3 -m py_compile scripts/goal807_segment_polygon_optix_mode_gate.py tests/goal807_segment_polygon_optix_mode_gate_test.py
git diff --check
```

Result: 12 tests OK, `py_compile` OK, and `git diff --check` OK.

Local non-strict run:

```bash
PYTHONPATH=src:. python3 scripts/goal807_segment_polygon_optix_mode_gate.py \
  --dataset authored_segment_polygon_minimal \
  --output-json docs/reports/goal807_segment_polygon_optix_mode_gate_local_2026-04-23.json
```

Result: `non_strict_recorded_gaps`, because this Mac does not have `librtdl_optix` built/available. CPU reference completed and both OptiX paths were recorded as unavailable. This is expected local evidence, not an RTX result.
