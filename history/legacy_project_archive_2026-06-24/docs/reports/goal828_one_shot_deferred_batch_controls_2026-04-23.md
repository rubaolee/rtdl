# Goal828 One-Shot Deferred Batch Controls

Date: 2026-04-23

## Purpose

Goal828 avoids manual cloud command loops. The RTX one-shot runner already
boots, builds, runs the manifest, analyzes artifacts, and bundles outputs. It
now also exposes the same deferred/filter controls as the underlying Goal761
runner.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal769_rtx_pod_one_shot.py`
- `/Users/rl2025/rtdl_python_only/tests/goal769_rtx_pod_one_shot_test.py`

## New CLI Controls

The one-shot runner now supports:

```text
--include-deferred
--only <app-or-path-name>
```

These are passed through to:

```text
scripts/goal761_rtx_cloud_run_all.py
```

## Cloud Cost Impact

This lets a future paid pod run active entries plus selected deferred readiness
gates in one session. It directly supports the rule: do not ask for repeated
pod restarts/stops per app.

Example future command:

```text
python3 scripts/goal769_rtx_pod_one_shot.py \
  --branch codex/rtx-cloud-run-2026-04-22 \
  --optix-prefix /workspace/vendor/optix-dev-9.0.0 \
  --include-deferred \
  --only service_coverage_gaps \
  --only event_hotspot_screening
```

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal769_rtx_pod_one_shot_test
```

Result:

```text
Ran 2 tests
OK
```

Broader runner/artifact regression set:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal769_rtx_pod_one_shot_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal827_cloud_artifact_contract_audit_test
```

Result:

```text
Ran 14 tests in 1.335s
OK
```

Pre-cloud readiness gate:

```text
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

Result: `valid: true`.

## Verdict

Goal828 is complete locally. No cloud pod was started. The next cloud session
can be a single batched one-shot run with active and selected deferred entries.
