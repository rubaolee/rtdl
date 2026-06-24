# Call For Review: Goal2896 RayDB Same-Contract Performance Decision Gate

Date: 2026-05-31

Please review Goal2896 as an independent external reviewer.

## Files To Inspect

- `docs/reports/goal2896_raydb_same_contract_performance_decision_gate_2026-05-31.md`
- `docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_raw_pod_69_30_85_171_2026-05-31.json`
- `docs/reports/goal2896_pod_artifacts/goal2896_raydb_same_contract_performance_decision_gate_pod_69_30_85_171_2026-05-31.json`
- `scripts/goal2896_raydb_same_contract_performance_decision_gate.py`
- `tests/goal2896_raydb_same_contract_performance_decision_gate_test.py`
- supporting context: `docs/reports/goal2727_raydb_prepared_grouped_reduction_opponent_2026-05-30.md`
- supporting context: `docs/reports/goal2728_raydb_v2_5_primitive_first_planner_2026-05-30.md`

## Review Questions

1. Does Goal2896 correctly transform the strategic "same-contract performance number" request into an executable, reproducible gate?
2. Are the comparisons correctly separated into:
   - required same-contract decision evidence: `paper_rt_optix_v2_5_primitive_first` versus `paper_rt_optix_device_hit_stream_triton_prepared`;
   - diagnostic full-call baseline evidence: `paper_rt_optix` versus primitive-first?
3. Are the thresholds reasonable and honest for an internal planning gate, given the pod results?
4. Does the report avoid overclaiming public speedup, true zero-copy, whole-app RayDB reproduction, auto-Triton promotion, or release readiness?
5. Does the design conclusion follow from the evidence: primitive-first for exact fused generic grouped reductions, typed hit-stream plus partner continuation reserved for continuations not expressible as fused RTDL primitives?
6. Are there missing fairness controls or failure modes that must be added before this result can feed a v2.5 release packet?

## Required Verdict Vocabulary

Use exactly one of:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If you choose `accept-with-boundary`, state the boundary precisely.

## Output

Please write the review to:

`docs/reviews/goal2897_external_review_goal2896_raydb_same_contract_perf_gate_2026-05-31.md`

This review should not authorize v2.5 release, public speedup claims, true-zero-copy claims, or paper-reproduction claims. It is a review of the Goal2896 internal planning gate only.
