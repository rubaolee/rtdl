# Handoff: Claude Review Goal3388 Boundary-Event Tolerance Sweep

Please perform a read-only external review of Goal3388.

## Context

Goal3387 accepted Goals 3385/3386 with boundary and requested larger CDB slice
evidence plus a deterministic tolerance policy before the boundary-event signal
could be considered for route promotion.

Codex then implemented Goal3388:

- script: `scripts/goal3388_boundary_event_tolerance_signal_slice_sweep.py`
- artifact: `docs/reports/goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.json`
- report: `docs/reports/goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.md`
- test: `tests/goal3388_boundary_event_tolerance_signal_slice_sweep_test.py`

Goal3388 sweeps 512/1024/2048 chain slices from `br_county.cdb` using live
OptiX candidate device columns and live OptiX boundary-event device columns.
The exact OptiX output is used only as an evaluation oracle.

The selected-point signal is:

```text
candidate_count > strict_zero_boundary_candidate_count
and strict_zero_boundary_candidate_count <= 2
```

The selected-row filter is:

```text
selected_candidate_pair_has_boundary_crossing_t_within_tolerance
```

with `crossing_tolerance = 1e-5`.

Result summary:

| Chains | Candidate rows | Exact rows | Extras before filter | Selected false-positive points | Dropped rows | Match |
| ---: | ---: | ---: | ---: | --- | ---: | --- |
| 512 | 1429 | 1417 | 12 | 633, 634, 635 | 12 | true |
| 1024 | 2844 | 2827 | 17 | 633, 634, 635 | 17 | true |
| 2048 | 5672 | 5619 | 53 | 633, 634, 635 | 53 | true |

All claim-boundary flags remain false.

## Validation Already Run By Codex

Local:

```powershell
$env:PYTHONPATH='src;.'; py -3 -m unittest `
  tests.goal3388_boundary_event_tolerance_signal_slice_sweep_test `
  tests.goal3386_boundary_event_signal_selective_route_probe_test `
  tests.goal3385_selective_boundary_event_cupy_filter_test `
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test
```

Result: `Ran 16 tests ... OK (skipped=2)`.

Pod at commit `ce87b13a`:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal3388_boundary_event_tolerance_signal_slice_sweep_test \
  tests.goal3386_boundary_event_signal_selective_route_probe_test \
  tests.goal3385_selective_boundary_event_cupy_filter_test \
  tests.goal3383_owner_face_ambiguity_signal_negative_probe_test
```

Result: `Ran 16 tests ... OK`.

## Review Questions

1. Does Goal3388 genuinely address the larger-slice and tolerance-policy gap
   raised in Goal3387, within its stated scope?
2. Is the tolerance policy (`abs(crossing_t) <= 1e-5`) documented and bounded
   enough for this internal characterization, without overclaiming route
   readiness?
3. Does the selected-point signal stay independent from the exact oracle?
4. Is the over-selection of points `633, 634, 635` correctly framed as bounded
   and safe because the final filtered row set still matches exact?
5. Are the claim boundaries correct: no release, no public speedup, no RayJoin
   paper reproduction, no RTDL-beats-RayJoin, no RT-core speedup, no true
   zero-copy, no native default route?
6. What should be the next gate: full `br_county`, other CDB families,
   overflow/tolerance stress, native lowering deferral, or something else?

## Output

Write the review to:

`docs/reviews/goal3389_claude_review_goal3388_boundary_event_tolerance_sweep_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`,
`needs-more-evidence`, or `reject`.

This is a review only. Please do not edit source code.
