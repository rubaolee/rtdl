## Independent Gemini Review of Goal3938 Current Benchmark Route Decision Registry

**Date:** 2026-06-08

**Reviewer:** Gemini CLI Agent

### Verdict: accept

### Review Questions and Answers:

1.  **Does the registry correctly encode the current route doctrine: primitive-first when a fused generic RTDL primitive wins, Numba when custom scalar/row-stream logic wins, CuPy only where honestly fastest with a Numba reference, and explicit user route choice throughout?**

    Yes, the registry correctly encodes the current route doctrine. The `CurrentBenchmarkRouteDecision` class's validation (`__post_init__`) strictly enforces explicit user choice and prohibits unauthorized claims. The `docs/reports/goal3938_current_benchmark_route_decision_registry_2026-06-08.md` report's "Design Rule" and the decisions for each application consistently reflect primitive-first when fused primitives win, Numba for custom scalar/row-stream logic, and CuPy only when fastest with a Numba reference, always emphasizing explicit user choice and non-promotion of slower candidates.

2.  **Does the `spatial_rayjoin` row correctly reflect Goal3936: Numba for bounded PIP one-shot, RTDL/OptiX for repeated PIP, LSI scalar count, and overlay active count, without auto-dispatch or RayJoin paper-reproduction claims?**

    Yes, the `spatial_rayjoin` row correctly reflects Goal3936 findings. The `current_reader_decision` in `src/rtdsl/current_benchmark_route_decisions.py` explicitly states: "Use Numba for bounded PIP one-shot; use RTDL/OptiX prepared primitives for repeated PIP, LSI scalar count, and overlay active count." It also explicitly rejects "universal PIP dominance" and "RayJoin paper reproduction" claims and emphasizes that "user explicit choice must remain required" for `partner_policy`. This aligns with the evidence presented in `docs/reports/goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08.md` and `docs/reports/goal3937_current_benchmark_adequacy_after_clean_cubin_rerun_2026-06-08.md`.

3.  **Does the `rt_dbscan` row correctly keep the blocked grouped-stream candidate unpromoted after Goal3936?**

    Yes, the `rt_dbscan` row correctly keeps the blocked grouped-stream candidate unpromoted. The `current_reader_decision` specifies "Use the unblocked RTDL/OptiX grouped stream plus Numba column-signature continuation," and `user_choice_guidance` states, "keep blocked mode off until it wins." The `rejected_or_unpromoted_candidates` also explicitly lists "blocked grouped stream candidate from Goal3936," which is consistent with the findings in `docs/reports/goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08.md` that the blocked mode is slower and should not be promoted.

4.  **Are claim boundaries intact: no release, public speedup, whole-app acceleration, broad RT-core, true-zero-copy, automatic partner selection, paper reproduction, AMD performance, or app-specific native-engine logic claims?**

    Yes, the claim boundaries are intact. The `CURRENT_BENCHMARK_ROUTE_DECISION_CLAIM_BOUNDARY` string in `src/rtdsl/current_benchmark_route_decisions.py` explicitly disavows such claims. This is rigorously enforced by the `__post_init__` method of the `CurrentBenchmarkRouteDecision` class, which mandates related boolean flags (e.g., `release_authorized`, `public_speedup_claim_authorized`, `true_zero_copy_claim_authorized`) to be `False`. Unit tests also confirm these restrictions. Consistent "Boundary" sections in `docs/reports/goal3938_current_benchmark_route_decision_registry_2026-06-08.md`, `docs/reports/goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08.md`, and `docs/reports/goal3937_current_benchmark_adequacy_after_clean_cubin_rerun_2026-06-08.md` further reinforce these boundaries.

5.  **Are there required fixes before Goal3938 can be treated as accepted internal route-governance evidence?**

    No, there are no required fixes. The design rule is clearly articulated, the route decisions for individual applications are consistent with the supporting evidence, and robust validation is in place to ensure claim boundaries are maintained. The existing unit tests also confirm the correct behavior and adherence to the specified policies.
