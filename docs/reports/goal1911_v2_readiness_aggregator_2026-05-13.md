# Goal1911 - v2 Readiness Aggregator

Status: active-local-gate

Date: 2026-05-13

## Scope

Goal1911 adds a machine-readable readiness aggregator:

`scripts/goal1911_v2_readiness_aggregator.py`

The aggregator reads the current v2.0 gate files and reports which release
slots are still blocked. It is intentionally conservative and always keeps v2.0
release unauthorized until pod evidence, post-pod acceptance, source-tree or
package policy consensus, final release consensus, and explicit release action
exist.

## Command

```bash
PYTHONPATH=src:. python3 scripts/goal1911_v2_readiness_aggregator.py
```

The generated JSON goes to:

`docs/reports/goal1911_v2_readiness_aggregator.json`

## Current Expected Result

After the Goal1937/1940 pod scale-up work, the expected status is still
`blocked`, but pod evidence has now been collected. The remaining unconditional
blockers are source-tree/package policy consensus, final v2.0 release consensus,
and explicit user release action.

The JSON also reports the strict Goal1905 acceptance status, the Goal1916
post-pod manifest status, and any post-pod external review files that are
present. These fields keep old hardware blockers from lingering after pod
evidence lands.

## Boundary

Goal1911 is an aggregator, not evidence. It does not replace Goal1905 strict
post-pod acceptance, external reviews, final consensus, or a user-requested
release action.
