# Independent Gemini Review for Goal2388: RTNN Fair-Fight Benchmark

**Reviewer**: Gemini / Google
**Date**: 2026-05-19
**Independent From**: Claude

## Verdict: `accept-with-boundary`

## Review Findings

1. **Does the implementation keep the native RTDL engine app-agnostic, with no RTNN-specific ABI or shader path?**
   - **Yes.** The report explicitly states, "No RTNN-specific native symbol, shader, or ABI was added to RTDL," and further reiterates in the boundaries section that the result remains app-agnostic at the native RTDL ABI level. The test uses the generic `run-rtdl-batched-3d-neighbors` mechanism rather than injecting any RTNN-specific semantics.

2. **Does the report accurately describe the five completed next-useful-work items: paper-facing harness, prepared/batched large-scale path, device-ranked summary continuation, exact-vs-approx boundary, and fair baseline fight?**
   - **Yes.** The "Purpose" section of the report directly itemizes and fulfills these five tasks. It adds a paper-facing harness for synthetic distributions (uniform, clustered, shell), leverages the prepared/batched large-scale path, exercises the device-resident top-K continuation (Goals 2381/2384), explicitly documents exact vs. approximate modes, and introduces a fair CUDA-core baseline via CuPy.

3. **Are the performance claims properly bounded to RTDL-vs-CuPy same-family ranked-summary evidence, without overclaiming full RTNN paper reproduction or broad RT-core speedups?**
   - **Yes.** The report is extremely careful in framing the performance comparison. The "Claim Boundary" section authorizes claims solely regarding RTDL beating the provided all-pairs CuPy baseline under identical workload parameters. It expressly forbids "Full RTNN paper reproduction" and "Broad RT-core nearest-neighbor speedup claim", keeping the narrative honest.

4. **Are the optional RTNN rows interpreted correctly as diagnostic, different-contract evidence?**
   - **Yes.** The "Optional Official RTNN Rows" section clearly frames these runs as reference benchmarks. It states that the "contract is not the same as RTDL ranked-summary rows, so these rows are diagnostic rather than direct wins/losses," and adds "different witness/materialization pipeline" notes to every table row. This avoids misleading apples-to-oranges comparisons.

5. **Are the remaining design debts stated clearly enough: clustered-density/adaptive partitioning and stronger optimized CUDA-core baseline?**
   - **Yes.** In the "Design Conclusions" section, the report explicitly flags two critical remaining debts for the RTNN campaign: "Adaptive/density-aware partitioning for clustered data" (which caused the massive candidate spike in the dense clustered row) and "A stronger optimized CUDA-core baseline... if we want a more aggressive CUDA-only comparison than all-pairs CuPy."

## Conclusion

The Goal2388 benchmark serves as a transparent and meticulously bounded validation of the generic prepared ranked-summary pipeline against a fair baseline. The report demonstrates significant progress while explicitly rejecting premature or exaggerated claims. I assign the `accept-with-boundary` verdict.
