Warning: Basic terminal detected (TERM=dumb). Visual rendering will be limited. For the best experience, use a terminal emulator with truecolor support.
Warning: 256-color support not detected. Using a terminal with at least 256-color support is recommended for a better visual experience.
Ripgrep is not available. Falling back to GrepTool.
The RTDL Barnes-Hut benchmark claim packet (Goal 2548) has been reviewed against the evidence provided in Goals 2543–2547.

### Verdict: **ACCEPT**
The "Strongest Currently Defensible Claim" is acceptable for internal engineering and bounded public-facing technical communications, provided the "Not Authorized" exclusions are strictly observed. The claim is technically precise, acknowledges the lack of contract parity, and avoids the common pitfall of conflating kernel speedups with whole-app performance.

---

### Defensible Claims
*   **Phase-Specific Performance:** A direct comparison of the **computational kernel phase** (0.509 ms for RTDL Goal2547 vs. 6.616 ms for authors' OWL/OptiX force phase) is valid when performed on the same hardware (RTX A5000) and the same input data.
*   **Dimensional & Model Parity:** The claim correctly identifies that dimensionality (3-D), input files, and the mathematical model (scalar inverse-square force) are now matched, making this a more relevant "apples-to-apples" comparison than previous 2-D vector tests.
*   **Numeric Validation:** The Goal 2547 diagnostic path is verified against RTDL's Python reference with acceptable float32 error bounds (mean relative error $\approx 1.7 \times 10^{-7}$), supporting the claim of "computing the same force shape."
*   **Diagnostic Status:** Explicitly labeling the RTDL implementation as a "diagnostic path" and "partner prototype" correctly signals that this is not a production-ready feature.

### Claims That Must Remain Blocked
*   **"13x Faster" Headlines:** Any headline claiming a generic "13x speedup" over the state-of-the-art is prohibited. Such a claim would be misleading without the "diagnostic kernel-phase" and "different tree contract" caveats.
*   **Paper Reproduction:** RTDL does **not** reproduce the RT-BarnesHut paper results (which involve specific tree structures and traversal logic not yet implemented in RTDL).
*   **Whole-App Speedup:** Including setup/preprocessing, the authors' code is significantly more efficient (~25ms total vs. ~330ms for RTDL). Any claim that omits the "phase-only" distinction is technically invalid.
*   **Native OptiX Status:** RTDL must not claim to use native OptiX RT-cores for this Barnes-Hut traversal yet; the Goal 2547 evidence is a CUDA-based diagnostic path.

### Required Wording Changes
While the current claim is acceptable, the following refinements are recommended for clarity:
1.  **Contract Clarity:** The phrase "narrower RTDL generic-tree contract" should be clarified for public audiences to something like: *"using RTDL's generic subtree-containment tree rather than the authors' specialized RT-tree."*
2.  **Explicit Kernel Labeling:** In any visual or summary representation, the `0.509 ms` figure should always be accompanied by the label **"Resident Kernel Phase (Force Only)"** to prevent accidental confusion with total execution time.
3.  **Force Model Terminology:** While "force shape" is used in the JSON metadata, "force calculation model" or "scalar inverse-square model" is preferred for the final claim to avoid ambiguity with "geometric shape."

### Strategic Note
The current `0.509 ms` result is a "hero number" achieved via float32 and O(1) source-containment optimizations. As noted in the rollup report (Goal 2545-2547), the next milestone must be a **same-contract** comparison to determine how much of the speedup is due to the RTDL engine versus the simplified tree structure used in the diagnostic path.
