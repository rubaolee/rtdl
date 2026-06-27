# Claude Phoenix V3 Route Capability Map Review

Reviewer: Claude Code, independent compact no-tools review distinct from Codex.

Date: 2026-06-20.

## Review

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

- Coverage and capability-naming look sound: all 19 rows mapped to named
  generic capabilities, P0/P1 tiers reflect the right candidates
  (`component_union`, `grouped_reduction`, topology stream,
  `prepared_graph_chunk`, `ranked_summary`, `aggregate_frontier`), and the
  Barnes-Hut `P0_blocked` flag for the paired V3-vs-V2 regression is the
  correct cherry-pick guard rather than quietly dropping or reclassifying that
  row.
- The denominator discipline is correct in principle: 46-row V2.14-vs-V3,
  1.012x geomean preserved, subset geomeans labeled as subset. However, since
  `release_authorized=false` and Phoenix M7-qualified release rows are zero,
  this summary cannot be cited as release evidence yet; that gating status
  needs to be stated explicitly alongside the map wherever it is referenced
  downstream, not just implied by the flags.
- Required amendment: confirm `threshold_summary` for Hausdorff and
  `aabb_candidate_stream` / `collision_flag_stream` P1 rows do not get a
  narrower geomean computed and presented without the `subset` label in any
  consuming doc. The policy is correct here, but enforcement depends on every
  downstream consumer respecting it, so add an explicit cross-check or lint
  rather than relying on convention.
