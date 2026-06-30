Verdict: accept

This is an independent Gemini review of Goal3606 RayJoin PIP Boundary Signal Negative Probe, distinct from Codex.

## Findings

1.  **Exactness Failure Confirmed:** Goal3606 accurately reports that the Goal3388 boundary-event selected-point signal fails to achieve exactness on the 4096-chain public-CDB county slice across all tested tolerances (0, 1e-6, 1e-5, 1e-4, 1e-3). The report (`docs/reports/goal3606_rayjoin_pip_boundary_signal_4096_negative_2026-06-06.md`) clearly states, "No tested tolerance matched it," with supporting data in the results table showing `Match: false` for all entries. The artifact (`docs/reports/goal3606_rayjoin_pip_boundary_signal_4096_negative_a5000/summary.json`) and associated test (`tests/goal3606_rayjoin_pip_boundary_signal_4096_negative_test.py`) further confirm this by asserting `all_tolerances_match_exact: false`.

2.  **Default-Route Promotion Blocked:** The evidence presented in Goal3606 correctly blocks the boundary-event signal family from default-route promotion. The report explicitly concludes that the signal is "not robust enough for default routing" and "blocks default-route promotion for the tested signal family." This is reinforced by the `claim_boundary.native_default_route_authorized: false` flag in the `summary.json` artifact, which is also verified by `tests/goal3606_rayjoin_pip_boundary_signal_4096_negative_test.py`.

3.  **Current Route Guidance Reaffirmed:** The current route guidance remains correct and is consistently reaffirmed by Goal3606. The "Interpretation" section explicitly reiterates the recommended paths: CuPy dense for public-CDB PIP scalar count, prepared OptiX exact for no-partner RTDL-only count, and the continued pursuit of a future fused generic closed-shape membership/count primitive for RTDL-side acceleration. This guidance aligns with the findings and conclusions of Goal3604 and its subsequent review (Goal3605).

4.  **Robust Claim Boundaries:** The claim boundaries established in Goal3606 are strong and consistently enforced. The report's "Status" and "Boundary" sections clearly state that the findings are "negative internal evidence only" and "does not authorize release, public speedup wording, RayJoin paper reproduction, RTDL-beats-RayJoin, RT-core speedup, true zero-copy, or native default-route claims." The `claim_boundary` object in `summary.json` has all its boolean fields set to `false`, a condition rigorously tested by `tests/goal3606_rayjoin_pip_boundary_signal_4096_negative_test.py`. These boundaries are consistent with the approach taken in related goals, ensuring that internal findings are not prematurely or inaccurately presented externally.

## Conclusion

Goal3606 successfully demonstrates the unsuitability of the Goal3388 boundary-event selected-point signal for default routing on larger public-CDB county slices due to its lack of exactness across tested tolerances. The evidence is clear, well-documented, and robustly tested. The goal correctly blocks default-route promotion for this signal family and reinforces the existing strategic route guidance, all while maintaining strong and appropriate claim boundaries. This provides valuable negative evidence that guides future development efforts towards more robust solutions.
