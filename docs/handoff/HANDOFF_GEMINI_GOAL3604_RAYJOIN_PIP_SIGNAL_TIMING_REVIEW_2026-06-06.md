# Handoff: Gemini Review Goal3604 RayJoin PIP Boundary-Event Signal Timing

Please perform a read-only independent Gemini review of Goal3604 and write the review to:

`docs/reviews/goal3605_gemini_review_goal3604_rayjoin_pip_signal_timing_2026-06-06.md`

## Context

Goal3604 turns the earlier constructive RayJoin PIP boundary-event signal route into a timing packet on the A5000 pod.

The route is:

1. OptiX candidate device columns.
2. OptiX first-boundary-event device columns.
3. CuPy selected-point derivation from candidate and strict-zero boundary-event counts.
4. CuPy selective boundary-event filter with `crossing_tolerance=1e-5`.

It remains exact on 512/1024/2048 public-CDB county slices, but it is much slower than the dense CuPy scalar-count baseline.

## Files To Read

- `docs/reports/goal3604_rayjoin_pip_boundary_event_signal_timing_2026-06-06.md`
- `docs/reports/goal3604_rayjoin_pip_boundary_event_signal_timing_a5000/summary.json`
- `scripts/goal3604_rayjoin_pip_boundary_event_signal_timing.py`
- `tests/goal3604_rayjoin_pip_boundary_event_signal_timing_test.py`
- `docs/research/future_version_to_do_list.md`

Useful prior context:

- `docs/reports/goal3386_boundary_event_signal_selective_route_probe_2026-06-04.md`
- `docs/reports/goal3388_boundary_event_tolerance_signal_slice_sweep_2026-06-04.md`
- `docs/reports/goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md`

## Review Questions

1. Does Goal3604 accurately conclude that the boundary-event signal route is correct but not performance-ready?
2. Are the reported CuPy, prepared OptiX exact, and boundary-event signal ratios computed and interpreted correctly?
3. Is the route-selection guidance correct: CuPy dense for current public-CDB PIP scalar count, prepared OptiX exact for no-partner RTDL-only count, no default promotion for boundary-event signal?
4. Does the script remain generic and app-agnostic at the engine level?
5. Are the claim boundaries strong enough?

## Required Review Shape

- Start with `Verdict: accept`, `Verdict: accept-with-boundary`, `Verdict: needs-more-evidence`, or `Verdict: reject`.
- State that this is an independent Gemini review, distinct from Codex.
- Lead with findings ordered by severity.
- Include file-level references.
- Do not edit source, report, or artifact files except for writing the review file above.
