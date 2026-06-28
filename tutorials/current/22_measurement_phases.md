# Measurement Phases

RTDL programs should be measured in phases, because setup, hot relation work,
continuation, validation, and materialization answer different questions.

Run:

```bash
PYTHONPATH=src:. python examples/tutorial_programs/measure_phases.py --mode both
```

## Phase Boundary

Use this mental model:

| Phase | Meaning |
| --- | --- |
| setup | Build inputs and prepare reusable state. |
| hot relation | Emit relation rows or device outputs. |
| continuation | Reduce, rank, group, or summarize rows. |
| validation | Check correctness and materialize only the app result. |

This matters because an RTDL program can be excellent on the hot relation but
poorly measured if setup is mixed into the denominator. It can also be fast and
wrong if validation is skipped. Keep both timing and correctness visible.

Example timing table:

| Phase | Time | What to compare |
| --- | ---: | --- |
| setup | 120 ms | Usually amortized across repeated runs. |
| hot relation | 8 ms | The core RTDL relation/operator work. |
| continuation | 3 ms | Group, sum, rank, union, or summarize rows. |
| validation | 2 ms | Correctness check and final materialization. |
| full wall | 133 ms | User-visible one-shot cost. |

If you report only full wall time, setup may hide the hot-path behavior. If you
report only hot time, you may hide materialization or validation cost. A serious
RTDL result names both the denominator and the phase.

## V4 Mapping

The V4 surface changes the executor, not the measurement logic. A V4 run should
still identify setup, hot relation work, continuation, and validation.

Next: [Callback Planning Boundary](23_callback_planning_boundary.md)
