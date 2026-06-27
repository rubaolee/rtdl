# Handoff: Goal2388 RTNN Fair-Fight Benchmark Review

Please perform a read-only external review of Goal2388.

## Context

RTDL v2.2 is using the RTNN paper/repo as a benchmark pressure test for nearest-neighbor workloads. The goal is not a full RTNN paper reproduction. The goal is to verify that RTDL can express a serious RTNN-shaped workload with app-agnostic prepared 3-D fixed-radius neighbor primitives and measure it against:

- a same-family CuPy CUDA-core all-pairs ranked-summary baseline, and
- an optional build/run of the public RTNN implementation.

## Files To Inspect

- `scripts/goal2348_rtnn_v2_2_external_runner.py`
- `scripts/goal2388_rtnn_fair_fight_pod_runner.sh`
- `tests/goal2348_rtnn_v2_2_external_runner_test.py`
- `tests/goal2388_rtnn_fair_fight_benchmark_test.py`
- `docs/reports/goal2388_rtnn_fair_fight_benchmark_2026-05-19.md`
- `docs/reports/goal2388_rtnn_fair_fight_pod/*.json`

## Questions

1. Does the implementation keep the native RTDL engine app-agnostic, with no RTNN-specific ABI or shader path?
2. Does the report accurately describe the five completed next-useful-work items: paper-facing harness, prepared/batched large-scale path, device-ranked summary continuation, exact-vs-approx boundary, and fair baseline fight?
3. Are the performance claims properly bounded to RTDL-vs-CuPy same-family ranked-summary evidence, without overclaiming full RTNN paper reproduction or broad RT-core speedups?
4. Are the optional RTNN rows interpreted correctly as diagnostic, different-contract evidence?
5. Are the remaining design debts stated clearly enough: clustered-density/adaptive partitioning and stronger optimized CUDA-core baseline?

## Expected Output

Write a review to:

- Gemini: `docs/reviews/goal2389_gemini_review_goal2388_rtnn_fair_fight_2026-05-19.md`
- Claude, if available: `docs/reviews/goal2390_claude_review_goal2388_rtnn_fair_fight_2026-05-19.md`

Use verdict `accept`, `accept-with-boundary`, or `needs-more-evidence`. If accepting, keep the boundary explicit: no full RTNN reproduction claim and no broad RT-core speedup claim.
