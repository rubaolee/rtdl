accept

Goal4190: RT-DBSCAN Counts-Only Mixed-Route Probe

Review Summary:

1.  **Probe Correctness:** The probe correctly compares the current grouped-stream Numba route with predicate direct-status routes (until-stable and single-pass) under both strict component-size and counts-only semantic contracts. The `policy_bound_component_sizes` and `core_noise_assigned_counts_only` signatures are appropriately calculated and compared.
2.  **Artifact Support:** The generated artifacts and the report clearly support the conclusion that counts-only signatures match while policy-bound component-size signatures do not for the direct-status routes. This semantic split is well-evidenced by the data.
3.  **Performance Justification:** The performance results justify the report's conservative conclusion. The single-pass direct-status shows only modest and scale-dependent speedups (up to 1.056x at 4M points), and the until-stable direct-status is consistently slower. This clearly indicates that it should not be a promoted default.
4.  **Next Runtime Target Identification:** The report correctly identifies the next major runtime target as a generic predicate-aware direct-status grouped-union primitive with deterministic border assignment, without encoding DBSCAN logic into the native engine. This aligns with the principle of keeping the native vocabulary generic.
5.  **Boundary Preservation:** All claim/release/route-promotion boundaries are strictly preserved throughout the script, report, and tests. Explicit flags and wording prevent unauthorized claims or premature promotion.

Overall, the Goal4190 probe provides sound evidence for the semantic contract distinction in mixed-predicate RT-DBSCAN routes and offers a cautious assessment of performance, maintaining clear boundaries for future development.
