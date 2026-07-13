# Call For Review — Goal4902 Reusable Prepared Point-Location Session Probe

Date: 2026-07-03

Please critically review Goal4902.

## Primary Report

- `history/internal_docs/goal4902_reusable_point_location_session_report_2026-07-03.md`

## Evidence

- `history/internal_docs/goal4902_reusable_point_location_session_summary_2026-07-03.json`
- `history/internal_docs/goal4901_phase_accounting_summary_2026-07-03.json`
- `history/internal_docs/goal4901_accounted_harness_verify_summary_2026-07-03.json`

## Code Surface

- `history/internal_docs/goal4902_reusable_point_location_session_probe.py`

## Requested Verdict Labels

- `approve_goal4902_reusable_point_location_session_probe`
- `approve_with_required_amendments`
- `block_due_to_metric_reframing`
- `block_due_to_correctness_or_semantics_risk`

## Questions

1. Does Goal4902 correctly use the existing generic prepared point-location session shape rather than adding a RayJoin-specific shortcut?
2. Does it preserve byte-for-byte correctness on both hot-body repeats?
3. Is the distinction between setup cost and hot-body cost honest?
4. Is the measured hot-body speedup, about `1.64x` versus Goal4901 steady-state repeat, correctly bounded to repeated-query/session-reuse workloads?
5. Does the report avoid claiming a single-run speedup or author hot-kernel parity?
6. Is the next bottleneck conclusion correct: after session reuse, writer/output-chain emission is the largest hot-body phase, followed by LSI and vertex PIP?
7. Should Goal4902 close and authorize a next measured goal targeting writer/output-chain bulk emission, if we continue immediate app-layer performance work?

## Non-Authorization Boundary

This review must not authorize:

- broad RTDL/RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- single-run speedup claims from a hot-session measurement;
- LSI/PIP semantic changes;
- RayJoin-specific hidden kernels;
- V3/V4 release resurrection;
- public release/tag decisions.
