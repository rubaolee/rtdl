# Handoff: Claude Review For Goal3846 Stress Probe Candidates

Please perform an independent read-only review of Goal3846 and save your review
to:

`docs/reviews/goal3847_claude_review_goal3846_stress_probe_candidates_2026-06-08.md`

## Files To Inspect

- `docs/reports/goal3846_stress_probe_candidates_2026-06-08.md`
- `docs/reports/goal3846_stress_probe_candidates_a5000/`
- `tests/goal3846_stress_probe_candidates_test.py`
- Optional context:
  - `docs/reports/goal3844_current_scale_profile_refresh_2026-06-08.md`
  - `docs/reports/goal3844_current_scale_profiles_refresh_a5000/summary.json`
  - `src/rtdsl/v2_9_benchmark_adequacy.py`

## Review Questions

1. Does Goal3846 correctly distinguish hot app-reported metrics from whole
   process wall time?
2. Does the RayDB evidence support the conclusion that fused count/sum is not
   the next best primitive-runtime bottleneck?
3. Does the LibRTS evidence support treating larger AABB-index scale behavior
   as a plausible future performance target?
4. Does the triangle-counting stress row preserve the boundary that it is not
   an authorized RT-core graph-acceleration claim?
5. Are all release/public-speedup/paper-reproduction/auto-selection boundaries
   kept blocked?

## Required Review Shape

Lead with findings, ordered by severity. Use one of the project verdicts:
`accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

If accepted, state the exact boundary: this is internal A5000 stress-triage
evidence for next-target selection, not release authorization, not public
speedup wording, and not paper reproduction.
