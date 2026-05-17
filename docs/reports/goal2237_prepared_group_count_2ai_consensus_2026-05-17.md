# Goal2237: Prepared Group-Count 2-AI Consensus

Status: accepted with boundary.

## Evidence

- Codex implementation/report: `docs/reports/goal2233_prepared_ray_segment_group_count_2026-05-17.md`
- Codex implementation/report: `docs/reports/goal2235_prepared_ray_segment_odd_parity_2026-05-17.md`
- Gemini review: `docs/reviews/goal2236_gemini_review_goal2233_2235_prepared_group_count_2026-05-17.md`
- Tests:
  - `tests/goal2233_prepared_ray_segment_group_count_test.py`
  - `tests/goal2235_prepared_ray_segment_odd_parity_test.py`

## Consensus

Codex and Gemini agree that Goal2233 and Goal2235 are valid, app-agnostic
OptiX primitive improvements:

- prepared ray/segment group-count scene reuse is implemented,
- compact odd-parity output is implemented,
- the API uses ray, segment, group, count, and parity vocabulary,
- RTX pod build and functional probes passed,
- the RayJoin-style 10,000-query probe matched legacy positive rows exactly.

## Performance Boundary

The accepted claim is narrow:

- Goal2233 reduced the generic full-count path from the earlier unprepared
  1.476056-second median to 0.820912 seconds.
- Goal2235 reduced the prepared full-count run from 0.724264 seconds to
  0.282348 seconds by returning only odd-parity rows.
- Compact odd-parity output matched the legacy optimized positive row set:
  879 rows.

This does not authorize a RayJoin speedup claim. The compact odd-parity path was
still 8.96x slower than the legacy optimized positive-output PIP path in the
Goal2235 pod probe.

## Remaining Work

The next performance target is a still-generic closed-shape membership or
caller-supplied predicate primitive. The engine must not regress to app-named
RayJoin or PIP exports, and these goals do not close the v2.0 release gate.
