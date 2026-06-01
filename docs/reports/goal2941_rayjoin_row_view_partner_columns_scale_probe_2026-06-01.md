# Goal2941: RayJoin Row-View Partner-Column Scale Probe

Date: 2026-06-01
Status: script added; pod evidence pending

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

## Boundary

The probe is internal engineering evidence. It does not authorize v2.5 release,
public speedup wording, broad RT-core wording, whole-app speedup wording,
true-zero-copy wording, device-resident handoff wording, automatic
partner-selection wording, package-install wording, paper-reproduction wording,
or app-specific native engine logic.
