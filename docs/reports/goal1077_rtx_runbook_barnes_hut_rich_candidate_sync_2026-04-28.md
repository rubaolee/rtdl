# Goal1077 RTX Runbook Barnes-Hut Rich Candidate Sync

Date: 2026-04-28

## Scope

This goal updates the RTX cloud runbook after Goal1075 and Goal1076.

## Change

The runbook still makes Goal1072 the primary compact facility/robot pod batch.
It now also documents Goal1076 as a separate optional Barnes-Hut rich-contract
runner if pod time remains after Goal1072 artifacts are copied back.

The runbook explicitly says not to merge Barnes-Hut into the facility/robot
Goal1072 batch.

## Boundary

This is documentation/runbook synchronization only. It does not run cloud,
authorize release, change public wording, or authorize public RTX speedup
claims.

## Verification

Ran:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal1076_barnes_hut_rich_rtx_pod_candidate_test
```

Result: 11 tests OK.
