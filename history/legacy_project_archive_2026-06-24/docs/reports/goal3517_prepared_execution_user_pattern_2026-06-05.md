# Goal3517 Prepared Execution User Pattern

Date: 2026-06-05

## Verdict

`accept-with-boundary`.

Goal3517 defines a thin, generic prepared-execution explanation surface for the
v2.8 closeout lane. It does not add a new native primitive, does not change the
Goal3511 measured behavior, and does not authorize release, public speedup
wording, broad RT-core speedup wording, true zero-copy wording, RayJoin paper
reproduction, `rtdl beats RayJoin`, full overlay claims, hidden partner
selection, or app-specific native-engine behavior.

## User Pattern

The explicit workflow is:

```text
prepare -> pack/cache -> warm -> run steady-state -> explain timings
```

The new public helper surface is:

- `rt.describe_prepared_execution_user_pattern()`
- `rt.prepared_execution_report_from_artifact(...)`
- `rt.validate_prepared_execution_report(...)`
- `rt.PreparedExecutionReport`
- `rt.PreparedExecutionPhaseTiming`

The helper normalizes an already-measured artifact into required phases:

| Phase | Purpose |
| --- | --- |
| `prepare` | one-time build or rehydrate prepared payloads |
| `cache_load` | load reusable prepared payload columns |
| `cache_write` | write reusable prepared payload columns |
| `warmup` | discarded warm passes before steady-state timing |
| `steady_state_stream` | prepared relation stream after warmup |
| `candidate_filter` | optional device filter before continuation planning |
| `planner` | continuation planning from prepared columns |
| `executor` | explicit-partner continuation execution |
| `validation` | external oracle validation, not deployed steady-state cost |

Validation fails closed if the report lacks required phases, hides partner
choice, allows automatic partner selection, allows app-specific native-engine
logic, or inherits an authorizing source claim boundary.

## Runner Wiring

`scripts/goal3492_overlay_area_public_cdb_tile_task_executor.py` now appends:

```text
prepared_execution_report
```

to future artifacts. The raw `timing_sec` dictionary remains unchanged. The
normalized report simply makes the Goal3511 separation teachable and
machine-checkable.

## Learner Docs

Added:

- `docs/learn/prepared_execution_pattern.md`

Linked from:

- `docs/learn/README.md`
- `docs/tutorials/README.md`

The page explains that the `0.00387s` Goal3511 resident relation-stream timing
is not a whole-application time. It is one steady-state phase after setup,
cache load, warmup, planning, continuation execution, and validation are shown
separately.

## Goal3511 Evidence Normalized

The existing Goal3511 artifact normalizes to:

| Phase | Seconds |
| --- | ---: |
| Binary prepared-payload cache load | `0.192737128585577` |
| Warmups | `0.37163624819368124`, `0.0074598342180252075`, `0.007164366543292999` |
| Final prepared relation stream | `0.0038709240034222603` |
| Device tile-task planner best repeat | `0.05171292740851641` |
| Tile-task executor best repeat | `0.014305617660284042` |
| External exact oracle validation | `0.26809314265847206` |

Source artifact:

- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`

## Boundary

This goal is a user-pattern and reporting-contract cleanup. It keeps partner
choice explicit (`cupy` in the current overlay-area artifact), keeps the backend
explicit (`optix` for the current pod artifact), and keeps the native engine
generic.

No new pod run was required because the goal consumes existing Goal3511 pod
evidence and does not alter the measured execution path. A fresh pod artifact
can be collected in Goal3521 if the final validation packet needs current-HEAD
confirmation with the new `prepared_execution_report` field.
