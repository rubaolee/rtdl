# Phoenix V3 Barnes-Hut Blocker Intake M7

Status: `barnes_hut_focused_fix_intake_not_release`

This is a planning and evidence-intake packet, not a release packet.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
full_all_app_rerun_authorized_by_this_packet: false
```

## Result

- Frozen Barnes-Hut app geomean: `0.844197x`
- Projected Barnes-Hut app geomean after focused generic fix: `1.008971x`
- Frozen all-row geomean: `1.011779x`
- Projected all-row geomean if only Barnes-Hut rows supersede: `1.032810x`
- Runner vs existing fused-control geomean: `0.999328x`
- Historical OptiX frontier over runner geomean: `12.730691x`

Interpretation: the old Barnes-Hut severe regression is covered by a
generic prepared OptiX fixed-radius symbol/library-cache fix for planning
purposes, pending the next reviewed full all-app paired run. This does not
authorize release or public performance wording.

## Replacement Rows

| row | frozen speedup | focused patched speedup |
| --- | ---: | ---: |
| `goal2626_large / barnes_hut_embree_node_coverage` | 1.016x | 1.032x |
| `goal2626_large / barnes_hut_optix_node_coverage` | 0.622x | 0.999x |
| `goal2636_stress / barnes_hut_embree_node_coverage_bodies_131072` | 1.007x | 1.006x |
| `goal2636_stress / barnes_hut_optix_node_coverage_bodies_131072` | 0.961x | 0.990x |
| `goal2636_stress / barnes_hut_embree_node_coverage_bodies_32768` | 1.002x | 0.990x |
| `goal2636_stress / barnes_hut_optix_node_coverage_bodies_32768` | 0.591x | 1.038x |

## Checks

| check | pass |
| --- | --- |
| `all_six_barnes_hut_rows_replaced` | `true` |
| `focused_metric_sources_match` | `true` |
| `focused_patch_removes_barnes_hut_severe_regression_projection` | `true` |
| `runner_parity_packet_failed_checks_empty` | `true` |
| `runner_parity_with_existing_fused_partner` | `true` |
| `runner_claim_flags_false` | `true` |

## Next Resource Decision

do_not_spend_more_barnes_hut_pod_time_before_attacking_librts_spatial_rayjoin_or_rtnn_rows

## Goal-Level Decision Audit

Decision: Reclassify Barnes-Hut from active severe-regression target to focused-fix-covered pending full-suite validation.

1. Was I foolish? No for this decision.
2. If yes, what actions made it foolish? It would be foolish to keep tuning Barnes-Hut after the generic fixed-radius OptiX hot-path regression is already covered, or to claim release from a focused replacement projection.
3. Was there another path? Run another Barnes-Hut POD or a full all-app suite immediately. That would spend money before the remaining non-Barnes blockers are addressed.
4. Can I now try a different path that actually solves the problem? Record the focused fix, preserve release non-authorization, and redirect engineering to the next unfixed shared-runtime blocker.
