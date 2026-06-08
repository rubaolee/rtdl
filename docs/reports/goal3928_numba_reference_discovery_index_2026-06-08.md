# Goal3928 Numba Reference Discovery Index

Date: 2026-06-08

## Purpose

Goal3926's Gemini review accepted the Goal3924-3925 Numba coverage work and
recommended making Numba reference implementations easier to discover. Goal3928
adds a narrow advisory helper:

`rtdsl.v2_6_numba_reference_index()`

The helper is built from the existing v2.6 partner-choice guidance rows, so it
does not create a second source of truth. It answers one user-facing question:

> For the ten benchmark apps, where does a Numba reference exist, and is a
> custom partner required for the reference path?

## Changes

- Added `V2_6_NUMBA_REFERENCE_INDEX_VERSION`.
- Added `v2_6_numba_reference_index()`.
- Made every `numba_role` string explicitly name Numba.
- Exported the helper from `rtdsl`.
- Updated `docs/learn/benchmark_partner_reference_matrix.md` to mention the
  helper.

## Boundary

The helper is advisory only. It does not auto-select partners, promote Numba
globally, demote CuPy where CuPy remains the fastest measured reference,
authorize release wording, authorize public speedup claims, authorize broad
RT-core claims, authorize true-zero-copy wording, or add native engine behavior.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3928_numba_reference_discovery_index_test tests.goal3925_numba_custom_partner_coverage_after_local_smokes_test tests.goal3054_v2_6_partner_choice_guidance_test
```

Expected: all tests pass.
