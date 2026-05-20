# Goal2453 RT-DBSCAN Planner Budget Pod Smoke

Date: 2026-05-19

Status: pod-smoked.

## Purpose

Goal2452 raised the explicit continuation planner's default directed-edge
budget to `160,000,000`. Goal2453 verifies that the actual benchmark mode now
selects the fast full-adjacency branch on hardware for the 32,768-point
`clustered3d` row.

## Artifact

```text
docs/reports/goal2453_rt_dbscan_planner_budget_pod_smoke/summary.json
```

## Result

The pod smoke selected:

```text
optix_rt_core_adjacency_cupy_components_3d
```

with:

- estimated directed edges: `135291470`
- directed-edge budget: `160000000`
- `full_stream_fits_budget: true`
- `not_hidden_dispatcher: true`
- elapsed seconds: `1.6375182308256626`

The run used `--no-validation`, so `matches_reference` is `null`; correctness
for the full-adjacency contract is covered by prior focused tests and the
Goal2452 full-vs-chunked signature match artifact.

## Boundary

This is a planner smoke, not a release claim or paper reproduction claim. The
planner remains explicit and records the selected mode and budget decision.

## Verdict

`accept-with-boundary`.
