# Prepared Execution Pattern

RTDL v2.8 uses a prepared-execution pattern for workloads where setup is large
but repeated queries are small and fast.

The shape is:

```text
prepare -> pack/cache -> warm -> run steady-state -> explain timings
```

This is not hidden dispatch. The user still chooses the backend and partner.
The report exists so a learner can see what was paid once, what was reused, and
what belongs to the measured steady-state path.

## What Each Step Means

| Step | Meaning | Timing field |
| --- | --- | --- |
| `prepare` | Build or rehydrate prepared payloads and handles | `geometry_plus_payload_prepare` |
| `pack/cache` | Load or write reusable column payloads | `payload_cache_load`, `payload_cache_write` |
| `warm` | Run discarded prepared passes before timing steady state | `active_relation_device_columns_warmup_secs` |
| `run steady-state` | Run the prepared stream, planner, and continuation after warmup | `active_relation_device_columns`, `device_tile_task_planning_best_repeat`, `cupy_tile_task_executor_best_repeat` |
| `explain timings` | Record backend, partner, cache mode, validation, and claim boundaries | `prepared_execution_report` |

Validation oracle time is reported separately. It is important for trust, but it
is not part of the runtime path that a deployed application would pay on every
query.

## Minimal Pattern

```python
import json
import rtdsl as rt

artifact = json.load(open("docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json"))
report = rt.prepared_execution_report_from_artifact(
    artifact,
    workflow_name="simple_polygon_overlay_area_prepared_execution",
    backend="optix",
)

print(report.to_dict()["summary_sec"])
```

The report keeps the source artifact's claim flags and refuses to validate if a
source artifact authorizes release, public speedup wording, true zero-copy
wording, hidden partner selection, or app-specific native-engine behavior.

## Current v2.8 Example

For the public-CDB overlay-area route, the current evidence separates:

| Phase | Seconds |
| --- | ---: |
| Binary prepared-payload cache load | `0.1927` |
| Warmups | `0.3716`, `0.00746`, `0.00716` |
| Final prepared relation stream | `0.00387` |
| Device tile-task planner best repeat | `0.0517` |
| Tile-task executor best repeat | `0.0143` |
| External exact oracle validation | `0.2681` |

The useful lesson is not that the whole application magically takes `0.00387`
seconds. The lesson is that prepared handles, cached payloads, warmup, steady
streams, planning, continuation execution, and validation must be shown as
different phases.

## Boundaries

Prepared execution does not authorize:

- release;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true zero-copy wording;
- paper reproduction wording;
- hidden partner selection;
- app-specific native engine behavior.

The native engine remains generic. Application interpretation stays in Python
examples or user code, and the partner is explicit.
