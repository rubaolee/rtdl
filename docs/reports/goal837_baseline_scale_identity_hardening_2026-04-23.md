# Goal837 Baseline Scale Identity Hardening

Status: implemented.

## Purpose

Goal836 originally validated baseline artifacts for identity, correctness parity, phase separation, repeated runs, required phase coverage, and metric scope. Before generating local baseline artifacts, one more safety condition was needed: baseline artifacts must also match the benchmark scale from the RTX manifest.

Without this, a small local smoke artifact could be schema-valid for a future large RTX comparison package. Goal837 closes that hole.

## Changes

- `/Users/rl2025/rtdl_python_only/scripts/goal835_rtx_baseline_collection_plan.py` now carries each manifest row's `scale` into the generated baseline plan.
- `/Users/rl2025/rtdl_python_only/scripts/goal836_rtx_baseline_readiness_gate.py` now requires `benchmark_scale` in a baseline artifact to exactly match the Goal835 row scale whenever the row has a scale.
- `/Users/rl2025/rtdl_python_only/tests/goal835_rtx_baseline_collection_plan_test.py` verifies scale preservation for DB, fixed-radius Outlier/DBSCAN, and robot rows.
- `/Users/rl2025/rtdl_python_only/tests/goal836_rtx_baseline_readiness_gate_test.py` verifies that a valid artifact must include matching `benchmark_scale`, and that a scale mismatch is reported as an invalid artifact.
- Regenerated `/Users/rl2025/rtdl_python_only/docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.json`.
- Regenerated `/Users/rl2025/rtdl_python_only/docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json`.

## Current Result

The baseline readiness gate still reports `needs_baselines`, with 23 missing required artifacts. This remains expected. The difference is that future baseline artifacts cannot pass the gate unless they match the intended RTX benchmark scale.

## Verification

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal835_rtx_baseline_collection_plan_test tests.goal836_rtx_baseline_readiness_gate_test
python3 -m py_compile scripts/goal835_rtx_baseline_collection_plan.py scripts/goal836_rtx_baseline_readiness_gate.py tests/goal835_rtx_baseline_collection_plan_test.py tests/goal836_rtx_baseline_readiness_gate_test.py
git diff --check
```

Result:

```text
Ran 9 tests in 0.345s
OK
```

`py_compile` and `git diff --check` passed.

## Claim Boundary

Goal837 does not run benchmarks, start cloud resources, collect baselines, or authorize speedup claims. It only prevents wrong-scale baseline artifacts from satisfying the readiness gate.
