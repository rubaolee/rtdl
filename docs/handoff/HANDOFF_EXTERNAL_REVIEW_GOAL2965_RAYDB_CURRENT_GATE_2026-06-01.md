# Handoff: External Review For Goal2965 RayDB Current-Commit Gate Refresh

Please perform an independent read-only review of Goal2965. Write your review
to the output path named in the prompt you received. Do not edit source files,
tests, reports, or artifacts other than that single review file.

## Scope

Goal2965 refreshes the Goal2896 RayDB same-contract performance decision gate on
current main and adds 2,000,000-row stress rows. The decision rule is unchanged:
use primitive-first fused generic RTDL reductions when they exactly express the
continuation; reserve typed hit-stream plus partner continuation for operations
not expressible by the fused primitive set.

Primary files:

- `docs/reports/goal2965_raydb_current_commit_gate_refresh_2026-06-01.md`
- `tests/goal2965_raydb_current_commit_gate_refresh_test.py`
- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`
- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_raw_current.json`
- `scripts/goal2896_raydb_same_contract_performance_decision_gate.py`
- `src/rtdsl/v2_5_internal_readiness.py`

## Questions To Answer

1. Does the current-commit gate pass at source commit `28bcf380` with no errors
   and all CPU-reference checks true?
2. Do the formal 250K/1M acceptance rows still clear the Goal2896 thresholds
   for both `count` and `sum`?
3. Do the 2M stress rows support the same direction without being overpromoted
   into the formal acceptance threshold set?
4. Is the planner conclusion still sound: primitive-first for exact fused
   generic grouped reductions, typed hit-stream plus partner continuation only
   when the fused primitive set cannot express the requested continuation?
5. Does the report avoid overclaiming and preserve all blocked release/public
   claim categories?
6. Are there remaining fairness or release-gate cautions, especially compiler
   flag alignment or second-architecture checks?

## Expected Verdict Format

Use one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

For this review, `accept-with-boundary` is expected if the refreshed evidence is
sound but release/public claims and multi-architecture fairness remain blocked.

Please include file-level findings where possible and distinguish source-backed
facts from your own recommendations.
