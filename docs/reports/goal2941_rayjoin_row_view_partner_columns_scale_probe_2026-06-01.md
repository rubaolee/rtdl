# Goal2941: RayJoin Row-View Partner-Column Scale Probe

Date: 2026-06-01
Status: pod scale probe passed

## Purpose

Goal2941 adds a scale-aware Spatial RayJoin probe for the Goal2938 typed
row-view bridge. It uses the deterministic RayJoin-style scale cases from the
existing Goal2147 harness, but compares:

- prepared count-only query; and
- prepared raw rows converted into partner-owned typed columns through
  `rt.optix_row_view_to_partner_columns`.

This is designed to measure the cost and usefulness of typed primitive payload
columns before the future device-resident row-stream work.

## Script

`scripts/goal2941_rayjoin_row_view_partner_columns_scale_probe.py`

Example:

```text
PYTHONPATH=src:. python3 scripts/goal2941_rayjoin_row_view_partner_columns_scale_probe.py \
  --scale large --partner cupy --warmups 1 --repeats 5 \
  --output /tmp/goal2941_rayjoin_row_view_partner_columns_large.json
```

## Pod Result

Artifact:

`docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_pod/goal2941_rayjoin_row_view_partner_columns_large.json`

- source commit: `b480901e45a0c47353da244b94642d3c6fdd81de`
- source dirty: `[]`
- GPU: `NVIDIA RTX A5000, 570.211.01`
- partner: `cupy`
- scale: `large`

| Workload | Row count | Count-only median sec | Typed CuPy columns median sec | Ratio |
| --- | ---: | ---: | ---: | ---: |
| PIP | `4096` | `0.000731917` | `0.001310086` | `1.790x` |
| LSI | `65536` | `0.006797644` | `0.008633615` | `1.270x` |
| Overlay seed | `262144` | `0.073687353` | `0.074747488` | `1.014x` |

## Interpretation

The bridge behaves like a stepping stone, not the destination:

- For large row streams, the typed-column conversion overhead is small enough
  to make partner continuation practical. The overlay-seed row stream with
  `262144` rows adds only `1.014x` over the existing raw row path.
- For smaller row streams, fixed transfer/setup cost dominates. PIP at `4096`
  rows is `1.790x` over count-only, so a count-only path should stay canonical
  when the user does not need row payloads.
- The probe confirms a design direction rather than a public speedup claim:
  row-bearing continuations should move from app dictionaries to typed columns
  now, then to device-resident row streams later.

## Boundary

The probe is internal engineering evidence. It does not authorize v2.5 release,
public speedup wording, broad RT-core wording, whole-app speedup wording,
true-zero-copy wording, device-resident handoff wording, automatic
partner-selection wording, package-install wording, paper-reproduction wording,
or app-specific native engine logic.
