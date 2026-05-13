# Goal1913 - v2 Pod Session Runbook

Status: runbook-ready-waiting-for-pod

Date: 2026-05-13

## Scope

Goal1913 adds a single shell runbook for the next RTX pod session:

`scripts/goal1913_v2_pod_session_runbook.sh`

It prints explicit phase progress and runs the current sequence:

1. Goal1908 local non-pod preflight.
2. Goal1903 RTX pod batch.
3. Goal1905 strict post-pod acceptance.
4. Goal1911 readiness aggregation.

## Command

From a fresh pod checkout on `main`:

```bash
OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1913_v2_pod_session_runbook.sh
```

## Progress Contract

The script prints `[goal1913] BEGIN ...` and `[goal1913] END ...` around each
phase. This keeps long pod sessions visible and avoids silent multi-minute
work.

## Boundary

Goal1913 is orchestration only. It does not weaken the RTX requirement in
Goal1903, does not authorize release, and does not replace post-pod external
review or final 3-AI release consensus.
