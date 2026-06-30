# Goal756 Prepared DB App Session Plan

## Purpose

Goal755 showed that DB prepared RT query phases are fast, but one-shot prepared dataset construction dominates total app time. Goal756 should expose a public app-level prepared session so applications can build a prepared DB dataset once and run multiple query bundles against it.

## Scope

Add a prepared-session mode for the unified DB app surface:

- regional dashboard session;
- sales-risk session;
- unified database analytics session that owns one prepared session per requested scenario.

The session should expose:

- cold prepare timing;
- repeated warm query timing;
- close timing;
- compact output summaries for large runs;
- the same correctness-visible outputs as existing one-shot app paths.

## Non-Scope

- Do not rewrite native DB kernels in this goal.
- Do not claim RTX RT-core speedup from GTX 1070.
- Do not turn RTDL into a DBMS: no SQL planner, indexes, joins, transactions, or storage engine.
- Do not change default CLI behavior; existing one-shot commands must keep working.

## Proposed User Surface

Python app usage:

```python
from examples import rtdl_database_analytics_app as db_app

with db_app.prepare_session("optix", scenario="sales_risk", copies=20000) as session:
    first = session.run(output_mode="summary")
    second = session.run(output_mode="summary")
```

CLI usage:

```bash
PYTHONPATH=src:. python examples/rtdl_database_analytics_app.py \
  --backend optix \
  --scenario sales_risk \
  --copies 20000 \
  --execution-mode prepared_session \
  --session-iterations 5 \
  --output-mode summary
```

## Expected Evidence

Run on Linux for CPU, Embree, OptiX, and Vulkan where available:

- one-shot mode;
- prepared-session cold prepare;
- prepared-session warm query median;
- close.

Goal755's measured bottleneck predicts that warm repeated session queries should show the real value of prepared RT backends.

## Acceptance Criteria

- Backward-compatible default DB app CLI behavior.
- Portable tests for the session API, output shape, close behavior, and CLI mode.
- Linux scaled performance JSON/report comparing one-shot versus prepared-session warm query behavior.
- 2+ AI consensus for plan and finish.
- Explicit GTX 1070 honesty boundary.
