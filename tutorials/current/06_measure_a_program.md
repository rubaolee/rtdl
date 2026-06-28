# Measure a Program

RTDL programs have several phases. If you measure only the final number, you
will not know whether time was spent in setup, traversal, continuation, or data
movement.

For a V4 app, record at least:

- the operator surface;
- the partner;
- the input size;
- setup time;
- hot run time;
- continuation time;
- result validation.

A tiny measurement record can be plain Python data:

```python
record = {
    "app": "triangle_counting",
    "operator": "any_hit",
    "partner": "torch",
    "input": "rays=1024 triangles=2048",
    "setup_seconds": 0.0,
    "hot_seconds": 0.0,
    "continuation_seconds": 0.0,
    "validated": True,
}

print(record["app"], record["operator"], record["partner"], record["validated"])
```

Run the measurement tutorial program:

```powershell
$env:PYTHONPATH = "src;."
py -3 examples\tutorial_programs\measure_phases.py
```

Linux or macOS:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/measure_phases.py
```

When you build your own benchmark, keep the measured question narrow:

```python
import rtdsl.v4 as rt

plan = rt.plan_operator_request_v4("any_hit", partner="torch")
measurement = {
    "surface": plan.api_surface,
    "metric": "hot_seconds",
    "includes_setup": False,
    "includes_result_validation": False,
}

print(measurement["surface"])
print(measurement["metric"])
```

Then keep a separate end-to-end number for the full application. Both numbers
are useful. The operator number tells you whether the RTDL surface is healthy;
the app number tells you whether the whole workflow is healthy.

For public performance wording, use
[../../docs/learn/performance_wording.md](../../docs/learn/performance_wording.md).

Next: [Build the Benchmark Apps](07_benchmark_apps.md)
