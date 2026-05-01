# Goal886 Claude External Review Request

Please review the Goal886 RTX cloud start packet and return `ACCEPT` or
`BLOCK`.

Files to inspect:

- `docs/reports/goal886_rtx_cloud_start_packet_2026-04-24.md`
- `tests/goal886_rtx_cloud_start_packet_test.py`
- `docs/reports/goal885_pre_cloud_readiness_current_head_2026-04-24.json`
- `docs/rtx_cloud_single_session_runbook.md`

Review questions:

1. Is it correct to tell the user that cloud can start now if an RTX-class GPU
   is available, given the current-head readiness gate is `valid: true`?
2. Does the packet preserve the claim boundary: cloud evidence collection only,
   no public RTX speedup claim?
3. Does the active-first/deferred-second command sequence match the current
   runbook and avoid per-app pod restarts?
4. Does the packet include all 10 deferred targets from the current manifest?

Local verification:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal886_rtx_cloud_start_packet_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: `11 tests OK`.

