# Phoenix V3 M67 Barnes-Hut Phase-Structure Pre-Audit

Status: `m67_barnes_hut_phase_structure_pre_audit_ready_for_external_review_no_pod_no_release`

## Bottom Line

M67 finds no reason to start another Barnes-Hut coding branch. The
material Barnes-Hut route already exists as the aggregate-tree fused
weighted-vector partner path routed through the productized prepared
execution session runner. The current fastest fused control has no new
compressible phase for the runner to remove; the runner preserves it at
`0.999328x` geomean.

The large material delta is against the historical prepared OptiX/frontier
predecessor only:
`12.730691x` geomean.
That is predecessor-displacement evidence, not wrapper-is-faster wording.

## Reconciliation

- M45 blocks new Barnes-Hut app tuning and classifies the old all-app
  blocker as focused-fix-covered pending full-suite validation.
- M66 redirects to a local Barnes-Hut pre-audit after RayJoin non-go.
- M67 reconciles them: audit existing productized runtime evidence, then
  ask external review whether Barnes-Hut already counts as the Step-1
  material family.

## Phase Structure

| Path | Role | Reading |
| --- | --- | --- |
| historical prepared OptiX/frontier | historical no-go predecessor, not primary public claim | compressible non-zero phase found: `true` |
| current fused Numba CUDA control | current fastest app-front-door control | new compressible phase found: `false` |
| productized runner | productized runtime-trunk carrier for the fused partner route | runtime trunk executes: `true` |

## Decision

- Status: `existing_evidence_answers_pre_audit_requires_external_counting_review`
- Barnes-Hut current coding target: `false`
- POD now authorized: `false`
- All-app now authorized: `false`
- Material source versus historical predecessor: `true`
- New material source versus current fused control: `false`

Send this M67 packet for external review. If accepted, Barnes-Hut can be counted as an existing Step-1 replacement material family and the next engineering target should move to the next Set-A family. If rejected, select a different family rather than doing Barnes-Hut app-specific tuning.

## Checks

- `m66_redirect_to_barnes_hut_pre_audit_recorded`: `true`
- `m45_blocks_new_barnes_hut_app_tuning`: `true`
- `step2_audit_requires_productized_runtime_before_pod`: `true`
- `runner_packet_status_not_release`: `true`
- `runner_parity_geomean_floor`: `true`
- `runner_parity_each_size_floor`: `true`
- `historical_predecessor_material_floor`: `true`
- `runner_runtime_trunk_all_samples`: `true`
- `runner_internal_residency_all_samples`: `true`
- `runner_no_frontier_or_contribution_host_materialization`: `true`
- `runner_control_output_equivalence`: `true`
- `m29_confirms_no_v2_14_equivalent_current_trunk_surface`: `true`
- `source_helper_is_current_and_generic`: `true`
- `app_adapter_calls_productized_helper`: `true`
- `non_authorization_flags_closed`: `true`

Failed checks: `0`

## Non-Authorization

This packet authorizes no release, no all-app run, no POD spend, no
public speedup claim, no broad V3-over-V2 claim, no RT-core speedup
claim, no whole-app speedup claim, no paper reproduction claim, no
true-zero-copy claim, no automatic partner selection, no app-specific
Barnes-Hut engine tuning, and no watch-row closure.

## Goal-Level Decision Audit

Decision: Treat Barnes-Hut M67 as a local phase-structure reconciliation audit, not a new Barnes-Hut coding branch.

1. Was I foolish? No after rereading M45/M66/M29. The foolish path would be to turn M66's redirect into more Barnes-Hut app tuning.
2. If yes, what actions made the decision foolish? The risky action would be ignoring that M45 already blocked new Barnes-Hut app tuning and that M28/M29 already productized the fused runner route.
3. Was there another path? Run another focused POD or write another Barnes-Hut-specific route. That would repeat the leaf-first mistake.
4. Can I now try a different path that actually solves the problem? Ask external review whether existing productized Barnes-Hut evidence counts as the Step-1 material family, then move to the next generic Set-A family or select a replacement.
