# Gemini Review: Goal2997 Numba Compact Mask

**Date:** 2026-06-01

**Review Scope:** Current `main` after commit `afca574838d2519def88c9bed45d999a4e0b153b` (as evidenced by the L4 pod artifact). Static/artifact review only, as shell execution was unavailable.

**Verdict:** `accept-with-boundary`

**Findings:**

All review questions indicate that Goal2997 has been implemented and documented according to the stated goals and constraints. The `compact_mask_i64` primitive is generic, correctly integrated with the v2.6 neutral partner handoff, preserves stable input order using a host prefix sum, and its L4 pod evidence rigorously documents runtime conformance without making unauthorized claims.

**Residual Boundaries:**

-   No v2.6 release authorization.
-   No public speedup claims (including Numba specific speedup claims).
-   No whole-app speedup claims.
-   No broad RT-core speedup claims.
-   No true zero-copy claims.
-   No automatic partner selection claims.
-   The current implementation prioritizes correctness and stable input order through a host-side prefix sum. A future performance pass may implement a device-resident scan, but this is not claimed or authorized by this goal.

---

### Questions To Answer:

**1. Is `compact_mask_i64` implemented as a generic Numba continuation primitive, without RayJoin/triangle-counting/app-specific engine logic?**

**Answer:** Yes, `compact_mask_i64` is implemented as a generic Numba continuation primitive.
-   The `describe_numba_compact_mask_i64` function in `src/rtdsl/numba_partner_continuation.py` provides a generic descriptor for the operation.
-   The `_base_numba_descriptor` explicitly states a claim boundary: "Numba executes only generic grouped continuation over device arrays; RTDL/OptiX traversal remains separate."
-   The `tests/goal2997_numba_compact_mask_prepared_test.py` explicitly asserts the absence of "rayjoin" and "triangle_count" in the Numba implementation source.
-   Documentation (`docs/reports/goal2997_numba_compact_mask_prepared_2026-06-01.md` and `docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md`) consistently describes it as a generic and app-agnostic primitive.

**2. Does `partner_mask_indices(mask, partner="numba")` require the v2.6 neutral partner handoff and avoid torch carrier/conversion?**

**Answer:** Yes, `partner_mask_indices(mask, partner="numba")` requires the v2.6 neutral partner handoff.
-   `src/rtdsl/partner_adapters.py` clearly shows the Numba branch of `partner_mask_indices` importing and calling `prepare_v2_6_neutral_partner_handoff` and `validate_v2_6_neutral_partner_handoff`.
-   The test `test_partner_mask_indices_accepts_numba_branch_and_rejects_host_mask` in `tests/goal2997_numba_compact_mask_prepared_test.py` confirms this by asserting the presence of `prepare_v2_6_neutral_partner_handoff` in the source and demonstrating that host NumPy masks are rejected, implying that only device-resident arrays are handled via the dedicated Numba path, thus avoiding `torch` carrier/conversion.

**3. Does the implementation preserve stable input order, and is the host-prefix-sum boundary honestly documented?**

**Answer:** Yes, the implementation preserves stable input order, and the host-prefix-sum boundary is honestly documented.
-   In `src/rtdsl/numba_partner_continuation.py`, `describe_numba_compact_mask_i64` sets `"stable_input_order": True` and `"host_prefix_sum_used": True`. The `run_numba_compact_mask_i64` function employs a two-pass strategy involving per-block counts and a host-side prefix sum calculation before scattering, ensuring order preservation.
-   The documentation (`docs/reports/goal2997_numba_compact_mask_prepared_2026-06-01.md` and `docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md`) explicitly states that a host prefix sum is used for correctness and stable input order, noting that it is "not yet a performance claim" and could be optimized with a device-resident scan in the future.
-   The `scripts/goal2997_numba_compact_mask_pod_runner.py` verifies this by checking `stable_input_order` and `host_prefix_sum_used` flags and performing CPU parity checks on ordered results.

**4. Is the L4 pod evidence valid runtime conformance evidence? Check rows, selected count, source commit, toolchain metadata, CPU parity flags, and claim-boundary fields.**

**Answer:** Yes, the L4 pod evidence (`docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md` and `docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.json`) is valid runtime conformance evidence.
-   **Rows and selected count:** Consistent (1,000,000 rows, 193,279 selected count).
-   **Source commit:** `afca574838d2519def88c9bed45d999a4e0b153b` is correctly recorded.
-   **Toolchain metadata:** Comprehensive details are provided, including Numba version (0.65.1), NumPy version (2.1.2), specific Numba CUDA module path, and environment variables, confirming the execution environment.
-   **CPU parity flags:** "values match CPU: true," "original indices match CPU: true," and "`partner_mask_indices`... indices match CPU: true" are all verified, demonstrating functional correctness.
-   **Claim-boundary fields:** The `claim_boundary` in the JSON artifact lists all unauthorized claims as `false`, and the markdown report clearly delineates what the evidence *does not* authorize (e.g., release, speedup claims, zero-copy claims).

**5. Are the roadmap/readiness updates honest, especially that Goal2997 is not release evidence or speedup evidence?**

**Answer:** Yes, the roadmap and readiness updates are honest and consistent in their claims.
-   `src/rtdsl/v2_6_roadmap.py` explicitly states `"compact_mask_status": "compact_mask_i64_l4_pod_conformance_passed_stable_order_host_prefix_sum_not_speedup_evidence"`, and consistently sets all release and speedup authorization flags to `False`. The `V2_6_ROADMAP_CLAIM_BOUNDARY` reinforces these restrictions.
-   `src/rtdsl/v2_5_internal_readiness.py` lists "request\_external\_review\_for\_goal2997\_numba\_compact\_mask" under `ALLOWED_NEXT_ACTIONS` and explicitly includes release and speedup wording in `BLOCKED_ACTIONS` and `CLAIM_BOUNDARY`.
-   The Goal2997 L4 pod report (`docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md`) reiterates that this is runtime conformance evidence and does not authorize release or speedup claims.

---
