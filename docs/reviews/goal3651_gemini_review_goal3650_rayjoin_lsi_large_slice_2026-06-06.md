# Gemini Review for Goal3650 RayJoin LSI Large-Slice Prepared-Left Scaling

**Verdict: accept-with-boundary**

**Date:** 2026-06-06

**Reviewer:** Gemini

## Findings

Goal3650 successfully validates the RayJoin LSI helper's utilization of the generic prepared-left segment-set route on a larger 4096-row public CDB slice. This builds upon the previous Goal3647, which established the contract on a 512-row slice. The artifact and report demonstrate that the RTDL prepared-left query mechanism accurately matches RayJoin's visible LSI counts while exhibiting a favorable timing comparison. The report diligently maintains clear claim boundaries, preventing any overstatement of the implications of this work regarding broader performance claims, release readiness, or full RayJoin reproduction. The progression from a smaller to a larger slice provides stronger evidence for the robustness of the prepared-left route.

## Answers to Review Questions

### 1. Does the 4096-row artifact genuinely show matching visible LSI counts (`4977` RayJoin, `4977` RTDL)?
Yes, the primary artifact `docs/reports/goal3650_rayjoin_lsi_prepared_left_large_slice_a5000/same_slice_4096_summary.json` and the `Result` table within the main report clearly show matching visible LSI counts of `4977` for both RayJoin and RTDL for the 4096-row slice.

### 2. Is the timing comparison scoped correctly to RayJoin's reported query median versus RTDL's prepared query median, not full app-wall timing?
Yes, the timing comparison is correctly scoped. The report explicitly presents "RayJoin Query Median ms" against "RTDL Prepared Query Median ms." The methodology outlined in the report and corroborated by previous reviews (Goal3648) confirms that hot-route/repeated-call evidence is prioritized over one-shot, full app-wall timing, focusing precisely on the query execution within the respective systems.

### 3. Does the report avoid claiming full RayJoin reproduction, broad RT-core speedup, release readiness, true zero-copy, or whole-app benchmark speedup?
Yes, the report diligently avoids these claims. The "Boundary" section explicitly lists all these items as not authorized by this goal. Furthermore, the underlying artifact (`same_slice_4096_summary.json`) confirms that all `claim_boundary` flags are set to `false`, reinforcing the narrow and precise scope of the accepted claims.

### 4. Is it reasonable to treat the 4096-row result as stronger evidence than the 512-row smoke for the narrow LSI visible-count contract?
Yes, it is reasonable. The "Interpretation" section of the Goal3650 report explicitly states that "The 4096-row result is the stronger current evidence for this narrow LSI count contract" and notes that "The 512-to-4096 progression is useful because the old one-row comparison could have been dismissed as launch-noise sensitive." The larger dataset provides more robust validation for the count contract.

### 5. What should be the next engineering step after this packet: larger/synthetic LSI slices, prepared-left route integration into broader benchmark tables, or a new generic primitive?
The most impactful next engineering step should be **prepared-left route integration into broader benchmark tables**. While larger/synthetic LSI slices could further stress the current implementation, integrating the proven prepared-left route into more existing benchmark packets will broaden its applicability and validate its performance across a wider array of scenarios. This approach builds effectively on the current success and aligns with the strategy of leveraging generic primitives within higher-level applications.

## Boundary

This goal does not authorize:

- release readiness;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app benchmark claims;
- true zero-copy claims;
- full RayJoin paper reproduction claims;
- extending the LSI count-contract result to PIP, overlay, or full RayJoin assignment semantics.

The accepted claim is only that, for the public 4096-row county/soil LSI visible count contract, the RTDL prepared-left generic segment-pair route matches RayJoin's visible count and has a lower prepared-query median on the A5000 pod.
