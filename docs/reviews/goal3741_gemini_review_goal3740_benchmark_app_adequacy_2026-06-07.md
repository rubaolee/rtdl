# Goal3741 - Gemini Review of Goal3740 Benchmark-App Adequacy

Date: 2026-06-07

## Review Verdict: accept

Goal3740 effectively addresses the internal benchmark-app adequacy after the Goal3737 RayJoin executor packet. The approach provides a machine-checkable matrix for adequacy classification and clearly defines next steps.

## Answers to Questions

1.  **Does Goal3740 cover all 10 promoted benchmark apps without hiding weak rows?**
    Yes, Goal3740 explicitly covers all 10 promoted benchmark applications, as confirmed by the `v2_9_benchmark_adequacy.py` and its corresponding unit tests (`tests/goal3740_benchmark_app_adequacy_after_goal3737_test.py`). The `adequacy` classifications are transparent, with `barnes_hut` clearly marked as `needs_major_followup`. The document also states that the benchmark suite "is no longer dominated by weak rows, but it is also not done," indicating a proactive and unhidden approach to identified weaknesses. The `CLAIM_BOUNDARY` in both the Python code and the markdown report reinforces that this is for internal performance triage and not for release authorization or public speedup claims, which further supports transparency.

2.  **Is the adequacy classification fair after Goal3737, especially: RayJoin as strong but contract-specific, Barnes-Hut as the only `needs_major_followup`, RT-DBSCAN and robot collision as near-parity rather than headline wins?**
    Yes, the adequacy classification appears fair and well-reasoned:
    *   **RayJoin (spatial_rayjoin)** is classified as "strong but contract-specific." The report highlights significant speedups (e.g., 324.324x geomean) after Goal3737 while acknowledging remaining challenges in generic closed-shape/topology exactness. This balances the substantial improvement with the identified limitations.
    *   **Barnes-Hut** is correctly identified as the sole `needs_major_followup`, indicating a clear area for future work where the force-vector continuation is still partner-shaped and lacks a Numba reference.
    *   **RT-DBSCAN (rt_dbscan)** and **robot collision** are classified as "near parity," aligning with their performance readings of 0.997206x and 0.987619x respectively. The report explains that `robot_collision` is close enough to be treated as no-regression unless larger batches expose issues, and `rt_dbscan` is noted for its Numba-reference gap rather than an engine gap. This avoids presenting them as "headline wins" when they are closer to baseline performance.

3.  **Are the Numba-reference pressure points correct: `spatial_rayjoin`, `rt_dbscan`, and `barnes_hut`?**
    Yes, the identified Numba-reference pressure points (`spatial_rayjoin`, `rt_dbscan`, and `barnes_hut`) are correct. The `src/rtdsl/v2_9_benchmark_adequacy.py` module and its associated tests explicitly confirm these three applications require Numba references. The "Numba Reference Scope" section in the report provides clear, app-owned reasons for each, such as component labeling for `rt_dbscan`, grouped force-vector continuation for `barnes_hut`, and closed-shape/topology policy for `spatial_rayjoin`.

4.  **Does the AMD HIPRT preparation scope start from generic primitive mapping rather than app-shaped ports?**
    Yes, the AMD HIPRT preparation scope explicitly starts from generic primitive mapping. The "AMD HIPRT Preparation Scope" section of the report states, "The AMD lane should start only after a primitive map, not by porting benchmark apps directly." It then lists seven generic primitive targets (e.g., "segment-pair exact count," "shape-pair active-count executor") for initial HIPRT efforts, prioritizing functional parity before performance work.

5.  **Does the report avoid release, public speedup, broad RT-core, RayJoin paper-reproduction, true-zero-copy, automatic partner selection, or app-specific native-engine claims?**
    Yes, the report diligently avoids all such claims. Both the `V2_9_BENCHMARK_ADEQUACY_CLAIM_BOUNDARY` in `src/rtdsl/v2_9_benchmark_adequacy.py` and the "Claim Boundary" section in `docs/reports/goal3740_benchmark_app_adequacy_after_goal3737_2026-06-07.md` explicitly list these claims as unauthorized. The Python code further enforces this with validation logic in `V29BenchmarkAdequacyRow.__post_init__` and `validate_v2_9_benchmark_adequacy`, preventing these flags from being set to `True`.

6.  **What should be the next engineering step after Goal3740?**
    The next engineering steps after Goal3740 are clearly outlined in the report, categorized by application and area:
    *   **Numba Reference Work (P0/P1):**
        *   `rt_dbscan`: Build/measure a Numba component-continuation reference.
        *   `barnes_hut`: Write a Numba grouped vector-sum reference and compare against CuPy.
        *   `spatial_rayjoin`: Develop a Numba reference for closed-shape/topology policy (P1).
    *   **Generic Runtime/Primitive Work:**
        *   `spatial_rayjoin`: Make broad-CDB closed-shape/PIP exact without CuPy-only policy, or reduce generic overlay active-scan/containment work.
        *   `robot_collision`: Treat as no-regression unless larger pose batches expose material overhead.
    *   **AMD HIPRT Parity:**
        *   Map generic primitives (segment-pair exact count, shape-pair active-count, nearest-witness output columns, fixed-radius grouped/ranked summary, grouped i64 count/sum, prepared AABB query, bounded witness collection) to HIPRT.
    *   **General:** Future performance work should target material semantic gaps and larger-scale contract stress, rather than sub-1% noise.

## Conclusion

Goal3740 provides a clear and robust framework for assessing benchmark application adequacy. The classification is fair, transparent, and supported by explicit evidence. The identified Numba reference points and AMD HIPRT preparation scope are well-defined, guiding future engineering efforts effectively. The strict adherence to claim boundaries ensures responsible communication of results.
