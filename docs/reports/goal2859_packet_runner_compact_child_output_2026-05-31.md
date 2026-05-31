# Goal2859 Packet Runner Compact Child Output

Date: 2026-05-31

Verdict: **accept-with-boundary**

Goal2859 adds an optional compact-output mode to the Goal2855 v2.5 canonical
packet runner:

```text
--compact-child-output
```

The default behavior is unchanged. Without this flag, child harnesses stream
their full stdout exactly as before.

With the flag enabled, the runner saves every child harness stdout stream under
`_stdout/<goal>_<app>.stdout` and echoes only progress or error-like lines to
the terminal. This keeps pod runs readable while preserving the full JSON and
diagnostic output for post-run inspection.

## Why

The first full Goal2855 packet validation was correct but noisy: each child
harness printed a large JSON payload. That made the terminal hard to scan even
though the run had good progress markers.

The compact mode preserves the important operator behavior:

- `[goal2855]` start/finish lines remain visible,
- child progress lines such as `[goal2803] membership case ...` remain visible,
- traceback, usage, error, failed, and unittest summary lines remain visible,
- full child stdout is retained on disk,
- packet summary JSON still records per-harness commands, return codes,
  timeouts, elapsed time, and stdout log paths.

## Boundary

This is an operational logging improvement only. It does not change benchmark
logic, native RTDL behavior, partner behavior, performance measurements, or any
claim boundary.

It does not authorize release, public speedup, broad RT-core speedup,
whole-app speedup, paper reproduction, true-zero-copy, or Triton auto-selection
claims.

## Validation

Local validation:

```text
py -3 -m py_compile scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal2855_v2_5_current_canonical_harness_packet_runner_test \
  tests.goal2857_v2_5_readiness_indexes_packet_runner_test
```

Result:

```text
Ran 12 tests in 0.584s
OK
```

Plan probe:

```text
py -3 scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py \
  --list --fail-fast --compact-child-output \
  --output-dir C:\Users\Lestat\AppData\Local\Temp\goal2859_plan_probe
```

The plan records `compact_child_output: true` for all seven harnesses and assigns
each one a `.stdout` log path.

## Conclusion

Goal2859 accepts compact child-output mode as a safer operator experience for
long pod runs. The recommended full packet command is now:

```bash
PYTHONPATH=src:. timeout 2400s python3 -u \
  scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py \
  --fail-fast \
  --compact-child-output \
  --output-dir /tmp/goal2855_current_packet
```
