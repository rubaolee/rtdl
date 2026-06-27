# Call For Review: Phoenix V3 Release Surface Breadth Gate

Reviewer requested: Claude Code
Date: 2026-06-21

## Context

Phoenix V3 is not release-ready. The current aggregate release gate already blocks release with:

- `release_authorization_false`
- `eleven_row_surface_still_too_narrow_for_major_release`
- `aggregate_release_readiness_consensus_blocks_release`

This review asks whether the new machine-readable surface-breadth gate correctly turns the old prose blocker into exact, reusable evidence:

- current M7 row-scoped surface is 11 rows;
- current M7 capability-family coverage is 7 / 9;
- missing M7 capability families are `aggregate_frontier` and `point_location_topology_stream`;
- old evidence is not promotable now;
- the gate does not authorize release, public speedup wording, or broad V3-over-V2 claims.

## Files To Review

- `scripts/v3_phoenix_release_surface_breadth_gate.py`
- `tests/v3_phoenix_release_surface_breadth_gate_test.py`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md`
- `docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json`
- `scripts/v3_phoenix_release_readiness_gate.py`
- `tests/v3_phoenix_release_readiness_gate_test.py`
- `scripts/v3_release_wording_gate.py`
- `docs/rebuild/v3/phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json`
- `docs/reviews/codex_phoenix_v3_aggregate_release_readiness_2ai_consensus_2026-06-21.md`

## Validation Already Run

```text
py -3 -m unittest tests.v3_phoenix_release_surface_breadth_gate_test tests.v3_release_wording_gate_test tests.v3_phoenix_release_readiness_gate_test
Result: 8 tests OK

py -3 scripts/run_test_matrix.py --group v3_rebuild
Result: 92 modules / 441 tests OK
```

## Review Questions

1. Is the new gate a valid machine-readable representation of the `eleven_row_surface_still_too_narrow_for_major_release` blocker?
2. Are the 7 / 9 capability coverage and missing capability-family names (`aggregate_frontier`, `point_location_topology_stream`) grounded in the current packet rather than invented?
3. Does the gate correctly avoid authorizing release, broad speedup, or public speedup claims?
4. Is the total release-readiness gate now stronger and less ambiguous after consuming this surface-breadth gate?
5. What P0/P1 fixes are still needed before this gate can be accepted as a current Phoenix V3 governance artifact?

Please return a verdict in this format:

```text
Verdict: `approve`, `approve-with-amendments`, or `reject`

P0 Findings
- ...

P1 Findings
- ...

Required Fixes
- ...

Notes
- ...
```
