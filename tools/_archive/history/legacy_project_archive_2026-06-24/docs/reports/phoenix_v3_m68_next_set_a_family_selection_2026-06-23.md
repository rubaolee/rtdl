# Phoenix V3 M68 Next Set-A Family Selection

Status: `m68_next_set_a_family_selection_ready_for_external_review_no_pod_no_release`

## Bottom Line

M68 selects RTNN fixed-radius ranked-summary as the next generic Set-A
family for local, no-POD phase/shape bridge audit. This is not a
benchmark-app tuning decision. The selected mechanism is the generic
`fixed_radius_ranked_summary_3d_prepared_session` runner surface.

The reason is disciplined: Barnes-Hut is already counted internally by
M67, Spatial/RayJoin is non-go under M66, LibRTS is Set-B control work,
Hausdorff is already above the app-win threshold, and RTNN has both an
existing productized runner and a frozen all-app app-win gap.

## Selected Family

- Family: `fixed_radius_ranked_summary_3d_prepared_session`
- Pressure app: `rtnn`
- Verdict: `select_for_m69_local_phase_shape_bridge_audit_no_pod_no_release`
- Frozen Set-A app geomean: `1.003327x`
- Existing runner vs legacy runner-wall: `1.370176x`
- Existing runner vs legacy hot-query boundary: `0.988781x`
- Input load/pack consolidation in existing evidence: `0.279946s`
- Runner after input load/pack: `0.626317s`

The hot-query boundary is part of the selection. M69 must not turn the
repeat50 wall signal into a single-shot or whole-RTNN claim. It must
also separate input-packing/loading consolidation from ranked-summary
execution compression before any later runbook is considered.

## Candidate Table

| Family | Pressure app | Rank | Reason |
| --- | --- | --- | --- |
| `barnes_hut_aggregate_tree_fused_vector_sum` | `barnes_hut` | `excluded_currently` | M67 3-AI counted it internally as an existing material family and blocked more Barnes-Hut-specific work. |
| `spatial_rayjoin_topology_stream` | `spatial_rayjoin` | `excluded_currently` | M66 rejected a repeat topology-stream run because the current route removes no new physical work. |
| `fixed_radius_ranked_summary_3d_prepared_session` | `rtnn` | `selected` | Generic ranked-summary surface exists, all-app app-win is still below target, and local bridge audit can test scope before POD. |
| `triangle_prepared_graph_chunk_execution` | `triangle_counting` | `reserve_candidate` | M19 already accepted a strict focused probe; useful if RTNN bridge fails, but not the cleanest next no-POD bridge. |
| `rt_dbscan_component_union` | `rt_dbscan` | `reserve_candidate` | M40 gives component-union evidence, but M35 says the incumbent comparison is still bottlenecked by grouped-union work. |
| `hausdorff_threshold_summary` | `hausdorff_xhd` | `defer` | Already the only Set-A app above 1.05x in the frozen scorecard; less urgent for the next app-win bridge. |

## Next Work

- Goal: `M69`
- Work item: `local_rtnn_ranked_summary_phase_shape_bridge_audit`
- Scope: No-POD local audit mapping the existing fixed-radius ranked-summary prepared-session runner evidence to the frozen RTNN all-app shapes.
- POD authorized: `false`
- All-app authorized: `false`

M69 must answer:

- Which all-app RTNN rows remain below the 1.05x Set-A app-win threshold?
- Do those rows share the generic fixed_radius_ranked_summary_3d prepared-session surface?
- Is the repeat50 material signal broad enough to justify a later focused runbook?
- Which phase is actually compressible: prepare, input packing, ranked-summary aggregate, or runner process wall?
- How much of the runner-wall delta is input-loading/packing consolidation rather than ranked-summary execution compression?
- Does the next change belong in a generic ranked-summary runner/phase bridge rather than app code?

Stop conditions:

- If the only positive signal is repeat50 amortization with no all-app shape bridge, stop.
- If runner-wall improvement is attributable entirely to input-loading/packing consolidation with no ranked-summary phase compression, stop before any runbook.
- If the route requires app-specific RTNN shortcuts, stop.
- If source inspection shows no current productized ranked-summary helper, stop.
- If M69 cannot define same-contract focused evidence before POD, stop.

## Checks

- `scorecard_blocks_release`: `true`
- `scorecard_blocks_all_app_pod_spend`: `true`
- `classification_frozen`: `true`
- `m66_blocks_repeat_topology_stream_pod`: `true`
- `m67_accepts_barnes_hut_as_existing_material_family`: `true`
- `m35_blocks_rtdbscan_and_rayjoin_as_immediate_material_targets`: `true`
- `m40_component_union_already_has_focused_probe`: `true`
- `m43_grouped_reduction_already_closed_bounded_step2`: `true`
- `selected_family_is_set_a`: `true`
- `selected_family_below_app_win_threshold`: `true`
- `selected_family_not_severe_regression`: `true`
- `selected_has_productized_helper`: `true`
- `selected_helper_has_generic_contract`: `true`
- `selected_evidence_runtime_trunk_executes`: `true`
- `selected_evidence_internal_residency`: `true`
- `selected_evidence_repeat50_wall_material_signal`: `true`
- `selected_evidence_hot_query_boundary_recorded`: `true`
- `all_non_authorization_flags_false`: `true`

Failed checks: `0`

## Non-Authorization

This packet authorizes no release, no all-app run, no POD spend, no
focused run, no public speedup wording, no broad V3-over-V2 claim, no
whole-app or paper claim, no RT-core speedup claim, no automatic partner
selection, no route-specific RTNN app tuning, and no watch-row closure.

## Goal-Level Decision Audit

Decision: Select RTNN fixed-radius ranked-summary as the next generic Set-A family for local no-POD phase/shape bridge audit.

1. Was I foolish? No. The decision explicitly rejects Barnes-Hut repetition, RayJoin rerun, LibRTS Set-B drift, and app-specific RTNN shortcuts.
2. If yes, what actions made the decision foolish? The foolish action would be to quote the repeat50 wall speedup as a broad RTNN or V3 claim, or to skip the all-app shape bridge.
3. Was there another path? Pick Triangle, RTDBSCAN, Hausdorff, or Spatial immediately. Those remain valid later, but each is either already accepted, recently non-go, already above the app-win threshold, or still tied to a known continuation bottleneck.
4. Can I now try a different path that actually solves the problem? Use M69 to perform a local ranked-summary phase/shape bridge audit first, then seek review before any runbook or POD request.
