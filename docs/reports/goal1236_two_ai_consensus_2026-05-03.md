# Goal1236 Two-AI Consensus

Date: 2026-05-03

Scope: public documentation simplification and audit synchronization after the
current Goal1224 public wording state.

## Consensus Verdict

ACCEPT

## Consensus

Codex and Gemini agree that the public documentation and audit-sync changes are
acceptable for the v1.0 release-readiness cleanup.

The accepted boundary is:

- Goal1177 and Goal1184 remain external-review input only.
- Neither Goal1177 nor Goal1184 authorizes a new public RTX speedup wording row.
- The current reviewed public RTX sub-path wording row count is `12` because of
  later reviewed bounded promotions through Goal1224.
- The updated audit scripts/tests preserve forbidden-public-promotion
  guardrails while replacing stale `11`-row assumptions with the current `12`
  reviewed-row state.

## Evidence

- Gemini review: `docs/reports/goal1236_gemini_public_doc_audit_sync_review_2026-05-03.md`
- Local verification:
  `PYTHONPATH=src:. python3 -m unittest tests.goal1178_goal1177_public_status_sync_audit_test tests.goal1179_public_docs_goal1177_boundary_audit_test tests.goal1180_current_release_readiness_window_audit_test tests.goal1185_goal1184_public_status_sync_audit_test tests.goal1186_current_release_readiness_after_goal1185_audit_test tests.goal506_public_entry_v08_alignment_test tests.goal531_v0_8_release_candidate_public_links_test tests.goal512_public_doc_smoke_audit_test tests.goal700_fixed_radius_summary_public_doc_test tests.goal646_public_front_page_doc_consistency_test tests.goal821_public_docs_require_rt_core_test tests.goal1231_front_page_simplification_test tests.goal1232_public_doc_map_test -v`
- Result: 41 tests passed.

## Required Fixes

None.
