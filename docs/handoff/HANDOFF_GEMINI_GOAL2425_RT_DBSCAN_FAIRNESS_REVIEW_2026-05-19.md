# Gemini Handoff: Review Goal2424/Goal2425 RT-DBSCAN Prepared CuPy Fairness

Please perform an independent read-only review and write your result to:

```text
docs/reviews/goal2426_gemini_review_goal2424_2425_rt_dbscan_prepared_fairness_2026-05-19.md
```

## Context

The main AI added a prepared pure-CuPy fairness baseline for the RT-DBSCAN
benchmark and then collected RTX A5000 pod evidence.

Relevant files:

```text
docs/reports/goal2424_rt_dbscan_prepared_cupy_fairness_baseline_2026-05-19.md
docs/reports/goal2425_rt_dbscan_prepared_cupy_fairness_pod_evidence_2026-05-19.md
docs/reports/goal2425_rt_dbscan_prepared_cupy_fairness_pod_evidence/
examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py
examples/v2_0/research_benchmarks/rt_dbscan/README.md
scripts/goal2403_rt_dbscan_repeat_probe.py
tests/goal2424_rt_dbscan_prepared_cupy_fairness_baseline_test.py
tests/goal2425_rt_dbscan_prepared_cupy_fairness_pod_evidence_test.py
```

## Review Questions

1. Does Goal2424 correctly identify the fairness issue: prepared RT was being
   compared against a fresh-grid pure CuPy repeat baseline?
2. Does Goal2425 correctly interpret the pod evidence:
   - prepared RT wins clustered3d at 65k and above;
   - prepared RT wins road3d only at the 524k row measured here;
   - prepared pure CuPy wins ngsim_dense through 262k;
   - all artifact rows preserve signature parity?
3. Is the updated `planned_rt_dbscan` policy explicit, traceable, and not a
   hidden dispatcher?
4. Does the wording avoid broad DBSCAN, paper-reproduction, or release-level
   speedup claims?
5. Are there any source-integrity, test, or documentation gaps that should be
   fixed before this goal is treated as accepted?

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.
