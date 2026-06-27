# Goal3931 Combined Pod Performance Manifest Intake Evaluator

Date: 2026-06-08

## Purpose

Goal3931 adds a bounded evaluator for the future Goal3927 combined A5000 pod
manifest:

`scripts/goal3931_evaluate_combined_pod_perf_manifest.py`

The evaluator turns `summary_manifest.json` into an intake summary that checks:

- all top-level claim-boundary flags remain false;
- RayJoin cases expose wrapper timing, nested subprobe timing, and loaded-case
  reuse flags;
- RTDBSCAN includes both unblocked and blocked Numba rows;
- RTDBSCAN blocked-vs-unblocked elapsed ratio clears, misses, or falls below a
  conservative 1.05x review threshold.

## Boundary

Goal3931 does not run performance tests, promote a default route, authorize
release wording, authorize public speedup claims, authorize broad RT-core
claims, authorize true-zero-copy wording, or claim paper reproduction. It only
standardizes how the next pod result should be read.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3931_combined_pod_perf_manifest_intake_evaluator_test
```

Expected: all tests pass.
