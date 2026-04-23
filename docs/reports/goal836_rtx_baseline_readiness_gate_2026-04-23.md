# Goal836 RTX Baseline Readiness Gate

Status: implemented; current gate result is `needs_baselines`.

## Purpose

Goal835 defined which same-semantics baselines are required before any public RTX speedup claim can be made for active or deferred NVIDIA RT-core app paths. Goal836 turns that plan into a machine-readable readiness gate.

The gate is intentionally local-only. It does not run benchmarks, start cloud resources, promote deferred apps, or authorize RTX speedup claims.

## Implementation

- Added `/Users/rl2025/rtdl_python_only/scripts/goal836_rtx_baseline_readiness_gate.py`.
- Added `/Users/rl2025/rtdl_python_only/tests/goal836_rtx_baseline_readiness_gate_test.py`.
- Generated `/Users/rl2025/rtdl_python_only/docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json`.
- Generated `/Users/rl2025/rtdl_python_only/docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.generated.md`.

## Artifact Schema

For every required baseline listed by Goal835, the gate expects a JSON artifact at the deterministic `goal835_baseline_*_<baseline>_2026-04-23.json` path. A valid artifact must provide:

- matching `app`, `path_name`, and `baseline_name`;
- `status: "ok"`;
- `correctness_parity: true`;
- `phase_separated: true`;
- `authorizes_public_speedup_claim: false`;
- `repeated_runs` greater than or equal to the Goal835 minimum;
- `required_phase_coverage` covering every required phase from Goal835;
- matching `comparable_metric_scope`.
- matching `benchmark_scale` when the Goal835 row defines a scale.

## Current Result

- rows checked: `8`
- active rows: `5`
- deferred rows: `3`
- required baseline artifacts: `23`
- valid artifacts: `0`
- missing artifacts: `23`
- invalid artifacts: `0`

This is the expected result before baseline collection. It makes the release flow safer: an RTX cloud result cannot accidentally be treated as a complete speedup claim package unless the same-semantics baselines are present and schema-valid.

## Verification

Command:

```bash
PYTHONPATH=src:. python3 -m unittest -v tests.goal836_rtx_baseline_readiness_gate_test
```

Result:

```text
Ran 4 tests in 0.203s
OK
```

Command:

```bash
python3 scripts/goal836_rtx_baseline_readiness_gate.py --output-json docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.json --output-md docs/reports/goal836_rtx_baseline_readiness_gate_2026-04-23.generated.md
```

Result: expected nonzero gate status with `Status: needs_baselines`, because baseline artifacts have not yet been collected.

## Claim Boundary

Goal836 does not say RTDL is faster than CPU, Embree, PostgreSQL, SciPy, PostGIS, Vulkan, HIPRT, or any other baseline. It says the exact opposite for now: the RTX claim package remains incomplete until baseline artifacts are collected and pass this gate.
