# Gemini Review For Goal3612/Goal3613 RayJoin Safe/Fast LSI Repair

## Verdict: accept-with-boundary

### Summary

The Goal3612 and Goal3613 reports and associated artifacts detail a successful repair of the RayJoin mixed-route LSI count mismatch identified in Goal3610. Goal3612 demonstrated a "safe mixed speedup" by employing an exact prepared RTDL/OptiX LSI count with host double refinement, ensuring count exactness. Goal3613 further refined this by tightening the specialized device-resident left-id dense count pipeline to use a strict segment predicate, achieving both exactness and significantly higher speedup for the LSI component without introducing app-specific engine logic. The evidence consistently supports the claims of correctness and performance, and the boundaries for public statements are clearly defined and consistently maintained. However, the ongoing need for a formalized, documented primitive contract for segment-pair intersection, especially concerning numerical tolerances and dataset diversity, suggests a "needs-more-evidence" aspect before unrestricted public claims can be made.

### Answers to Questions

1. **Does Goal3612 honestly repair the 4096 mixed-route composite by using exact prepared RTDL/OptiX LSI count, with all counts matching and a reported `193.939x` safe mixed speedup versus all-CuPy dense?**

   Yes, Goal3612 honestly repairs the 4096 mixed-route composite. The report `docs/reports/goal3612_rayjoin_safe_mixed_route_composite_2026-06-06.md` explicitly states the composite is "exact" and "strongly faster," reporting a `193.939x` speedup with "Counts Match: true." This is corroborated by the `summary.json` artifact, which shows `all_counts_match: true` and the specified speedup. The `scripts/goal3612_rayjoin_safe_mixed_route_composite.py` demonstrates the implementation uses `prepared_optix_exact_segment_pair_count` for LSI, and the corresponding test `tests/goal3612_rayjoin_safe_mixed_route_composite_test.py` validates these claims against the artifact.

2. **Does Goal3613 correctly tighten the specialized left-id dense count pipeline from conservative candidate counting to strict segment predicate counting without introducing RayJoin/CDB app-specific engine logic?**

   Yes, Goal3613 correctly tightens the specialized left-id dense count pipeline. The report `docs/reports/goal3613_lsi_left_id_dense_count_exact_predicate_2026-06-06.md` details the change to use a "strict segment predicate in the OptiX any-hit program" and confirms that "No RayJoin or CDB logic enters the engine." The `src/native/optix/rtdl_optix_workloads.cpp` source code verifies the change, showing the replacement of `seg_intersect_conservative_candidate` with `seg_intersect` and the introduction of `float hit_t = 0.0f;`. The tests `tests/goal3613_lsi_left_id_dense_count_exact_predicate_test.py` and `tests/goal3613_lsi_left_id_dense_count_exact_predicate_artifact_test.py` confirm both the code modification and the resulting correctness (zero diff count).

3. **Does the Goal3613 evidence support that the repaired dense count route now matches CuPy exactly at 4096 (`4977` vs `4977`, `diff_count=0`) and yields a valid mixed composite of `188.997x`, with LSI route speedup over `2000x`?**

   Yes, the Goal3613 evidence supports these claims. The `goal3613_lsi_left_id_dense_count_exact_predicate_2026-06-06.md` report's "Correctness Result" confirms exact matching LSI counts (`4977` vs `4977`, `0` differing left ids), and its "Performance Result" shows a `188.997x` mixed composite speedup with an LSI route speedup of `2032.908x`. These figures are precisely validated by the `mismatch_after_patch.json` and `fast_mixed_after_patch.json` artifacts, and further verified by `tests/goal3613_lsi_left_id_dense_count_exact_predicate_artifact_test.py`.

4. **Are the boundaries clear enough: internal evidence only, no release/public speedup/RayJoin-paper reproduction/RTDL-beats-RayJoin/broad RT-core/true-zero-copy/default-route authorization?**

   Yes, the boundaries are exceptionally clear and consistently enforced. All relevant reports and JSON artifacts explicitly state that the evidence is for internal use only and does not authorize any form of public release, speedup claims, RayJoin paper reproduction, RTDL-beats-RayJoin assertions, broad RT-core speedup, true zero-copy, or native default-route claims. The Python scripts reflect these claim boundaries, and the test suites confirm their presence and adherence.

5. **What risks remain before any public RayJoin claim or release packet? Pay special attention to float strict predicate versus host double exact refinement, dataset diversity, and whether the primitive contract needs a documented tolerance policy.**

   Significant risks remain before any public RayJoin claim or release packet. The `goal3610_rayjoin_lsi_4096_count_mismatch_probe_2026-06-06.md` and `goal3613_lsi_left_id_dense_count_exact_predicate_2026-06-06.md` reports both highlight the fundamental issue of a "missing shared near-degenerate segment policy."

   Specifically:

   - **Lack of Documented Primitive Contract:** There is an explicit need for the project to "document the segment-pair count contract as an explicit primitive policy," which must include clear definitions for denominator thresholds, endpoint handling, collinearity policy, and tolerance. Without this, the exactness achieved might be brittle and not generalize across different datasets or future changes.
   - **Float Strict Predicate vs. Host Double Exact Refinement:** Goal3612 used host double refinement, while Goal3613 opted for a float-side strict predicate for a device-resident solution, yielding higher speedup. The critical question remains whether this float-side strict predicate counting is universally sufficient for all accepted datasets. The `goal3613` report itself raises the question of whether an "exact device/host fallback on detected ambiguity" is necessary. This ambiguity needs to be resolved with a clear, documented policy.
   - **Limited Dataset Diversity:** The current evidence is based on a specific public CDB dataset (`br_county.cdb` and `br_soil.cdb`) at a 4096-chain count. While this dataset effectively revealed the initial mismatch, it may not encompass the full range of geometric complexities or near-degenerate conditions that could arise in a more diverse set of real-world or adversarial datasets.

   In summary, while the immediate correctness issue has been resolved for the tested scenario, the underlying generic contract for segment-pair intersection still lacks formalization and comprehensive testing across diverse conditions. This poses a risk for broader application or public claims.

## Provenance Note

Gemini produced this review to stdout in read-only plan mode after the auto-edit attempt failed to write the requested file. Codex saved the stdout review text to this file without changing the verdict or substantive findings.
