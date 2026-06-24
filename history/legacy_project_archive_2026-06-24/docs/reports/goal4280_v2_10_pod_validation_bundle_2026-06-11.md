# Goal4280 v2.10 Pod Validation Bundle

Status: local pod-preflight and hardware-runner preparation.

## Purpose

The current v2.10 docs, source-tree doctor, and benchmark evidence index make
the project navigable. The next risk is paid pod time: users should not stitch
together old runbook fragments or wait blindly on long commands. Goal4280 adds
one bounded bundle that runs fast preflight locally and only runs expensive
hardware packets when explicitly requested.

## Delivered

| File | Action | Reason |
| --- | --- | --- |
| `scripts/rtdl_v2_10_pod_validation_bundle.py` | Added v2.10 pod validation bundle. | Runs source-tree doctor, benchmark evidence index, front-door dry-run, scale-profile dry-run, and optional hardware packets with progress lines and JSON artifacts. |
| `docs/audit/runbooks/v2_10_pod_validation_bundle.md` | Added current runbook. | Gives concise pod commands separate from older historical cloud runbooks. |
| `docs/learn/benchmark_evidence_index.md` | Linked the pod bundle runbook. | Makes the benchmark evidence page point to the bounded hardware procedure. |
| `tests/goal4280_v2_10_pod_validation_bundle_test.py` | Added focused tests. | Validates local preflight output, explicit hardware flags, non-authorizing claim flags, and runbook wiring. |

## Boundary

The default bundle does not run hardware timing. It is safe local preflight. The
hardware packet requires explicit `--run-front-door`, `--run-scale-profile`, or
`--run-partner-comparison` flags and still does not authorize release,
speedup, broad RT-core, paper-reproduction, automatic-partner, or zero-copy
claims.

## Validation

Focused validation command:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal4280_v2_10_pod_validation_bundle_test \
  tests.goal4279_benchmark_evidence_index_test \
  tests.goal4278_source_tree_doctor_test
```

Focused bundle gate: 10 tests ran, all passed.

Expanded v2.10 doc/release/navigation gate: 33 tests ran, all passed.
