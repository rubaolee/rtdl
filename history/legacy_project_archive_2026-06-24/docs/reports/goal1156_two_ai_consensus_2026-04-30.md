# Goal1156 Two-AI Consensus: DB Compact-Summary Batch Contract

Date: 2026-04-30

Verdict: `ACCEPT`

## Scope

Goal1156 added a stable prepared DB compact-summary batch contract and moved the two public DB app scenarios to use it when available.

## Evidence

- Codex implementation report: `docs/reports/goal1156_db_compact_summary_batch_contract_2026-04-30.md`
- Gemini review: `docs/reports/goal1156_gemini_db_compact_summary_batch_contract_review_2026-04-30.md`
- Focused test command passed: `PYTHONPATH=src:. python3 -m unittest tests.goal1156_db_compact_summary_batch_contract_test tests.goal954_database_native_continuation_contract_test tests.goal1128_embree_db_compact_summary_contract_test tests.goal851_optix_db_sales_grouped_summary_fastpath_test tests.goal850_optix_db_grouped_summary_fastpath_test tests.goal756_db_prepared_session_perf_test -v`
- Local Embree profile after the fix: `copies=1000`, `iterations=5`, `output_mode=compact_summary`, warm query median `0.0024431670317426324` seconds, row-materializing operations `0`, compact-summary operations represented `6`.

## Consensus

Codex and Gemini agree that the batch contract preserves correctness, avoids duplicate grouped summary calls in the app integration, and is honest about its boundary. This is a preparatory contract and Python/runtime dispatcher, not yet a native OptiX single-launch batch ABI and not a public speedup claim.

## Next Step

Implement the native OptiX prepared DB compact-summary batch ABI behind this contract, then mirror it in Embree for fair same-semantics baseline parity before the next RTX pod batch.

## Boundary

This consensus closes Goal1156 only. It does not authorize public RTX speedup wording, release v1.0, or start cloud resources.
