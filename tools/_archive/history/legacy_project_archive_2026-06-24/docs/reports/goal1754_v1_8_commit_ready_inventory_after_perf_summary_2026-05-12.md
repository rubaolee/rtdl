# Goal1754 v1.8 Commit-Ready Inventory After Performance Summary

## Verdict

`v1_8_inventory_ready_pending_user_release_authorization`

The workspace contains a coherent v1.8 source-tree Python+RTDL evidence chain through Goal1762. It is not release-ready for tag/version action because explicit user release authorization is still required.

## v1.8 Decision Trail To Include

These files are the current v1.8 decision/status trail:

- `docs/reports/goal1737_v1_8_python_rtdl_gap_audit_2026-05-12.md`
- `tests/goal1737_v1_8_python_rtdl_gap_audit_test.py`
- `docs/reviews/goal1738_claude_review_goal1737_v1_8_gap_audit_2026-05-12.md`
- `docs/reviews/goal1739_gemini_review_goal1737_v1_8_gap_audit_2026-05-12.md`
- `docs/reports/goal1740_v1_8_public_docs_boundary_alignment_2026-05-12.md`
- `tests/goal1740_v1_8_public_docs_boundary_alignment_test.py`
- `docs/reports/goal1741_v1_8_source_tree_install_boundary_2026-05-12.md`
- `tests/goal1741_v1_8_source_tree_install_boundary_test.py`
- `docs/reports/goal1742_v1_8_release_candidate_evidence_packet_2026-05-12.md`
- `tests/goal1742_v1_8_release_candidate_evidence_packet_test.py`
- `docs/reviews/goal1743_gemini_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md`
- `docs/reviews/goal1745_gemini_second_pass_review_goal1742_v1_8_release_candidate_packet_2026-05-12.md`
- `docs/reports/goal1753_v1_8_decision_status_after_perf_summary_2026-05-12.md`
- `tests/goal1753_v1_8_decision_status_after_perf_summary_test.py`
- `docs/reports/goal1758_legacy_lsi_overlay_triangle_probe_native_cleanup_2026-05-12.md`
- `tests/goal1758_legacy_lsi_overlay_triangle_probe_native_cleanup_test.py`
- `docs/reports/goal1759_v1_8_release_prep_after_legacy_native_cleanup_2026-05-12.md`
- `tests/goal1759_v1_8_release_prep_after_legacy_native_cleanup_test.py`
- `docs/reviews/goal1760_claude_review_goal1759_v1_8_release_prep_2026-05-12.md`
- `docs/reviews/goal1761_gemini_review_goal1759_v1_8_release_prep_2026-05-12.md`
- `docs/reports/goal1762_v1_8_final_release_prep_consensus_2026-05-12.md`
- `tests/goal1762_v1_8_final_release_prep_consensus_test.py`
- `docs/reports/goal1763_v1_8_public_docs_and_learner_path_readiness_2026-05-12.md`
- `tests/goal1763_v1_8_public_docs_and_learner_path_readiness_test.py`
- `docs/reports/goal1764_post_v1_5_release_rule_audit_2026-05-12.md`
- `tests/goal1764_post_v1_5_release_rule_audit_test.py`
- `docs/reports/goal1765_github_learner_readiness_double_check_2026-05-12.md`
- `tests/goal1765_github_learner_readiness_double_check_test.py`
- `docs/reviews/goal1766_claude_review_goal1763_1765_release_docs_audit_2026-05-12.md`
- `docs/reviews/goal1767_gemini_review_goal1763_1765_release_docs_audit_2026-05-12.md`
- `docs/reports/goal1768_v1_8_release_authorization_readiness_after_docs_audit_2026-05-12.md`
- `tests/goal1768_v1_8_release_authorization_readiness_after_docs_audit_test.py`

## Performance Clarification Chain To Include

These files explain the v1.0 customized-engine versus current generic-engine comparison boundary:

- `scripts/goal1746_v1_0_embree_baseline_adapter.py`
- `tests/goal1746_v1_0_embree_baseline_adapter_test.py`
- `docs/reports/goal1746_v1_0_embree_baseline_adapter_manifest_2026-05-12.md`
- `docs/reports/goal1746_v1_0_embree_baseline_adapter_manifest_2026-05-12.json`
- `docs/reports/goal1746_v1_0_embree_baseline_adapter_run_2026-05-12.json`
- `docs/reports/goal1746_v1_0_*_embree.json`
- `docs/reports/goal1747_v1_0_embree_baseline_recovery_consolidation_2026-05-12.md`
- `tests/goal1747_v1_0_embree_baseline_recovery_consolidation_test.py`
- `scripts/goal1748_v1_0_embree_schema_mapper.py`
- `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.md`
- `docs/reports/goal1748_v1_0_embree_schema_mapping_2026-05-12.json`
- `tests/goal1748_v1_0_embree_schema_mapping_test.py`
- `docs/reviews/goal1749_gemini_review_goal1746_1748_embree_recovery_2026-05-12.md`
- `scripts/goal1750_same_contract_perf_summary.py`
- `docs/reports/goal1750_same_contract_perf_summary_2026-05-12.md`
- `docs/reports/goal1750_same_contract_perf_summary_2026-05-12.json`
- `tests/goal1750_same_contract_perf_summary_test.py`
- `docs/reviews/goal1751_gemini_review_goal1750_same_contract_perf_summary_2026-05-12.md`

## Handoff Files To Include Or Preserve

These handoff files explain external review attempts and can be committed if the project wants durable AI-workflow traceability:

- `HANDOFF_GEMINI_GOAL1746_1748_REVIEW.md`
- `HANDOFF_GEMINI_GOAL1750_REVIEW.md`
- `HANDOFF_CLAUDE_GOAL1742_1750_UPDATED_REVIEW.md`

The older attempted Claude output path remains absent and should not be treated as evidence:

```text
docs/reviews/goal1752_claude_review_updated_goal1742_1750_v1_8_packet_2026-05-12.md
```

## Focused Gate

The focused v1.8 evidence gate was re-run after the Goal1753 status note:

```text
Ran 167 tests in 4.617s
OK (skipped=1)
```

## Do Not Stage

Do not stage local/protected files:

- `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`
- `id_ed25519_rtdl_codex`
- `rtdl_v0_4.tar.gz`
- `scratch/`

The `scratch/goal1746_ann_rerank.log` file is useful local corroboration, but it is not required for the tracked review chain because Goal1747 and Goal1749 record the relevant command and elapsed time.

## Remaining Blockers

- Explicit user authorization before any `VERSION` bump, tag, push, or release operation.

## Boundary

This is an inventory and staging guide only. It is not a release decision, not a tag command, and not package publication.
