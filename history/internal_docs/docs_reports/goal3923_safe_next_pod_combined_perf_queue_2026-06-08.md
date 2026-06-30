# Goal3923 Safe Next-Pod Combined Performance Queue

Date: 2026-06-08

## Purpose

Goal3923 packages the two pending A5000 diagnostics into one safe next-pod
queue:

- Goal3913 RayJoin LSI/overlay subprobe timing with shared loaded-case reuse.
- Goal3920 RT-DBSCAN blocked Numba column-signature timing.

This was added after the Windows PowerShell SSH quoting incident so the next
pod run can be launched via stdin with remote-side `mktemp` workspace creation,
visible progress logs, and bounded timeouts.

## Artifact

- `docs/handoff/GOAL3923_SAFE_NEXT_POD_COMBINED_PERF_QUEUE_2026-06-08.md`

## Safety Boundary

The runbook:

- uses `ssh ... 'bash -s'` stdin invocation;
- creates a remote `mktemp -d /root/goal3923_queue.XXXXXX` workspace;
- verifies the workspace is not `/root`;
- avoids `rm -rf /root...`;
- writes outputs under `/root/goal3923_combined_perf_artifacts`;
- emits progress before and after each diagnostic;
- keeps every claim-boundary flag false in the generated manifest.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3923_safe_next_pod_combined_perf_queue_test tests.goal3913_safe_next_pod_rayjoin_runbook_test tests.goal3920_safe_next_pod_rtdbscan_blocked_numba_runbook_test
```

Expected: all tests pass.

## Non-Authorization

This goal does not create performance evidence, promote routes, authorize
release wording, authorize public speedup wording, authorize true-zero-copy
wording, or claim RayJoin/DBSCAN paper reproduction. It only prepares the next
pod run to be safe and efficient.
