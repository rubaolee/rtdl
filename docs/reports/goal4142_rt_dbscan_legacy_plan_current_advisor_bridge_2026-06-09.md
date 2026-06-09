# Goal4142 - RT-DBSCAN Legacy Plan / Current Advisor Bridge

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4142 resolves the reviewer carry-forward that `plan_rt_dbscan_execution`
still reflected older Goal2425 route thresholds while the newer
`explain_rt_dbscan_explicit_route_choice` advisor carried the current
Goal4117-Goal4139 factor evidence.

## Change

`plan_rt_dbscan_execution` remains a legacy compatibility execution surface for
the `planned_rt_dbscan` CLI mode. It still returns a concrete `selected_mode`
using the older Goal2425 thresholds, so existing smoke tests and historical
planned-mode artifacts stay comparable.

The plan now also embeds:

- `current_route_guidance_source` set to the Goal4139 advisor;
- `current_route_advisor`, the full advisory packet from
  `explain_rt_dbscan_explicit_route_choice`;
- `current_route_first_option`, the nearest current evidence row for the
  requested dataset/scale and one-shot intent;
- explicit non-authorization flags for hidden dispatch, automatic partner
  selection, and automatic partition-cell-factor selection;
- a `selected_mode_boundary` explaining that the legacy selected mode is not the
  modern route/factor authority.

## Boundary

This goal does not promote `planned_rt_dbscan` to a hidden dispatcher and does
not change native code. It does not authorize automatic route selection,
automatic partner selection, automatic factor selection, release, public
speedup wording, broad RT-core wording, paper reproduction, app-specific engine
logic, AMD claims, or true-zero-copy claims.

The current advisor remains the user-facing route guidance surface. The legacy
planned mode is kept only for compatibility and historical smoke coverage.
