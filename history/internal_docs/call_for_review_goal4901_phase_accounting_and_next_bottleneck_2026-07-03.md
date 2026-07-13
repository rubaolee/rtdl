# Call For Review — Goal4901 Phase Accounting and Next Bottleneck

Date: 2026-07-03

Please critically review Goal4901.

## Primary Report

- `history/internal_docs/goal4901_phase_accounting_and_next_bottleneck_report_2026-07-03.md`

## Evidence Files

- `history/internal_docs/goal4901_phase_accounting_summary_2026-07-03.json`
- `history/internal_docs/goal4901_accounted_harness_verify_summary_2026-07-03.json`
- `history/internal_docs/goal4900_numba_cache_overlay_summary_2026-07-03.json`

## Code Surfaces To Inspect

- `history/internal_docs/goal4901_same_process_phase_accounting.py`
- `history/internal_docs/goal4880_section57_public_primitives_overlay_harness.py`

## Requested Verdict Labels

- `approve_goal4901_phase_accounting_gap_closed`
- `approve_with_required_amendments`
- `block_due_to_measurement_error`
- `block_due_to_overclaim_or_semantics_risk`

## Questions

1. Does Goal4901 correctly explain the former `~9.8s` unattributed gap as missing phase accounting, especially point-location preparation?
2. Does the same-process two-repeat measurement support separating cold first-run effects from steady-state route cost?
3. Does the patched harness preserve byte-for-byte correctness and only add timing scopes?
4. Is the claim boundary correct: no RT traversal speedup, no broad RayJoin speedup, no Numba-on-primitive claim?
5. Is the next target, generic reusable/prepared point-location base-map preparation, justified by the measured largest steady-state phase?
6. Is this next target generic enough for RTDL planar-map PIP, rather than a RayJoin-specific shortcut?
7. Should Goal4901 close and authorize a follow-up goal to design/measure a reusable point-location preparation surface?

## Non-Authorization Boundary

This review must not authorize:

- broad RTDL/RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- changes to LSI/PIP semantics;
- RayJoin-specific hidden kernels;
- V3/V4 release resurrection;
- public release/tag decisions.
