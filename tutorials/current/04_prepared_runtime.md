# Prepared Runtime

V3's important runtime idea is prepared execution.

Instead of treating every call as a fresh one-off operation, V3 can prepare
kernel state and reuse the prepared route when the workload shape allows it.
This is the trunk that current examples and benchmark code are expected to use.

For a small local walkthrough:

```powershell
py -3 examples\current\getting_started\rtdl_prepared_measurement_demo.py
```

Prepared execution is a capability. It is not, by itself, a public speedup
statement. Performance wording should name the exact row, metric, hardware, and
measurement context.

Next: [Measurement Boundaries](05_measurement_boundaries.md)
