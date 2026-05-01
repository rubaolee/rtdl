# Goal860 Spatial Partial-Ready Gate

Date: 2026-04-23

## Purpose

Goal860 adds a focused readiness gate for the two spatial prepared-summary apps:

- `service_coverage_gaps`
- `event_hotspot_screening`

These apps are stronger than the redesign-heavy app families, but weaker than
the already-active RT paths. They need a separate gate because their promotion
depends on two distinct conditions:

1. same-semantics local baseline artifacts must exist;
2. a real OptiX phase artifact must also exist.

The existing global gates did not isolate that intermediate state cleanly.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal860_spatial_partial_ready_gate.py`
- `/Users/rl2025/rtdl_python_only/tests/goal860_spatial_partial_ready_gate_test.py`

## What The Gate Checks

For each of the two spatial apps, Goal860 checks:

- required baseline artifacts:
  - `cpu_oracle_summary`
  - `embree_summary_path`
- optional baseline artifact:
  - `scipy_baseline_when_available`
- real RTX artifact presence and validity:
  - `docs/reports/goal811_service_coverage_rtx.json`
  - `docs/reports/goal811_event_hotspot_rtx.json`

The resulting row status is one of:

- `needs_required_baselines`
- `needs_real_rtx_artifact`
- `ready_for_review`

## Boundary

This gate does not promote anything by itself.

It does not:

- authorize a public RTX speedup claim
- treat optional SciPy baselines as blockers
- treat a dry-run profiler artifact as equivalent to a real OptiX artifact

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal860_spatial_partial_ready_gate_test \
  tests.goal859_spatial_summary_baseline_test \
  tests.goal819_spatial_prepared_summary_rt_core_gate_test
```

Result:

```text
Ran 12 tests
OK
```

Additional local checks:

```text
python3 -m py_compile \
  scripts/goal860_spatial_partial_ready_gate.py \
  tests/goal860_spatial_partial_ready_gate_test.py

git diff --check
```

Both passed.

## Why This Matters

This makes the next decision precise:

- if required local baselines are missing, the apps are still blocked locally;
- if required baselines are present but the real RTX artifact is missing, the
  next step is cloud or RTX-host collection;
- only when both are present can the apps move to review.

## Verdict

Goal860 is complete locally. It gives the spatial prepared-summary pair a
separate, auditable promotion gate instead of leaving them mixed into the
broader deferred set.
