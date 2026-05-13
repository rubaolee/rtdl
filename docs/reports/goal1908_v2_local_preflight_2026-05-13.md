# Goal1908 - v2 Local Preflight

Status: active-local-gate

Date: 2026-05-13

## Scope

Goal1908 adds a one-command local preflight for the current non-pod v2.0 gates:

`scripts/goal1908_v2_local_preflight.py`

It runs the package-install audit, v2 birth board tests, partner boundary doc
tests, source-tree-only proposal tests, Goal1903/1904/1905/1906/1907/1909/1910/1911/1912
tests, the public v2 claim-boundary scanner, the pre-pod Goal1905 acceptance
snapshot, and the Goal1911 readiness aggregator.

## Command

```bash
PYTHONPATH=src:. python3 scripts/goal1908_v2_local_preflight.py
```

The generated JSON goes to:

`docs/reports/goal1908_v2_local_preflight.json`

## Boundary

Goal1908 intentionally does not run hardware performance evidence. Passing it
means the current non-pod v2 gates are internally coherent. It does not
authorize v2.0 release, package-install support, broad RT-core speedup claims,
or whole-app speedup claims.
