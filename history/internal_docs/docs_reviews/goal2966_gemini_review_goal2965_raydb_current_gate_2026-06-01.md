# Goal 2966: Gemini Review for Goal 2965 RayDB Current Gate

- **Verdict:** `accept-with-boundary`
- **Review Date:** 2026-06-01
- **Source Commit:** `8baed4f0` (Reports based on `28bcf380`)
- **Review Status:** Complete, Read-Only

## Summary

The Goal 2965 refresh of the RayDB same-contract performance decision gate is sound. The evidence collected at commit `28bcf380` confirms that the primitive-first routing logic for exact fused generic RTDL reductions remains significantly faster than the typed hit-stream plus Triton continuation path. The 2,000,000-row stress rows reinforce this direction without regressing. While the technical evidence is accepted, the review remains `accept-with-boundary` because release authorization, public claims, and multi-architecture fairness checks (compiler flag alignment and second-architecture validation) are explicitly blocked and remain as tracking items in the v2.5 readiness index.

## Findings

### 1. Gate Pass and CPU-Reference
The current-commit gate passes with no errors and all CPU-reference checks true.
- **Evidence:** `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json` records `"status": "pass"`, `"all_correct": true`, and `"errors": []`.
- **Commit:** The artifact correctly identifies `28bcf380b078f6e3c0cbe55d9ed4ed78a9ac61e9` as the source of the pod evidence.
- **Provenance:** Raw artifacts in `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_raw_current.json` confirm `"matches_cpu_reference": true` for all measured backends.

### 2. Formal Acceptance Rows (250K/1M)
The formal acceptance rows clear the Goal 2896 thresholds by substantial margins.
- **250K Count:** 30.138x slowdown for hit-stream (Required >= 10x).
- **250K Sum:** 134.389x slowdown for hit-stream (Required >= 50x).
- **1M Count:** 31.617x slowdown for hit-stream (Required >= 10x).
- **1M Sum:** 142.648x slowdown for hit-stream (Required >= 50x).
- **Finding:** The primitive-first path maintains its performance lead, justifying the continued use of fused generic primitives for these operations.

### 3. Stress Rows (2M)
The 2,000,000-row stress rows support the same performance direction.
- **2M Count:** 34.962x slowdown for hit-stream; 10148.444x speedup vs. old full-call baseline.
- **2M Sum:** 108.213x slowdown for hit-stream; 2435.365x speedup vs. old full-call baseline.
- **Finding:** The 2M rows provide empirical evidence of stability at scale. They are correctly excluded from the formal threshold gate to avoid overpromotion, serving instead as directional validation.

### 4. Planner Conclusion Soundness
The interpretation of the results into the v2.5 planner rule is sound:
- **Rule:** Prioritize fused generic RTDL primitives when they exactly match the continuation; reserve hit-stream plus partner continuation for non-expressible cases.
- **Finding:** This preserves the performance "fast path" while maintaining the flexibility of the partner-integrated ecosystem (Triton).

### 5. Claim Boundaries and Overclaiming
The report rigorously avoids overclaiming.
- **Evidence:** The "Boundary" section in the report and the `claim_boundary` flags in the gate JSON explicitly disallow release authorization, public speedup wording, and broad RT-core claims.
- **Finding:** All release and claim boundaries established in previous goals are preserved.

### 6. Remaining Cautions
Fairness and release-gate cautions remain active.
- **Evidence:** `src/rtdsl/v2_5_internal_readiness.py` continues to track `track_goal2897_compiler_flag_alignment_before_release_packet` and `track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet`.
- **Finding:** Multi-architecture fairness and toolchain alignment are not yet closed and must be resolved before a full release packet can be authorized.

## File-Level Findings

- **`docs/reports/goal2965_raydb_current_commit_gate_refresh_2026-06-01.md`**: Accurate summary of pod evidence and gate results. Correctly identifies boundaries.
- **`docs/reports/goal2965_raydb_current_gate_pod/*.json`**: Coherent artifacts that provide the necessary technical provenance.
- **`tests/goal2965_raydb_current_commit_gate_refresh_test.py`**: Verifies that the report and artifacts are present and internally consistent. Successfully passes in the local environment.
- **`scripts/goal2896_raydb_same_contract_performance_decision_gate.py`**: Implementation of the decision rule is correct and aligns with the reported thresholds.
- **`src/rtdsl/v2_5_internal_readiness.py`**: Correctly incorporates Goal 2965 into the v2.5 readiness index while maintaining tracking for pending release-gate items.
