# Goal935 Consolidated RTX Runbook Sync After Goal934

Date: 2026-04-25

## Verdict

Local pre-cloud synchronization is valid. The RTX cloud runbook now matches the
current manifest after Goals933 and 934. No cloud pod was started, and no speedup
claim is authorized by this audit.

## Problem Found

The consolidated RTX runbook still listed the old Group E pair-row target:

```text
segment_polygon_anyhit_rows_native_bounded_gate
```

The current Goal759 manifest now uses the prepared Goal934 target:

```text
segment_polygon_anyhit_rows_prepared_bounded_gate
```

Leaving the old target in the runbook would waste pod time or produce a stale
one-shot correctness artifact instead of the required prepared polygon-BVH
artifact.

## Fix

Updated `docs/rtx_cloud_single_session_runbook.md`:

- Group E now runs:
  - `road_hazard_native_summary_gate`
  - `segment_polygon_hitcount_native_experimental`
  - `segment_polygon_anyhit_rows_prepared_bounded_gate`
- Group E now explicitly documents:
  - Goal933 road-hazard prepared profiler.
  - Goal933 segment/polygon hit-count prepared profiler.
  - Goal934 bounded pair-row prepared profiler with `emitted_count`,
    `copied_count`, and `overflowed`.
- Artifact copyback instructions now include `goal933_*` and `goal934_*`
  artifacts, while marking `goal873_*` and `goal888_*` as historical when
  present.

Added regression coverage in
`tests/goal829_rtx_cloud_single_session_runbook_test.py` so the runbook cannot
silently regress to the old pair-row gate.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal762_rtx_cloud_artifact_report_test

Ran 34 tests in 2.275s
OK

PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json

valid: true

git diff --check
```

## Current Pod Policy

Do not start a pod for one app. The next paid RTX run should still use the
single-session OOM-safe groups, copying artifacts back after every group. Group
E is now safe to run against the current prepared segment/polygon manifest.
