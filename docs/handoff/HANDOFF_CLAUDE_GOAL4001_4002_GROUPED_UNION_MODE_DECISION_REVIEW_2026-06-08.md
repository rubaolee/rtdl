# Handoff: Claude Review Goal4001-4002 Grouped-Union Mode Decision

Please perform a read-only review of the Goal4001/Goal4002 grouped-union
actual-radius telemetry and direct-side-effect app decision. Write the review
to:

`docs/reviews/goal4003_claude_review_goal4001_4002_grouped_union_mode_decision_2026-06-08.md`

## Files To Inspect

- `docs/reports/goal4001_actual_radius_grouped_union_extended_telemetry_2026-06-08.md`
- `docs/reports/goal4001_actual_radius_exttelemetry_pod/*.json`
- `tests/goal4001_actual_radius_grouped_union_extended_telemetry_test.py`
- `docs/reports/goal4002_grouped_union_direct_side_effect_app_probe_2026-06-08.md`
- `docs/reports/goal4002_direct_side_effect_app_probe_pod/*.json`
- `tests/goal4002_grouped_union_direct_side_effect_app_probe_test.py`
- `docs/research/future_version_to_do_list.md`

## Questions

1. Does Goal4001 correctly interpret actual-radius extended telemetry: same-root
   culling is required, disabling it is slower, and the remaining bottleneck is
   candidate traversal/root-read work rather than reported any-hit union?
2. Does Goal4002 correctly reject promoting
   `grouped_union_direct_side_effect=True` as a default despite matching app
   signatures, given mixed app-level timing?
3. Are the reports claim-boundary clean?
4. Is the recommended next direction reasonable: a generic device-resident
   partition/convergence hybrid rather than another mode knob?
5. What design risks should the next native implementation goal explicitly
   guard before editing the OptiX grouped-union path?

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`. Lead with findings and required-before-next-step items.
