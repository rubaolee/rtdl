# Codex + Claude 2-AI Consensus: Phoenix V3 M37 Component-Union Core Node

Date: 2026-06-23

Status: `m37_component_union_core_node_2ai_consensus_continue_not_release`

Codex verdict: `accept_m37_component_union_core_node_continue`

Claude verdict:
`accept_m37_component_union_core_node_continue`

Claude recorded review:
`docs/reviews/claude_phoenix_v3_m37_component_union_core_node_recorded_review_2026-06-23.md`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
all_app_pod_spend_authorized: false
v4_work_authorized: false
performance_claim_authorized: false
```

## Consensus

M37 is accepted as a local Phoenix V3 runtime-trunk step. It is not release
evidence and not a material performance claim.

Accepted facts:

- `run_radius_graph_component_union_3d_prepared_session` exists as a generic
  runner-callable component-union core node.
- Component-union accounting is split from component-signature accounting.
- The helper fails closed when signature output is treated as union output.
- The helper now requires a real `component_labels` output column before
  `component_label_pass_accounted` can be true.
- M36's grouped-vector real-adapter metadata carry-forward is locally gated:
  `row_count` and `group_count` are preserved by the real prepare/run metadata
  path.
- Top-level `rtdsl` exports are repaired and now machine-gated against
  prepared-session surface drift.
- The current local prepared-session surface is 13 public helpers: 9 Step-4
  ready by local audit, 1 blocked Set-A seed, and 3 blocked Set-B controls.

## Validation

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 117
Ran 608 tests in 74.624s
OK
stdout: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stdout.txt
stderr: docs/rebuild/v3/evidence/phoenix_v3_latest_v3_rebuild_matrix_after_m37_label_column_tightening_20260623_134306.stderr.txt
```

## Next Step

Do not run all-app. Do not make public speedup claims.

The next useful Phoenix V3 work is M38 local protocol work for one focused
component-union POD probe, or first addressing the remaining blocked Set-A seed
if we decide the fixed-radius count-threshold helper should be promoted before
POD spend. Either path needs a bounded review packet before paid POD execution.

## Goal-Level Decision Audit

Decision: accept M37 as structurally complete after Claude review and local
label-column tightening, but keep release/all-app/performance claims blocked.

1. Was I foolish?

   No.

2. If yes, what actions made the decision foolish?

   The foolish action would be treating an accepted local core-node shape as a
   performance result or using it to unlock all-app POD spend.

3. Was there another path?

   Yes. Ignore Claude's label-column observation and close M37 without the
   tighter guard. That path was avoided by applying the small fail-closed
   improvement and rerunning the full matrix.

4. Can I now try a different path that actually solves the problem?

   Yes. M37 now exposes the union pass as a generic node. The next path is a
   focused, reviewed same-contract probe or a local promotion of the remaining
   blocked Set-A seed; not route-specific RTDBSCAN tuning.

## Non-Authorization

This consensus authorizes no V3 release, no all-app POD spend, no public
speedup claims, no broad V3-over-V2.x claims, no true-zero-copy wording, no
automatic partner selection, no V4 work, no C ABI work, and no embedding work.
