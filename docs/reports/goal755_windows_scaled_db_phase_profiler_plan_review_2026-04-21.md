# Goal755 Windows Review: Scaled DB Phase Profiler Plan

## Verdict

ACCEPT_WITH_NOTES.

This is a fair next step for the OptiX app-performance roadmap. The current DB phase profiler already exposes scenario/backend/phase timing, so adding `--copies`, running scaled Linux backend comparisons, and using phase splits to choose the next DB optimization is better than guessing. The notes below should be handled so the resulting data is interpretable and does not overclaim.

2+ AI consensus is satisfied for this review: Windows Codex reviewed the bridge request and local profiler shape, and an independent second-agent review returned `ACCEPT_WITH_NOTES`.

## Findings

- The direction is sound: scale the DB workload, collect phase-level evidence, then choose whether to optimize dataset preparation, native query execution, row materialization, or Python postprocessing from measured bottlenecks.
- The plan should define fairness criteria before running comparisons: same generated input rows, same `--copies`, same iteration/warmup policy, same Linux machine/hardware class, and the same backend availability rules for skipped optional backends.
- The plan should distinguish app/scenario scaling from backend speedup. A `--copies` option should record input row counts per scenario and should make clear whether it tiles data, duplicates rows with fresh IDs, or changes predicate selectivity.
- The existing `scripts/goal693_db_phase_profiler.py` has useful phase buckets, but Goal755 should avoid collapsing too much into `query_*_and_materialize` if the optimization decision depends on whether native execution or Python row materialization dominates.

## Missing Tests Or Honesty-Boundary Issues

- Add a portable regression test that default profiler behavior remains unchanged when `--copies` is omitted.
- Add a test that `--copies` is accepted, increases the expected scenario row counts, and preserves correctness/output shape for a small CPU reference run.
- Add a test or report assertion that scaled Linux backend comparisons use identical generated inputs across compared backends.
- Keep the existing honesty boundary explicit: DB phase profiler results do not prove RTX RT-core speedup. GTX 1070 Linux runs are useful for backend availability, correctness, and whole-call/phase behavior, not RTX-class acceleration claims.
- If optional Linux backends are unavailable, the report should record `skipped_or_failed` or equivalent status instead of silently dropping them.

## Specific Next-Step Recommendation

Proceed with a small, controlled Goal755 implementation:

1. Add `--copies` to `scripts/goal693_db_phase_profiler.py` and make both DB scenarios consume the same scaled case generation deterministically.
2. Emit row-count/selectivity metadata and phase stats in the JSON payload.
3. Run a baseline small portable CPU test, then one scaled Linux comparison across CPU/Embree/OptiX/Vulkan as available.
4. In the closure report, choose the next DB optimization only from the largest measured phase bucket, with an explicit no-RTX-speedup boundary.

## Blockers

None.
