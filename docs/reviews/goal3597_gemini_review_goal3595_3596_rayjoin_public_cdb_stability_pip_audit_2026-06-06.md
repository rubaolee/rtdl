Verdict: accept-with-boundary

This is an independent Gemini review, distinct from Codex.

Goal3595 and Goal3596 provide clear, consistent, and well-bounded evidence regarding RayJoin-style workloads, addressing prior concerns and offering strong internal guidance for route selection. The artifacts and reports are accurately generated and interpreted, and critical claim boundaries are robustly maintained across all documentation.

### Findings

1.  **Git-Cleanliness Concern Addressed (Severity: Low)**
    Goal3595 successfully addresses the prior git-cleanliness concern. The `docs/reports/goal3595_rayjoin_public_cdb_long_repeat_stability_2026-06-06.md` explicitly states that "The artifact was regenerated from a fresh clean pod checkout; its recorded `git_status_short` is empty." This is confirmed by the `git_status_short` field in `docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json` being an empty string, and validated by `tests/goal3595_rayjoin_public_cdb_long_repeat_stability_test.py`.

2.  **Accurate Reporting of Long-Repeat Numbers (Severity: Low)**
    The Goal3595 long-repeat numbers are accurately reported from the artifact. The `docs/reports/goal3595_rayjoin_public_cdb_long_repeat_stability_2026-06-06.md` table presents totals, medians, and count parity, which align precisely with the detailed data found in `docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json`. The report also correctly notes that "All counts matched." These aspects are further validated by assertions in `tests/goal3595_rayjoin_public_cdb_long_repeat_stability_test.py`, which also confirms the expected performance ratios.

3.  **PIP Route Conclusion Supported by Probes (Severity: Low)**
    Goal3596's PIP route conclusion is strongly supported by its measured existing-route probes. The "Results" table in `docs/reports/goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md` clearly shows CuPy as the "fastest" for scalar PIP count, with RTDL/OptiX exact prepared count as the "best RTDL-only route" but slower. Other device-filtered modes are correctly "rejected" due to not maintaining positive-membership semantics. The "Interpretation" and "Engineering Conclusion" sections logically derive from these measurements, which are implicitly verified by `tests/goal3596_rayjoin_public_cdb_pip_route_audit_test.py` asserting the presence of these findings in the report.

4.  **Clear README Guidance for PIP Workflows (Severity: Low)**
    The `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md` now provides clear guidance for the three specified cases: public-CDB mixed routes, no-partner RTDL-only PIP scalar count, and richer candidate-plus-refiner PIP workflows. It explicitly recommends CuPy for simple bounded PIP count in public CDB, the exact prepared OptiX count for no-partner RTDL-only scalar counts, and reserves `prepared_optix_cupy_refined_pip` for richer workflows. This clarity is implicitly verified by `tests/goal3596_rayjoin_public_cdb_pip_route_audit_test.py`.

5.  **Robust Avoidance of Overclaiming Authority (Severity: Low)**
    Both Goal3595 and Goal3596 consistently and explicitly avoid overclaiming authority. Their respective reports (`docs/reports/goal3595_rayjoin_public_cdb_long_repeat_stability_2026-06-06.md` and `docs/reports/goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md`), the `claim_boundary` object in `docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json`, and associated test files (`tests/goal3595_rayjoin_public_cdb_long_repeat_stability_test.py` and `tests/goal3596_rayjoin_public_cdb_pip_route_audit_test.py`) all explicitly disclaim authority over release, RayJoin reproduction, broad RT-core speedup, whole-app speedup, zero-copy, and automatic dispatch claims.

### Recommended Next Engineering Step

The concrete next engineering step to prioritize before a v2.9 RayJoin performance packet is outlined in `docs/reports/goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md` under "Engineering Conclusion":
Development of "a generic exact point-in-closed-shape count primitive that avoids the current candidate materialization plus exact-refine overhead while preserving boundary semantics." This should be a generic primitive, not a RayJoin-specific native path.

File references:
- `docs/reports/goal3595_rayjoin_public_cdb_long_repeat_stability_2026-06-06.md`
- `docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json`
- `tests/goal3595_rayjoin_public_cdb_long_repeat_stability_test.py`
- `docs/reports/goal3596_rayjoin_public_cdb_pip_route_audit_2026-06-06.md`
- `tests/goal3596_rayjoin_public_cdb_pip_route_audit_test.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/README.md`
- `docs/reviews/goal3594_gemini_review_goal3593_rayjoin_public_cdb_cupy_same_contract_2026-06-06.md`
