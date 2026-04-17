# Codex Consensus: Goal 500 v0.7 DB Expert Attack Audit Intake

Date: 2026-04-17

Verdict: ACCEPT

## Reviewed Artifacts

- `/Users/rl2025/rtdl_python_only/docs/reports/v0_7_db_expert_attack_suite_audit_comprehensive_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/v0_7_db_expert_attack_suite_audit_response_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal500_claude_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL500_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-17.md`

## Consensus

Codex and Claude agree that the newly supplied external v0.7 DB expert attack
suite report is useful evidence, but needed bounded interpretation before it
could be used in the release record.

Accepted points:

- The report should be preserved as an external audit artifact.
- The report correctly keeps attention on `conjunctive_scan`, `grouped_count`,
  and `grouped_sum`.
- The current local repo already contains the Goal 469 native CPU empty-table
  fast path.
- The remaining local error-surface gap was real: grouped field lookups could
  still leak `KeyError`.

Code response:

- `src/rtdsl/db_reference.py` now raises `ValueError` for missing grouped
  fields instead of leaking `KeyError`.
- `src/rtdsl/oracle_runtime.py` validates required DB fields before text-field
  encoding.
- `tests/test_v07_db_attack.py` no longer accepts `KeyError` for the covered
  missing-field cases and adds direct missing-group/value-field tests.

Honesty boundary:

- Do not repeat the external report's unqualified "Production Stable" phrasing.
- Do not claim this local response reran Linux PostgreSQL, OptiX, Vulkan, or
  large remote backend tests.
- The correct local claim is that the new audit was ingested, overclaims were
  corrected, and the remaining local error-contract gap was fixed and tested.
