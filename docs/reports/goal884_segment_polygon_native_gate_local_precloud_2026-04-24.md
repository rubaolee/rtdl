# Goal884 Segment/Polygon Native OptiX Gate Local Pre-Cloud Report

Date: 2026-04-24

## Result

Goal884 records the local segment/polygon native OptiX promotion gate before
the next paid RTX pod run.

Local non-strict gate:

```bash
PYTHONPATH=src:. python3 scripts/goal807_segment_polygon_optix_mode_gate.py \
  --dataset authored_segment_polygon_minimal \
  --output-json docs/reports/goal884_segment_polygon_gate_local_non_strict_2026-04-24.json
```

Result: `non_strict_recorded_gaps`.

Local strict gate:

```bash
PYTHONPATH=src:. python3 scripts/goal807_segment_polygon_optix_mode_gate.py \
  --dataset authored_segment_polygon_minimal \
  --strict \
  --output-json docs/reports/goal884_segment_polygon_gate_local_strict_2026-04-24.json
```

Result: `fail`, with the expected local failures:

- `optix_host_indexed did not run`
- `optix_native did not run`

Both OptiX paths failed locally only because `librtdl_optix` is unavailable on
this macOS host:

```text
FileNotFoundError: librtdl_optix not found. Build it with 'make build-optix' or set RTDL_OPTIX_LIB=/path/to/lib.
```

The CPU Python reference path ran successfully and provides the local reference
digest for the next RTX host gate.

## Boundary

This is a local pre-cloud readiness artifact. It is not a segment/polygon
promotion claim and not a speedup claim.

Short form: not a segment/polygon promotion claim.

The result means:

- The gate logic is healthy enough to record local CPU reference evidence.
- The strict promotion gate cannot be satisfied on this macOS host because the
  native OptiX library is not present.
- A real RTX Linux host must build `librtdl_optix` and rerun the same gate
  before segment/polygon native OptiX can be promoted.

## Pre-Cloud Readiness

The broader pre-cloud readiness gate was refreshed after Goals879-883 and
remains valid:

```bash
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal884_pre_cloud_readiness_after_goal879_883_2026-04-24.json
```

Result: `valid: true`.

The readiness gate preserves the cloud-cost policy: start one RTX pod only
after local source edits, docs, manifests, dry-runs, and review packets are
ready, then run the consolidated cloud batch.

## Next Cloud Action

When the pod is available, run the one-shot RTX flow first for active manifest
entries. Then run the focused segment/polygon native gate with `librtdl_optix`
built on the host. Do not restart the pod per app.

## Verification

Focused local tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal807_segment_polygon_optix_mode_gate_test \
  tests.goal808_segment_polygon_app_native_mode_propagation_test
```

Result: `8 tests OK`.

Goal884 report test:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal884_segment_polygon_precloud_gate_report_test
```

Expected result: `OK`.
