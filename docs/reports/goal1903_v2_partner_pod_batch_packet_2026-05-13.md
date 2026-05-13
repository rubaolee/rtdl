# Goal1903 - v2 Partner Pod Batch Packet

Status: pre-pod-ready

Date: 2026-05-13

## Scope

Goal1903 adds a batch runner for high-value RTX pod sessions:

`scripts/goal1903_v2_partner_pod_batch_runner.sh`

The runner is designed for multi-head pod use. It can run:

- fixed-radius app rows through `scripts/goal1878_fixed_radius_app_adapter_perf.py`;
- segment/polygon hitcount rows through
  `scripts/goal1863_segment_polygon_hitcount_v2_partner_perf.py`;
- road-hazard priority rows through the Goal1897 packet.

## Default Pod Command

```bash
OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1903_v2_partner_pod_batch_runner.sh
```

Default accepted-mode outputs:

- `docs/reports/goal1903_fixed_radius_batch_pod.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_512.json`
- `docs/reports/goal1903_segment_polygon_batch_pod_2048.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1903_v2_partner_pod_batch_summary.json`

The runner clears only this run's target artifact paths before execution and
builds the summary from the requested counts, not from a broad filesystem glob,
so stale pod JSON cannot be swept into a new evidence packet.

## Local Dry Run

For mechanics-only local Linux dry runs, use only the road-hazard head:

```bash
OUT_DIR=/tmp/goal1903_dryrun \
REQUIRE_RTX=0 \
RUN_FIXED_RADIUS=0 \
RUN_SEGMENT_POLYGON=0 \
RUN_ROAD_HAZARD=1 \
ROAD_HAZARD_COUNTS="64" \
ROAD_HAZARD_ITERATIONS=2 \
ROAD_HAZARD_PARTNERS=torch \
OPTIX_PREFIX=/home/lestat/vendor/optix-dev \
PYTHONPATH=/tmp/rtdl_v2_partner_pydeps \
bash scripts/goal1903_v2_partner_pod_batch_runner.sh
```

`REQUIRE_RTX=0` is local mechanics-only and must not be used for accepted RTX evidence.

Codex ran the local dry-run on `192.168.1.20` with:

```bash
OUT_DIR=/tmp/goal1903_dryrun \
REQUIRE_RTX=0 \
RUN_FIXED_RADIUS=0 \
RUN_SEGMENT_POLYGON=0 \
RUN_ROAD_HAZARD=1 \
ROAD_HAZARD_COUNTS="64" \
ROAD_HAZARD_ITERATIONS=2 \
ROAD_HAZARD_PARTNERS=torch \
ROAD_HAZARD_THRESHOLD=2 \
OPTIX_PREFIX=/home/lestat/vendor/optix-dev \
PYTHONPATH=/tmp/rtdl_v2_partner_pydeps \
RTDL_SOURCE_COMMIT_LABEL=13275c462af5eadfb624b287a937d8af00d13e51 \
bash scripts/goal1903_v2_partner_pod_batch_runner.sh
```

Dry-run result:

- OptiX build passed.
- Shared focused tests passed: 16 tests.
- Goal1897 nested road-hazard packet passed: 14 tests.
- One mechanics artifact was generated for count 64 and partner `torch`.
- Batch summary was written to `/tmp/goal1903_dryrun/summary.json`.

Dry-run summary:

| Head | Requested | Local result |
| --- | --- | --- |
| fixed-radius | false | skipped by dry-run config |
| segment/polygon | false | skipped by dry-run config |
| road-hazard | true | pass, count 64, Torch only |

This dry-run proves batch orchestration only. It is not accepted RTX evidence.

## Boundary

The batch runner collects evidence. It does not by itself authorize v2.0 release
readiness, whole-app speedup, broad RT-core speedup, package-install support, or
arbitrary PyTorch/CuPy acceleration claims.
