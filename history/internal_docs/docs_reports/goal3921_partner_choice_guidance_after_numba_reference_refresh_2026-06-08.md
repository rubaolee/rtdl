# Goal3921 Partner Choice Guidance After Numba Reference Refresh

Date: 2026-06-08

## Purpose

The benchmark-app partner guidance had drifted behind the newer Numba work. The
learner-facing matrix already describes RT-DBSCAN as having a current Numba
reference path, but the machine-readable `v2_6_partner_choice_guidance()` row
still recommended CuPy. Barnes-Hut also had newer Numba no-RawKernel evidence
that was not visible in the guidance row.

Goal3921 keeps the guidance consistent with current implementation evidence
without changing native engine behavior.

## Changes

- RT-DBSCAN `component_labeling` now recommends `numba`.
- RT-DBSCAN keeps CuPy as an established same-contract baseline/opponent.
- RT-DBSCAN records the current Numba grouped-stream/component continuation
  lineage and explicitly says blocked variants still need Goal3920 A5000 timing
  before default promotion.
- Barnes-Hut keeps CuPy as the fastest measured force-vector continuation.
- Barnes-Hut now records Numba as a measured no-RawKernel exact-force reference,
  not merely a future candidate.

## Boundary

This is an advisory metadata correction. It does not auto-select partners,
authorize public speedup claims, authorize release claims, authorize true
zero-copy wording, or add app-specific native-engine logic.

The next pod evidence remains:

- Goal3913 RayJoin subprobe runbook.
- Goal3920 RT-DBSCAN blocked Numba runbook.

## Validation

Run:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal3921_partner_choice_guidance_after_numba_reference_refresh_test tests.goal3054_v2_6_partner_choice_guidance_test
```

Expected: all tests pass.
