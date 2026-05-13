# Goal1897 - Road Hazard Prepared Reuse Pod Packet

Status: pre-pod-ready

Date: 2026-05-13

## Scope

Goal1897 adds a one-command RTX pod packet for the Goal1889 road-hazard
prepared partner-device reuse row.

Runner:

`scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh`

The packet records environment details, checks partner frameworks, builds
OptiX, runs focused tests, generates the two required Goal1889 pod artifacts,
and validates claim-boundary fields before completing.

## Default Pod Command

```bash
OUT_DIR=docs/reports/goal1897_road_hazard_prepared_reuse_pod \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh
```

Default artifact outputs:

- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1897_road_hazard_prepared_reuse_pod_summary.json`

## Local Dry Run

For mechanics-only local Linux checks on the GTX 1070 host, set:

```bash
REQUIRE_RTX=0 COUNTS="64" ITERATIONS=2 PARTNERS=torch \
OPTIX_PREFIX=/home/lestat/vendor/optix-dev \
PYTHONPATH=/tmp/rtdl_v2_partner_pydeps \
bash scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh
```

`REQUIRE_RTX=0` must not be used for accepted RTX evidence.

Codex ran this mechanics-only dry run on `192.168.1.20` with:

```bash
OUT_DIR=/tmp/goal1897_dryrun \
REQUIRE_RTX=0 \
COUNTS="64" \
ITERATIONS=2 \
PARTNERS=torch \
THRESHOLD=2 \
OPTIX_PREFIX=/home/lestat/vendor/optix-dev \
PYTHONPATH=/tmp/rtdl_v2_partner_pydeps \
RTDL_SOURCE_COMMIT_LABEL=9f584e11f3f246c6ea1189b235fd9923e0cf3237 \
bash scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh
```

Dry-run result:

- OptiX build passed.
- Focused tests passed: 14 tests.
- One mechanics artifact was generated for count 64 and partner `torch`.
- Summary showed prepared reuse faster than the unprepared partner row for that
  local dry run, but slower than v1.8 prepared native on GTX 1070.

Dry-run summary:

| Count | Partner | Unprepared median (s) | Prepared median (s) | Prepared/unprepared ratio | Prepared/v1.8 prepared ratio |
| ---: | --- | ---: | ---: | ---: | ---: |
| 64 | Torch | 0.1093116635 | 0.0009805606 | 0.009x | 2.335x |

The two-iteration dry run is intentionally not used for performance claims; it
only proves the packet mechanics.

## Claim Boundary

This packet does not authorize v2.0 release readiness, whole-app speedup,
broad RT-core speedup, package-install support, or arbitrary PyTorch/CuPy
acceleration claims.

The runner refuses accepted pod mode on a non-RTX GPU. Local dry runs are
development evidence only.
