**Review of Goal4172-4173 Declared All-Predicate RT-DBSCAN Route**

**Verdict:** `accept-with-boundary`

This review covers Goal4172 ("Declared All-Predicate RT-DBSCAN Route") and Goal4173 ("Declared All-Predicate RT-DBSCAN 2M Probe"). The chain introduces an explicit caller-declared all-predicate route for RT-DBSCAN, intended for scenarios where the caller has external proof that all predicate flags are true, thereby allowing the system to bypass predicate-measurement overhead.

**1. Does Goal4172 correctly add an explicit caller-declared all-predicate route without adding native app-specific engine logic?**
Yes. Goal4172 successfully adds the `partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d` route. The `rtdl_rt_dbscan_benchmark_app.py` code explicitly defines this mode, bypasses the OptiX count-threshold phase, and sets metadata flags such as `app_specific_engine_logic_allowed: False` and `native_abi_added: False`. The tests in `goal4172_declared_all_predicate_rtdbscan_route_test.py` confirm its explicit nature and the absence of hidden engine logic or ABI additions.

**2. Does the route honestly require external proof and avoid hidden/automatic dispatch?**
Yes. The documentation, code, and tests consistently emphasize that this route is predicated on the user's *external proof* of an all-true predicate. The `explain_rt_dbscan_explicit_route_choice` function exposes it as an explicit option, setting `caller_declared_predicate_columns_require_external_proof: True`, `automatic_route_selection_authorized: False`, and `hidden_dispatch_allowed: False`. The tests verify that it is not automatically selected or promoted.

**3. Does Goal4173 support the bounded claim that the declared route removes predicate-measurement overhead on the 2M road3d all-predicate row?**
Yes. Goal4173 provides strong empirical evidence. The pod artifact `goal4173_declared_all_predicate_rtdbscan_2m_probe_pod.json` and its corresponding report show that the "declared all-true predicate direct-status" route achieves a 1.211x elapsed speedup over the "measured all-true predicate direct-status" route, specifically because it records 0.0 seconds for the `optix_rt_count_threshold_sec`, while the measured route incurs approximately 5 seconds for this phase. The RT-DBSCAN component signatures remain identical across both routes, confirming correctness.

**4. Are the timing numbers and signatures in the pod artifact interpreted correctly?**
Yes. The timing numbers, calculated speedups, and the consistent RT-DBSCAN signatures across different routes are accurately presented and interpreted in `goal4173_declared_all_predicate_rtdbscan_2m_probe_pod.json` and `goal4173_declared_all_predicate_rtdbscan_2m_probe_2026-06-09.md`. The detailed timing breakdown in the JSON artifact correctly attributes the performance gain to avoiding predicate-measurement overhead. The use of a small warmup run to prevent JIT compilation costs from being charged to the measured timing is also explicitly noted.

**5. Is the claim boundary correct, especially that the declared subpath has no RT count-threshold execution and no RT-core acceleration claim?**
Yes. The claim boundary is rigorously maintained and explicitly stated across all documents and code. Both Goal4172 and Goal4173 clearly declare that the declared subpath involves "No RT-count-threshold execution" and makes "No RT-core acceleration claim." The pod artifact's metadata confirms `rt_count_threshold_executed: false` and `rt_core_accelerated: false` for this route. The underlying application code and tests consistently verify these boundary conditions.

**6. What, if anything, must be fixed before this can remain in the v2.x performance evidence chain?**
No fixes are identified as necessary. The implementation is robust, the claims are well-bounded, the empirical evidence is substantial, and the verification process through testing is adequate. This work maintains all stated project conventions and safety guidelines.
