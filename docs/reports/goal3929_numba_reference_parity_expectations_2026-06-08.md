# Goal3929 Numba Reference Parity Expectations

Date: 2026-06-08

## Purpose

Goal3926's Gemini review accepted the Numba coverage audit but asked for more
systematic parity-by-default tracking. Goal3929 adds a second narrow advisory
helper:

`rtdsl.v2_6_numba_parity_expectations()`

It is built from the Goal3928 Numba reference index and records the correctness
oracle or tolerance expected for every current Numba reference row.

## Scope

The helper covers the Numba-relevant benchmark rows:

- `hausdorff_xhd`
- `spatial_rayjoin`
- `rt_dbscan`
- `raydb_style`
- `barnes_hut`
- `triangle_counting`

Rows where Numba is only a future optional candidate are intentionally excluded
from the expectation rows.

## Boundary

Goal3929 does not run new pod tests, does not create performance evidence, does
not promote RTDBSCAN blocked modes, does not auto-select partners, does not
authorize release wording, and does not authorize public speedup, broad RT-core,
or true-zero-copy claims.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3929_numba_reference_parity_expectations_test tests.goal3928_numba_reference_discovery_index_test
```

Expected: all tests pass.
