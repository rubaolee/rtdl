# Phoenix V3 M70 RTNN Focused Protocol Draft

Status: `m70_rtnn_focused_protocol_draft_ready_for_review_no_execution_no_pod_no_release`

## Bottom Line

M70 is a no-execution focused protocol draft. It names the exact frozen
RTNN ranked-summary shapes, their same-contract incumbents, the phase
metrics that must remain separated, and the stop conditions for any later
harness. It authorizes no runbook, no POD, no all-app run, no release, and
no public performance claim.

## Scope

- Family: `fixed_radius_ranked_summary_3d_prepared_session`
- Productized app mode: `prepared_execution_ranked_summary`
- Current front door: `prepared_optix_ranked_summary`
- Shape groups: `7`
- Frozen RTNN rows: `14`
- Next step if accepted: `M71_local_rtnn_harness_design_or_dry_run_gate_no_pod`

## M69 Carry-Forward

- repeat50 phase attribution is uniform-distribution evidence only
- per-distribution phase bounds are required before clustered or shell protocol use
- prepared_execution_ranked_summary currently requires full-batch self-queries
- exact frozen RTNN shapes and same-contract incumbents must be named
- 0.988781x hot-query boundary must remain visible
- exact aggregate, productized prepared-session runner, graph partner bridge, and diagnostic rows must not be merged

## Frozen Shapes

| Shape | distribution | points | geomean V3/V2 | rows | phase bound |
| --- | --- | ---: | ---: | ---: | --- |
| `clustered:262144:rtnn_clustered_262144_ranked_summary` | `clustered` | `262144` | `0.971369x` | `2` | `true` |
| `clustered:65536:rtnn_clustered_65536_ranked_summary` | `clustered` | `65536` | `1.082892x` | `2` | `true` |
| `shell:262144:rtnn_shell_262144_ranked_summary` | `shell` | `262144` | `0.982728x` | `2` | `true` |
| `shell:65536:rtnn_shell_65536_ranked_summary` | `shell` | `65536` | `0.986102x` | `2` | `true` |
| `uniform:262144:rtnn_uniform_262144_ranked_summary` | `uniform` | `262144` | `1.005881x` | `2` | `false` |
| `uniform:65536:prepared_3d_ranked_summary` | `uniform` | `65536` | `1.000733x` | `2` | `false` |
| `uniform:65536:rtnn_uniform_65536_ranked_summary` | `uniform` | `65536` | `0.997491x` | `2` | `false` |

## Same-Contract Incumbents

- `clustered:262144:rtnn_clustered_262144_ranked_summary`
  - `rtnn_embree_clustered_262144_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_clustered_262144_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)
- `clustered:65536:rtnn_clustered_65536_ranked_summary`
  - `rtnn_embree_clustered_65536_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_clustered_65536_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)
- `shell:262144:rtnn_shell_262144_ranked_summary`
  - `rtnn_embree_shell_262144_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_shell_262144_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)
- `shell:65536:rtnn_shell_65536_ranked_summary`
  - `rtnn_embree_shell_65536_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_shell_65536_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)
- `uniform:262144:rtnn_uniform_262144_ranked_summary`
  - `rtnn_embree_uniform_262144_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_uniform_262144_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)
- `uniform:65536:prepared_3d_ranked_summary`
  - `rtnn_embree_prepared_3d_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_prepared_3d_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)
- `uniform:65536:rtnn_uniform_65536_ranked_summary`
  - `rtnn_embree_uniform_65536_ranked_summary` -> `frozen_v2_14_embree_ranked_summary_row` (same-contract embree fixed-radius ranked-summary aggregate incumbent)
  - `rtnn_optix_uniform_65536_ranked_summary` -> `legacy_app_front_door_prepared_optix_ranked_summary` (prepared_optix_ranked_summary)

## Phase Metric Contract

These metrics must remain separate:

- `input_load_sec`
- `input_pack_sec`
- `input_load_pack_sec`
- `execution_prepare_sec`
- `runner_after_input_load_pack_sec`
- `hot_query_median_sec`
- `runner_wall_sec`
- `measured_total_sec`
- `measured_median_sec`
- `signature_match_status`

M69 reference, uniform-distribution repeat50 only:

- Total runner-wall delta: `0.866893s`
- Input load/pack share: `0.323`
- Runner-after-pack share: `0.677`
- Execution-prepare delta: `0.357405s`
- Hot-query speedup vs legacy: `0.988781x`

## Future Harness Requirements

- Status: `requirements_only_no_execution`
- Commands present: `false`
- Authorization token present: `false`

## Stop Conditions

- Stop if a future harness lacks a reviewed local dry-run gate.
- Stop if any frozen RTNN shape lacks an exact same-contract incumbent row.
- Stop if clustered or shell rows reuse the uniform repeat50 phase split without per-distribution measurement.
- Stop if non-self-query batches are proposed without separate code-path review.
- Stop if input-loading/packing, prepare, runner-after-pack, hot-query, and runner-wall metrics are merged.
- Stop if exact aggregate, productized prepared-session runner, graph partner bridge, raw rows, or paper diagnostic rows are merged into one claim.
- Stop if the result is only input-loading/packing consolidation or repeat50 amortization with no runner-after-pack contribution.
- Stop if productized runner metadata does not show prepared_execution_session_runner and runtime_trunk_executes_end_to_end=true.
- Stop if any public, release, all-app, POD, V4, embedding, C ABI, true-zero-copy, route-specific tuning, or watch-row closure wording appears.

## Checks

- `m69_3ai_accepts_protocol_draft_only`: `true`
- `claude_carry_forward_present`: `true`
- `antigravity_carry_forward_present`: `true`
- `m69_audit_complete`: `true`
- `all_14_rows_named`: `true`
- `all_7_shape_groups_named`: `true`
- `all_rows_have_same_contract_incumbents`: `true`
- `distribution_bounds_required`: `true`
- `full_batch_self_query_constraint_source_present`: `true`
- `generic_helper_present`: `true`
- `phase_metrics_separated`: `true`
- `no_commands_or_authorization_token`: `true`
- `all_non_authorization_flags_false`: `true`

Failed checks: `0`

## Non-Authorization

This protocol draft authorizes no V3 release, no all-app benchmark run, no
POD spend, no paid POD spend, no focused POD spend, no runbook execution,
no public speedup wording, no broad V3-over-V2 claim, no whole-app
speedup claim, no paper reproduction claim, no RT-core speedup claim, no
V4 work, no embedding, no C ABI, no true-zero-copy claim, no automatic
partner selection, no route-specific RTNN app tuning, and no watch-row
closure.

## Goal-Level Decision Audit

Decision: draft a focused RTNN protocol without execution after M69 accepted RTNN as bridgeable but not runbook-ready.

1. Was I foolish? No. M70 preserves M69's no-execution boundary and turns the review debt into explicit protocol gates.
2. If yes, what actions made the decision foolish? It would be foolish to use M69's repeat50 runner-wall signal as execution authorization or to hide the 0.988781x hot-query boundary.
3. Was there another path? Jump directly to POD or tune RTNN app routes. That repeats leaf-first work and ignores the frozen all-app gap.
4. Can I now try a different path that actually solves the problem? Freeze exact shapes, same-contract incumbents, per-distribution requirements, separated phase metrics, and fail-closed stop conditions for external review.
