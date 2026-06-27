# Goal 19 Implementation Report

## Scope

Goal 19 measures the current RTDL Embree runtime against pure native C++ + Embree for the workloads that already have native baselines:

- `lsi`
- `pip`

The round is intentionally bounded to a `5–10 minute` local runtime budget.

## Implemented Changes

### Native executable improvements

Updated:

- [goal15_lsi_native.cpp](/Users/rl2025/rtdl_python_only/apps/goal15_lsi_native.cpp)
- [goal15_pip_native.cpp](/Users/rl2025/rtdl_python_only/apps/goal15_pip_native.cpp)

Changes:

- `--pairs-out` is now optional
- timing JSON now includes a deterministic `pair_hash`
- native runs can therefore be used in summary-only mode for larger profiles without writing full pair CSV files

### Goal 19 benchmark harness

Added:

- [goal19_compare_embree_performance.py](/Users/rl2025/rtdl_python_only/scripts/goal19_compare_embree_performance.py)

This harness runs:

1. deterministic fixture comparison
2. larger-profile comparison

For each workload it measures:

- RTDL dict-return path
- RTDL first-class raw path
- RTDL prepared raw path
- native C++ + Embree path

The larger profiles are:

- `lsi`: build `2000`, probe `1500`
- `pip`: build `2500`, probe `2000`

The default package uses:

- fixture repeats: `25`
- larger-profile repeats: `20`

Measured total package wall time:

- `8.74 min`

### Tests

Added:

- [goal19_compare_test.py](/Users/rl2025/rtdl_python_only/tests/goal19_compare_test.py)

This provides a small-profile smoke test for the full Goal 19 comparison path.

## Measured Result

See:

- [goal19_embree_performance_comparison_2026-04-01.md](/Users/rl2025/rtdl_python_only/docs/reports/goal19_embree_performance_comparison_2026-04-01.md)

Main result:

### Deterministic fixtures

`lsi`

- dict gap vs native: `13.39x`
- raw gap vs native: `0.72x`
- prepared raw gap vs native: `0.51x`

`pip`

- dict gap vs native: `31.35x`
- raw gap vs native: `1.82x`
- prepared raw gap vs native: `0.85x`

### Larger matched profiles

`lsi` (`2000 x 1500`)

- dict gap vs native: `101.56x`
- raw gap vs native: `0.98x`
- prepared raw gap vs native: `0.89x`

`pip` (`2500 x 2000`)

- dict gap vs native: `225.33x`
- raw gap vs native: `0.87x`
- prepared raw gap vs native: `0.83x`

## Interpretation

The architectural result is clear:

- the ordinary dict-return RTDL path is still nowhere near native performance
- the low-overhead raw/prepared runtime paths are close to native on the measured `lsi` and `pip` comparisons

So the current project direction should be:

- keep the DSL
- treat the dict-return path as a convenience path
- treat raw/prepared execution as the serious performance path

## Validation

Executed successfully:

- `PYTHONPATH=src:.:scripts python3 -m unittest tests.goal15_compare_test tests.goal19_compare_test`
- `PYTHONPATH=src:.:scripts python3 scripts/goal19_compare_embree_performance.py`
- `PYTHONPATH=src:.:scripts python3 -m unittest discover -s tests -p '*_test.py'`
- `make verify`

Current full-suite result:

- `80` tests passed
