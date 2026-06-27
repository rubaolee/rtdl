# Phoenix V3 M69 RTNN Phase/Shape Bridge Audit

Status: `m69_rtnn_phase_shape_bridge_audit_ready_for_external_review_no_pod_no_release`

## Bottom Line

M69 finds RTNN bridgeable to the generic fixed-radius ranked-summary
prepared-session runner, but not runbook-authorized. The existing
repeat50 evidence is not hot-query speedup and must not be described as
whole-RTNN or broad V3-over-V2 performance.

- Frozen RTNN all-app rows: `14`
- Rows below `1.05x`: `13`
- Shape groups below `1.05x`: `6`
- Bridge status: `bridgeable_but_not_runbook_authorized`
- Next recommended goal: `M70_draft_reviewed_rtnn_focused_protocol_no_execution`

## Phase Attribution

- Total runner-wall delta: `0.866893s`
- Input load/pack delta: `0.279946s`
- Input load/pack share: `0.323`
- Runner-after-pack delta: `0.586967s`
- Runner-after-pack share: `0.677`
- Execution-prepare delta: `0.357405s`
- Hot-query speedup vs legacy: `0.988781x`

The repeat50 runner-wall win is not hot-query speedup and is not input-loading/packing only. It is split across input packing, prepare/session reuse, and runner-after-pack phases.

## RTNN Shape Groups

| Shape | geomean V3/V2 | min | max | rows below 1.05x |
| --- | ---: | ---: | ---: | ---: |
| `clustered:262144:rtnn_clustered_262144_ranked_summary` | `0.971369x` | `0.945682x` | `0.997755x` | `2` |
| `clustered:65536:rtnn_clustered_65536_ranked_summary` | `1.082892x` | `1.020539x` | `1.149054x` | `1` |
| `shell:262144:rtnn_shell_262144_ranked_summary` | `0.982728x` | `0.972806x` | `0.992751x` | `2` |
| `shell:65536:rtnn_shell_65536_ranked_summary` | `0.986102x` | `0.980927x` | `0.991304x` | `2` |
| `uniform:262144:rtnn_uniform_262144_ranked_summary` | `1.005881x` | `0.992278x` | `1.019670x` | `2` |
| `uniform:65536:prepared_3d_ranked_summary` | `1.000733x` | `0.997864x` | `1.003609x` | `2` |
| `uniform:65536:rtnn_uniform_65536_ranked_summary` | `0.997491x` | `0.994313x` | `1.000678x` | `2` |

## Bridge Decision

- All-app shape bridge candidate: `true`
- Runbook authorized now: `false`
- POD authorized now: `false`
- All-app authorized now: `false`

Required before any later runbook:

- external review accepts M69 phase/shape bridge
- protocol names exact frozen RTNN shapes and same-contract incumbent
- protocol records that repeat50 phase attribution currently comes from the uniform distribution only
- protocol requires per-distribution phase bounds before using clustered or shell shapes
- protocol carries the full-batch self-query constraint for prepared_execution_ranked_summary
- protocol keeps hot-query, runner-wall, prepare, and input-load/pack metrics separate
- protocol preserves no release/all-app/POD/public-claim boundaries until separately authorized

Stop conditions:

- Stop if external review rejects the all-app shape bridge.
- Stop if the bridge requires app-specific RTNN native logic.
- Stop if the positive signal is only repeat50 amortization with no shape bridge.
- Stop if phase attribution shows only input-loading/packing consolidation and no runner-after-pack or prepare/session contribution.
- Stop if a later protocol extrapolates the uniform repeat50 phase split to clustered or shell without per-distribution evidence.
- Stop if a later protocol proposes non-self-query batches without separate code-path review.
- Stop if exact aggregate, graph partner bridge, and productized prepared-session contracts are mixed into one public claim.

## Checks

- `m68_authorizes_m69_local_audit_only`: `true`
- `rtnn_rows_present`: `true`
- `rtnn_rows_all_ranked_summary`: `true`
- `rtnn_app_geomean_below_threshold`: `true`
- `rtnn_rows_mostly_below_threshold`: `true`
- `front_door_currently_legacy_prepared_optix`: `true`
- `productized_runner_mode_exists`: `true`
- `productized_runner_calls_generic_helper`: `true`
- `prepared_helper_generic`: `true`
- `distribution_bridge_supported`: `true`
- `route_decision_keeps_contracts_separate`: `true`
- `phase_attribution_not_input_pack_only`: `true`
- `phase_attribution_hot_query_boundary_recorded`: `true`
- `phase_attribution_runner_after_pack_positive`: `true`
- `bridge_not_runbook_authorization`: `true`
- `all_non_authorization_flags_false`: `true`

Failed checks: `0`

## Non-Authorization

This packet authorizes no release, no all-app run, no POD spend, no
focused run, no runbook execution, no public speedup wording, no broad
V3-over-V2 claim, no whole-app or paper claim, no RT-core speedup claim,
no automatic partner selection, no route-specific RTNN app tuning, and
no watch-row closure.

## Goal-Level Decision Audit

Decision: Treat RTNN as bridgeable to the generic ranked-summary runner, but not yet runbook-ready until external review accepts the local phase/shape audit.

1. Was I foolish? No. M69 splits the repeat50 wall signal by phase and refuses to convert it into a hot-query or whole-app claim.
2. If yes, what actions made the decision foolish? The foolish action would be to claim the full 1.370176x runner-wall speedup as ranked-summary execution speedup, hiding the input-packing share and the 0.988781x hot-query boundary.
3. Was there another path? Jump directly to a POD runbook or rewrite RTNN app code. Both are rejected because the all-app shape bridge and phase attribution must be reviewed first.
4. Can I now try a different path that actually solves the problem? Send the local bridge audit for review. If accepted, a later goal may draft a bounded focused protocol; if rejected, return to Triangle or RTDBSCAN reserve candidates.
