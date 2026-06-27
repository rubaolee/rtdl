# Handoff - Gemini Review Goal3742 RT-DBSCAN Numba Grid Reference

Please perform an independent Gemini review of Goal3742 and write:

`docs/reviews/goal3743_gemini_review_goal3742_rt_dbscan_numba_grid_reference_2026-06-07.md`

## Context

Goal3740 identified RT-DBSCAN as one of three benchmark apps that still needs a
Numba reference path so users are not forced into CuPy RawKernel-style custom
logic. Goal3742 adds a generic Numba CUDA grid component-labeling adapter and
wires it into the RT-DBSCAN benchmark app.

## Files to Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py`
- `examples/v2_0/research_benchmarks/rt_dbscan/README.md`
- `tests/goal3742_rt_dbscan_numba_grid_reference_test.py`
- `docs/reports/goal3742_rt_dbscan_numba_grid_reference_2026-06-07.md`
- `docs/reports/goal3742_rt_dbscan_numba_grid_a5000/summary.json`
- `docs/reports/goal3742_rt_dbscan_numba_grid_a5000/larger_summary.json`

## Validation Already Run

Local:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.goal3742_rt_dbscan_numba_grid_reference_test \
  tests.goal2392_rt_dbscan_benchmark_campaign_test \
  tests.goal2394_rt_dbscan_device_grid_baseline_test \
  tests.goal3740_benchmark_app_adequacy_after_goal3737_test

Ran 19 tests in 2.633s
OK (skipped=2)
```

A5000 pod:

```text
PYTHONPATH=src:. /root/rtdl_numba_venv/bin/python -m unittest \
  tests.goal3742_rt_dbscan_numba_grid_reference_test

Ran 6 tests in 1.835s
OK
```

## Questions

1. Does Goal3742 keep native engines app-agnostic and avoid any DBSCAN-specific
   native ABI?
2. Is the Numba adapter genuinely generic fixed-radius graph component
   continuation over device columns?
3. Does the RT-DBSCAN app expose explicit user-selected Numba modes without
   hidden dispatch?
4. Does the report interpret performance honestly: Numba competitive and
   sometimes faster than prepared CuPy on clustered rows, but slower on
   road-shaped rows?
5. Does the report avoid release, public speedup, broad RT-core, true-zero-copy,
   automatic partner selection, and paper-reproduction claims?
6. What should the next engineering step be: OptiX core flags plus Numba grid
   continuation, or a larger Numba grouped-stream consumer?

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Please include any required-before-next-step fixes separately from
optional future work.
