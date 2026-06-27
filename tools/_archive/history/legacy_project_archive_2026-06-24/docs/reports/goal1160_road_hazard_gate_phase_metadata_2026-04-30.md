# Goal1160: Road-Hazard Gate Phase Metadata

Date: 2026-04-30

## Scope

Goal1160 updates the road-hazard native OptiX gate artifact so future cloud runs
preserve phase and native-continuation evidence. It is local preparation only.

## Problem

`road_hazard_screening` already has a compact native OptiX summary path through
`prepare_optix_segment_polygon_hitcount_2d(...).count_at_least(...)`, so the app
can avoid row materialization in `output_mode="summary"`.

However, the older Goal888 gate only stored total seconds and digests. That was
not enough to audit whether a future RTX artifact actually used the compact
native summary path rather than a row-materializing fallback.

## Implementation

`scripts/goal888_road_hazard_native_optix_gate.py` now records per-record:

- `run_phases`
- `summary_materializes_rows`
- `native_continuation_active`
- `native_continuation_backend`
- `row_count`
- `priority_segment_count`
- `output_mode`

The gate's `cloud_claim_contract.required_phase_groups` now includes these
fields. Missing-OptiX behavior remains unchanged: local macOS no-OptiX runs
record `unavailable_or_failed`.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal888_road_hazard_native_optix_gate_test \
  tests.goal1130_road_hazard_native_summary_count_test \
  tests.goal956_segment_polygon_native_continuation_metadata_test \
  tests.goal933_prepared_segment_polygon_profiler_test -q

Ran 20 tests in 0.157s
OK
```

Local no-OptiX gate probe:

```text
PYTHONPATH=src:. python3 scripts/goal888_road_hazard_native_optix_gate.py \
  --copies 2 \
  --output-mode summary \
  --output-json /tmp/goal888_road_gate_packet.json

status: non_strict_recorded_gaps
strict_pass: false
```

The CPU reference record includes phase metadata. The OptiX record is absent on
macOS and correctly has no phase metadata because it did not run.

## Boundaries

- This is an artifact-schema update and local test hardening.
- It does not prove RTX performance.
- It does not promote `road_hazard_screening` public wording.
- Future pod evidence must show `summary_materializes_rows == false`,
  `native_continuation_backend == "optix_native_hitcount_gated"`, strict parity,
  and reviewed same-semantics baseline comparison before public wording changes.

## Changed Files

- `scripts/goal888_road_hazard_native_optix_gate.py`
- `tests/goal888_road_hazard_native_optix_gate_test.py`

## Codex Verdict

ACCEPT. Goal1160 makes the road-hazard gate auditable for compact native summary
behavior while preserving strict claim boundaries.
