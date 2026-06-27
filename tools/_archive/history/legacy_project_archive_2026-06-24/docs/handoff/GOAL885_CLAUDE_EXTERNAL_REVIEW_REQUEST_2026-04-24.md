# Goal885 Claude External Review Request

Please review the Goal885 runbook refresh and return `ACCEPT` or `BLOCK`.

Files to inspect:

- `docs/rtx_cloud_single_session_runbook.md`
- `tests/goal829_rtx_cloud_single_session_runbook_test.py`
- `docs/reports/goal885_current_deferred_rtx_batch_runbook_refresh_2026-04-24.md`

Review questions:

1. Does the runbook correctly separate the active evidence batch from the
   deferred exploration batch?
2. Does the deferred batch list all current deferred RTX targets without
   overstating them as promotion-ready?
3. Does the cloud-cost rule remain clear: one pod session, no per-app restarts?
4. Are the tests sufficient to prevent the runbook from drifting back to the
   older service/hotspot-only deferred batch?

Local verification:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal769_rtx_pod_one_shot_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `10 tests OK`.

Deferred one-shot dry-run produced `status: ok`, `include_deferred: true`, and
`only_count: 10`.

