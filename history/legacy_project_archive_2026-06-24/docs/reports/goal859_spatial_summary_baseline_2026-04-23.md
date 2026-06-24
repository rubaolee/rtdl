# Goal859 Spatial Summary Baseline Writer

Date: 2026-04-23

## Purpose

Goal859 adds the missing local baseline collector for the two partial-ready
spatial OptiX apps:

- `service_coverage_gaps`
- `event_hotspot_screening`

Before this goal, those apps had:

- a prepared OptiX summary path,
- a phase profiler,
- a promotion packet,

but no Goal835-valid local baseline artifact writer for the same compact-summary
contract. That kept them in the deferred set.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal859_spatial_summary_baseline.py`
- `/Users/rl2025/rtdl_python_only/tests/goal859_spatial_summary_baseline_test.py`

## What The New Script Does

`goal859_spatial_summary_baseline.py` writes Goal835-compatible baseline
artifacts for:

- `service_coverage_gaps`
  - `cpu_oracle_summary`
  - `embree_summary_path`
  - `scipy_baseline_when_available`
- `event_hotspot_screening`
  - `cpu_oracle_summary`
  - `embree_summary_path`
  - `scipy_baseline_when_available`

Each artifact records:

- phase-separated timings using the Goal835 phase names:
  - `input_build`
  - `optix_prepare`
  - `optix_query`
  - `python_postprocess`
- compact summary output only
- correctness parity
- validation notes
- benchmark scale

## Boundary

This is still local baseline tooling.

It does not:

- promote either app to active RTX claim review
- create a real RTX artifact
- authorize a public RTX speedup claim
- compare whole-app row-output timings against compact prepared OptiX timings

The collector stays bounded to the same compact-summary contract already stated
in Goal835 and Goal849.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal859_spatial_summary_baseline_test \
  tests.goal819_spatial_prepared_summary_rt_core_gate_test \
  tests.goal811_spatial_optix_summary_phase_profiler_test
```

Result:

```text
Ran 13 tests
OK
```

Additional local checks:

```text
python3 -m py_compile \
  scripts/goal859_spatial_summary_baseline.py \
  tests/goal859_spatial_summary_baseline_test.py

git diff --check
```

Both passed.

## Why This Matters

This closes one of the concrete blockers identified in the spatial promotion
packet: the apps no longer depend on a future collector being invented before
baseline artifacts can be written.

After Goal859, the remaining blockers for these two apps are:

- collecting the actual baseline artifacts at the chosen benchmark scale
- obtaining a real RTX phase artifact
- review/consensus on the same-semantics comparison package

## Verdict

Goal859 is complete locally. The spatial prepared-summary apps now have a
baseline artifact writer consistent with the existing Goal835 contract.
