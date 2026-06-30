# Goal3134: Gemini Review For Goal3132 v2.8 Partner Front Door Pod Smoke

**Verdict:** accept-with-boundary

**Findings By Severity:**

*   **Medium:** Performance Debt identified in larger Numba timing probe for `grouped_argmin_f64` and `grouped_argmax_f64`, which are significantly slower than the Python reference. The report correctly classifies this as negative performance evidence/performance debt.

**Claim Boundary:**

*   No release
*   No public speedup
*   No broad RT-core
*   No true-zero-copy
*   No hidden dispatch
*   No automatic partner selection
*   No app-specific native engine
*   No user-defined shader injection
*   No benchmark-app performance claims

**Evidence Considered:**

*   Goal3132 validates v2.8 explicit partner-consumer front door on RTX 4000 Ada pod, driver 580.65.06, compute capability 8.9, Python 3.12.3, repo commit 2809a45b.
*   Partner stack includes Numba 0.65.1, CuPy 14.1.1, and Torch 2.12.0+cu130.
*   Focused unit gate passed with 27 tests OK.
*   Numba sanity kernel passed.
*   Small functional cases matched Goal3114 Python reference and kept claim flags false for: `segmented_count_i64/CuPy`, `segmented_sum_f64/CuPy`, `grouped_vector_sum_f64x2/CuPy`, `grouped_argmin_f64/Numba`, `grouped_argmax_f64/Numba`, `grouped_topk_f64/Torch`, and `bounded_collect_finalize_i64/Torch`.
*   Larger Numba timing probe with `row_count=65536 group_count=1024` showed `grouped_argmin_f64` warm 0.213s, steady [0.312, 0.216, 0.217] vs Python reference 0.056s. `grouped_argmax_f64` warm 0.208s, steady [0.210, 0.212, 0.212] vs Python reference 0.056s.
*   The report explicitly classifies this timing as negative performance evidence/performance debt, not a speedup claim.

**Review Question Answers:**

1.  **Does Goal3132 fairly state that pod functional smoke passed for current v2.8 front-door surface?** Yes, the "Focused unit gate passed: 27 tests OK" and small functional cases matching reference confirm this.
2.  **Does it correctly preserve the claim boundary?** Yes, the report clearly lists the negative claim boundaries, indicating no premature or overreaching claims are made.
3.  **Is larger Numba grouped-arg timing correctly classified as negative performance evidence/performance debt?** Yes, the report explicitly states this classification.
4.  **Are next engineering targets right?** Yes, the proposed next steps are appropriate for investigating and addressing the identified performance debt in the Numba grouped-arg path.

**Next Steps:**

*   Inspect Numba grouped-arg path for under-occupied launches and host-side compacting/front-door overhead.
*   Split kernel/compaction/front-door timing measurements.
*   Test larger regimes to further understand performance characteristics.
*   Decide if grouped arg should evolve into a stronger generic native primitive or remain as a partner continuation.
