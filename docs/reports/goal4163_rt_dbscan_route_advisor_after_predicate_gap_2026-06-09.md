# Goal4163 RT-DBSCAN Route Advisor After Predicate Gap

Date: 2026-06-09

Status: accepted advisor hardening; no hidden dispatch.

## Purpose

Goals4158-4162 changed the RT-DBSCAN route picture:

- The predicate direct-status candidate is strong for all-predicate/default-style rows.
- Mixed-predicate rows still need a compatible generic border-assignment policy.
- Canonical component-size signatures are the right comparison contract when component label ids are arbitrary.

Goal4163 updates `explain_rt_dbscan_explicit_route_choice()` so users see this boundary before choosing a route.

## Changes

The advisor now records:

- grouped-stream Numba as the conservative route for custom mixed-predicate settings
- predicate direct-status scope as default-shape / remeasured-only
- `all_predicate_fast_path_evidence: Goal4158`
- current border policy: `lowest_predicate_true_point_id_within_radius`
- target border policy: `reference_grouped_stream_compatible`
- canonical helper: `canonical_component_size_signature`
- mixed-predicate promotion blocked by Goals4159 and 4160

## Boundary

The advisor remains non-executing and does not choose a route automatically. It only explains explicit user choices. It does not authorize route promotion, public speedup claims, release claims, hidden dispatch, automatic partner selection, or app-specific native logic.
