# Goal874 RTX Manifest Native Pair-Row Gate Refresh

- date: `2026-04-24`
- parent work: `Goal872`, `Goal873`
- status: `local_manifest_refresh_complete`

## Work Completed

Goal874 wires the new native bounded `segment_polygon_anyhit_rows` OptiX gate
into the RTX cloud benchmark manifest as a deferred readiness gate.

Changes:

- Updated `scripts/goal759_rtx_cloud_benchmark_manifest.py`.
- Regenerated
  `docs/reports/goal759_rtx_cloud_benchmark_manifest_2026-04-22.json`.
- Updated `tests/goal759_rtx_cloud_benchmark_manifest_test.py`.

## Manifest Semantics

The new deferred entry is:

- app: `segment_polygon_anyhit_rows`
- path: `segment_polygon_anyhit_rows_native_bounded_gate`
- command:

```text
python3 scripts/goal873_native_pair_row_optix_gate.py --dataset authored_segment_polygon_minimal --output-capacity 1024 --strict --output-json docs/reports/goal873_native_pair_row_optix_gate_rtx_strict.json
```

It is intentionally deferred, not active. The reason is that the public rows
path is still host-indexed, and the native bounded device-emission path must
first pass a real Linux/RTX strict artifact.

## Baseline Contract

The manifest now gives `segment_polygon_anyhit_rows` a specific baseline
review contract:

- `cpu_python_reference`
- `optix_native_bounded_pair_rows`
- `postgis_when_available_for_same_pair_semantics`

Required phases/evidence:

- `records`
- `row_digest`
- `emitted_count`
- `copied_count`
- `overflowed`
- `strict_pass`
- `strict_failures`
- `status`

## Boundary

Goal874 does not promote `segment_polygon_anyhit_rows` into an active RTX app
benchmark. It only ensures the next cloud session can include the strict gate
with `--include-deferred` or `--only segment_polygon_anyhit_rows`.

No public RT-core claim is authorized until the strict RTX artifact passes and
is independently reviewed.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest tests.goal759_rtx_cloud_benchmark_manifest_test tests.goal873_native_pair_row_optix_gate_test
```

Result: `16 tests OK`.

```text
PYTHONPATH=src:. python3 -m py_compile scripts/goal759_rtx_cloud_benchmark_manifest.py tests/goal759_rtx_cloud_benchmark_manifest_test.py
git diff --check
```

Result: both passed.
