# Goal2437 RT-DBSCAN Explicit Continuation Planner

Date: 2026-05-19

Status: implemented locally, no new pod run required.

## Purpose

Goals 2431, 2433, and 2435 added three generic RT-DBSCAN continuation surfaces:

- full OptiX-written directed fixed-radius adjacency stream;
- memory-bounded chunked OptiX adjacency stream;
- single-pass chunked continuation that avoids the second RT adjacency fill.

Those paths created a planning problem. Full adjacency is fastest when the whole
stream fits in memory. Chunked adjacency is safer when dense rows would allocate
one huge neighbor-index table. The app needed a learner-visible way to choose
between them without creating an invisible runtime dispatcher.

## What Changed

`examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
now exposes:

- `estimate_rt_dbscan_directed_adjacency_edges(dataset, point_count)`
- `plan_rt_dbscan_continuation_execution(...)`
- CLI mode `planned_rt_dbscan_continuation`
- CLI option `--adjacency-edge-budget`

The existing one-shot `planned_rt_dbscan` mode is unchanged. Goal2437 adds a
separate continuation planner for experiments where exact adjacency is required.

## Policy

The continuation planner records:

- estimated directed fixed-radius adjacency edge count;
- explicit directed-edge budget;
- estimated full-stream bytes;
- whether the full stream fits the budget;
- selected generic contract;
- evidence goals used for the decision;
- claim-boundary flags.

Current decisions:

| Condition | Selected mode |
| --- | --- |
| `tiny` fixture | `cpu_reference` |
| estimated stream fits budget | `optix_rt_core_adjacency_cupy_components_3d` |
| estimated stream exceeds budget | `optix_rt_core_chunked_adjacency_cupy_components_3d` |

The planner surface is deliberately named:

```text
benchmark_app_plan_explain_not_engine_dispatch
```

This is an app-level plan/explain helper, not a hidden dispatcher or hidden
engine scheduler.

## Validation

Local validation:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal2437_rt_dbscan_explicit_continuation_planner_test
```

The focused test verifies:

- tiny planning stays on the CPU reference fixture;
- `clustered3d` 4096 selects full OptiX adjacency with the default budget;
- `clustered3d` 32768 selects chunked OptiX adjacency with the default budget;
- forcing smaller/larger budgets flips the selected mode as expected;
- the old one-shot planner remains separate;
- the docs and report keep the plan/explain claim boundary explicit.

No pod run is required because this goal changes only app-level planning and
documentation. Goal2431/2433/2435 already provide the hardware evidence for the
underlying modes.

## Boundary

This goal does not add native DBSCAN ABI. It does not change native engine
semantics. It does not authorize broad RT-core speedup, paper reproduction, or
release claims.

It also does not replace the one-shot `planned_rt_dbscan` policy. The new mode
is for explicit adjacency-continuation experiments where the user wants to
choose between full and chunked generic stream contracts.

## Verdict

`accept-with-boundary`.
