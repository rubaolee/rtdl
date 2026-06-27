# Prepared Execution And Measurement

Status: current v3.0 source-tree tutorial.

Goal: measure an RTDL program without mixing setup, warmup, and steady-state
work.

## Separate The Phases

| Phase | Meaning |
| --- | --- |
| setup | build inputs, load native libraries, allocate workspaces |
| prepare | build reusable backend or partner state |
| warmup | pay first-launch and cache effects before timing |
| steady state | repeat the contract being measured |
| validation | compare against an oracle or accepted tolerance |

One-shot app time is useful for user experience. Prepared steady-state time is
useful for repeated query workloads. Do not mix the two in one headline.

## Prepared Pattern

```text
prepare scene or columns once
repeat primitive or continuation many times
record repeat count and dataset
validate against CPU oracle or same-contract reference
publish the exact command
```

## Learner Commands

Prepared examples live in the source tree:

```bash
PYTHONPATH=src:. python examples/current/getting_started/rtdl_prepared_measurement_demo.py
PYTHONPATH=src:. python examples/current/getting_started/rtdl_feature_quickstart_cookbook.py
```

`rtdl_prepared_measurement_demo.py` is the small measurement lesson. It uses
the portable CPU Python reference backend by default, prepares a tiny
hello-world scene through the explicit prepared-session helper, runs warmup
iterations, times only the steady-state kernel repeats, validates against the
CPU Python oracle, and prints JSON fields reviewers should expect:

- `command`
- `commit`
- `backend`
- `partner`
- `dataset`
- `timed_phase`
- `prepared_session_residency`
- `phases_s`
- `correctness`

It also prints `performance_evidence: false` because the scene is a teaching
fixture, not a benchmark claim. The cookbook is larger than hello world, but
still safe as a source-tree learner program.

## Performance Rule

A result is not decision-grade unless it names:

- command;
- commit;
- dataset;
- backend;
- partner;
- hardware;
- correctness check;
- timed phase.

## Next

Continue with [Benchmark App Walkthrough](07_benchmark_app_python_rtdl_partner.md).
