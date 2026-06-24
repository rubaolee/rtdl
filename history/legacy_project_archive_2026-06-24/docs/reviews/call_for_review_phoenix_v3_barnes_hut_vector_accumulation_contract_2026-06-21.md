# Call For Review: Phoenix V3 Barnes-Hut Vector-Accumulation Contract

Date: 2026-06-21

Requested reviewer: Claude or another independent external AI reviewer.

Expected output:

```text
docs/reviews/claude_phoenix_v3_barnes_hut_vector_accumulation_contract_review_2026-06-21.md
```

## Review Target

Please review the Phoenix V3 Barnes-Hut/vector-accumulation contract packet:

```text
docs/rebuild/v3/phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md
docs/rebuild/v3/phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.json
scripts/v3_phoenix_barnes_hut_vector_accumulation_contract.py
tests/v3_phoenix_barnes_hut_vector_accumulation_contract_test.py
```

Relevant evidence and gates:

```text
docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md
docs/rebuild/v3/evidence/phoenix_v3_m6_barnes_hut_20260620/m6_barnes_hut_intake_summary.json
docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md
scripts/v3_release_wording_gate.py
scripts/v3_phoenix_release_readiness_gate.py
```

## Questions

1. Is the packet correct to keep Barnes-Hut as a generic V3 engine-gap driver rather than an M7 release row?
2. Does the packet correctly interpret the M6 evidence: fused Numba CUDA is fastest at every rerun scale, while prepared RTDL/OptiX+Numba is slower than the fastest route?
3. Is the proposed generic contract boundary right: `generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1`, app-agnostic, no hot-path aggregate-frontier row emission, no app-specific native Barnes-Hut callbacks?
4. Are the forbidden shortcuts strong enough to prevent misleading RT-core, whole-app, paper reproduction, or broad V3-over-V2 claims?
5. What concrete engineering action should come next if this remains a V3 priority?

## Required Verdict

Use one verdict:

```text
approve_queue_advancement_not_m7
approve_with_required_fixes_not_m7
needs_more_evidence_not_m7
reject_boundary
```

Do not approve any M7 promotion or release wording unless the evidence actually supports it.
