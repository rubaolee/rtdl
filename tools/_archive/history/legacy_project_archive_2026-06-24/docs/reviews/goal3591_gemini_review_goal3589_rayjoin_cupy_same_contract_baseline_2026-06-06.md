# Goal3591: Gemini Review of Goal3589 RayJoin CuPy Same-Contract Baseline

Date: 2026-06-06

## Verdict

`accept-with-boundary`

Goal3589 establishes a crucial new internal benchmark by comparing RTDL/OptiX performance against warmed, dense CuPy CUDA-core baselines for the same three RayJoin-style contracts (PIP, LSI, overlay active-count). The evidence supports the conclusion that while RTDL/OptiX excels in stress LSI scenarios, it currently lags behind optimized CuPy for PIP and overlay active-count on simple authored tiled fixtures. The report's explicit boundaries regarding public speedup claims and the scope of these findings are appropriate and well-communicated. This work is valuable for internal guidance and future optimization efforts.

## Findings

1.  **CuPy Baselines Correctly Defined (non-RT, same-contract, user/partner CUDA-core):**
    The `scripts/goal3589_rayjoin_cupy_same_contract_baseline.py` script, its associated `tests/goal3589_rayjoin_cupy_same_contract_baseline_test.py`, and the `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md` report consistently define the CuPy baselines as non-RT, same-contract, user/partner CUDA-core implementations.
    -   The script explicitly sets `"rt_core_accelerated": False`, `"partner_accelerated": True`, and `"same_contract_baseline": True` for CuPy results.
    -   The kernels used (`PIP_COUNT_KERNEL`, `LSI_COUNT_KERNEL`, `OVERLAY_ACTIVE_COUNT_KERNEL`) are raw CUDA kernels, confirming direct CUDA-core usage.
    -   The test suite includes assertions to verify these classifications and the non-RayJoin paper reproduction claim.
    -   The report clearly states: "This is intentionally user/partner code outside the engine. The CuPy baseline does not use RT cores and does not call RTDL candidate generators."

2.  **A5000 Artifacts Support Conclusions:**
    The `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_a5000/summary.json` (standard) and `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_stress_a5000/summary.json` (stress) artifacts fully support the main conclusion presented in `docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md`.
    -   **Standard Packet (x512):**
        -   PIP: RTDL/OptiX speedup vs CuPy: `0.041x` (CuPy faster)
        -   LSI: RTDL/OptiX speedup vs CuPy: `0.765x` (CuPy faster)
        -   Overlay: RTDL/OptiX speedup vs CuPy: `0.187x` (CuPy faster)
    -   **Stress Packet (x2048):**
        -   PIP: RTDL/OptiX speedup vs CuPy: `0.052x` (CuPy faster)
        -   LSI: RTDL/OptiX speedup vs CuPy: `6.261x` (RTDL/OptiX faster)
        -   Overlay: RTDL/OptiX speedup vs CuPy: `0.095x` (CuPy faster)
    This data aligns perfectly with the report's interpretation: "A warmed CuPy CUDA-core user baseline beats the current RTDL/OptiX route for PIP and overlay active-count on the simple square tiled fixtures. RTDL/OptiX wins the stress LSI row, where RT traversal and dense left-id count produce a real advantage over the dense CUDA-core pair test."

3.  **Result Boundaries Are Honest and Clear:**
    The report (`docs/reports/goal3589_rayjoin_cupy_same_contract_baseline_2026-06-06.md`) and the relevant `claim_boundary` fields within the `summary.json` artifacts clearly and consistently define the scope and limitations of the results.
    -   Goal3589 explicitly blocks "public RayJoin RT-core speedup wording" and states that "It is not a RayJoin paper reproduction and does not authorize public speedup wording."
    -   The report reiterates that "Goal3586 remains valid only as an Embree-vs-OptiX packet."
    -   The `claim_boundary` structures within the JSON artifacts consistently set `public_speedup_claim_authorized: false`.
    These boundaries are robust and prevent misinterpretation of the results.

4.  **No Measurement-Contract Problems or Suspicious Timings:**
    The measurement protocol described in the report (one warmup, five hot repeats, exclusion of setup/compile/upload from hot medians, count identity verification) appears sound and fair for comparison.
    -   The script includes an explicit runtime check for count mismatches between RTDL/OptiX and CuPy.
    -   The interpretations in the report provide a reasonable explanation for the observed performance differences, attributing CuPy's wins to simple geometry allowing for cheap bounds rejection and RTDL/OptiX's overheads.
    -   No obvious unfair exclusions, count/parity gaps, or suspicious timings were identified that would undermine the validity of Goal3589 as internal benchmark guidance. The findings serve as actionable insights for future optimization.
