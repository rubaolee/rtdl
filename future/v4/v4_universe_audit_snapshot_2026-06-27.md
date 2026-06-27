# V4 Universe Audit Snapshot

Date: 2026-06-27

Status: `pass_with_known_local_debris`

## Counts

- tracked files: `27673`
- untracked files: `671`
- public current files scanned: `31`

## Tracked Buckets

- `audit_provenance`: `1171`
- `current_code_or_gate`: `4356`
- `history_archive`: `22046`
- `other_tracked`: `69`
- `public_current`: `31`

## Tracked Documentation Buckets

- `audit_provenance`: `559`
- `current_code_or_gate`: `4`
- `history_archive`: `14343`
- `other_tracked`: `7`
- `public_current`: `19`

## Tracked Code Buckets

- `audit_provenance`: `13`
- `current_code_or_gate`: `4333`
- `history_archive`: `328`
- `other_tracked`: `62`
- `public_current`: `12`

## Public Surface Findings

- none

## Untracked Buckets

- `local_build_output`: `2`
- `local_external_checkout`: `1`
- `local_raw_v4_evidence`: `329`
- `local_v4_review_working_record`: `339`

## Untracked Samples

### `local_build_output`
- `dist/goal4722_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
- `dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl`
### `local_external_checkout`
- `external/RT-BarnesHut-author/`
### `local_raw_v4_evidence`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_1m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_checkout_diff.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_synthetic25m_stderr.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_synthetic25m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/author_treelogy_10m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stderr.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`
- `future/v4/evidence/v4_goal4635_component_union_pod_gate_embree_2026-06-25/pid`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/legacy_app_front_door_prepared_optix.stderr.txt`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/productized_prepared_execution_runner.stderr.txt`
- `future/v4/evidence/v4_goal4636_threshold_summary_pod_gate_2026-06-25/same_contract_embree.stderr.txt`
- `future/v4/evidence/v4_goal4636b_grouped_any_hit_pod_gate_2026-06-25.tgz`
### `local_v4_review_working_record`
- `future/v4/reviews/antigravity_prompt_v4_goal4720_4722_release_candidate_review_2026-06-26.txt`
- `future/v4/reviews/antigravity_v4_goal4616_status_ledger_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_promotion_decision_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4617_grouped_i64_promotion_decision_review_retry_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4618_point_group_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4618_point_group_promotion_decision_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4621_catalog_hardening_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4622_tier3_callback_protocol_completion_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4623_development_state_decision_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4624_development_state_naming_cleanup_review_2026-06-24.stderr.txt`
- `future/v4/reviews/antigravity_v4_goal4625_design_status_and_next_goals_amended_review_2026-06-24.stderr.txt`

## Interpretation

Public V4 current surface must be clean. history/ is archival. future/ is audit provenance. Known untracked raw evidence, review working records, and local debris are not public V4 files. Use --strict-release before a final tag/package gate to require a debris-free local tree.
