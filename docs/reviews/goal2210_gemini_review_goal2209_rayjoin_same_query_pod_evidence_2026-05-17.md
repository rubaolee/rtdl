# Goal2210 Gemini Review of Goal2209 RayJoin Same-Query Pod Evidence

## Verdict

**`accept-with-boundary`**

## Summary of Findings

The Goal2209 artifact package provides a comprehensive and traceable set of evidence regarding the same-query pod run. The documentation, JSON summary, and dedicated unit test file collectively ensure that the results and interpretations are well-supported and transparent.

### Traceability of Artifact Package

The artifact package is traceable and well-documented. The `goal2209_rayjoin_same_query_pod_evidence_2026-05-17.json` file meticulously lists all imported files, their SHA-256 hashes, and their original source paths, providing a clear chain of provenance. While the full RayJoin query streams were not committed to the repository, their SHA-256 hashes and sizes are recorded, and the `test_import_keeps_raw_streams_out_of_repo_but_hashes_them` unit test explicitly validates this practice, which is acceptable for managing large data artifacts. The presence of `environment.txt` further aids in understanding the execution context.

### Same-Query and Same-Row Parity Claims

The claims for same-query and same-row parity for both LSI and PIP workloads are well-supported by the evidence. The interpretation document (`goal2209_rayjoin_same_query_pod_evidence_interpretation_2026-05-17.md`) explicitly states that RTDL consumed the exact same query stream as RayJoin through a dedicated adapter. The results tables consistently show "pass" for CPU, Embree, and OptiX parity against the native CPU reference for both workloads, and this is programmatically verified by the `test_rtdl_backends_preserve_same_stream_parity` unit test.

### Prevention of Overclaiming

The interpretation and associated documents rigorously adhere to the specified claim boundaries. It is explicitly and repeatedly stated across the `json`, `.md`, and `_interpretation.md` files, and verified by the `test_claim_boundaries_remain_locked` unit test, that claims such as "paper-scale RayJoin reproduction," "RTDL beats RayJoin," "broad RT-core speedup," or "v2.0 release readiness" are *not authorized*. The interpretation clearly articulates that direct performance comparisons between RayJoin's reported `Query` phase and RTDL's Python runtime call are not directly comparable due to differing phase boundaries, effectively preventing any overstatement of RTDL's current performance relative to RayJoin.

### LSI OptiX Success and PIP OptiX Weak Spot

The report correctly identifies and highlights both the success of LSI OptiX and the weak spot in PIP OptiX. The interpretation notes that "Goal2207's chunked segment-pair launch fixed the LSI OptiX capacity blocker," leading to "parity and runs much faster than RTDL's native CPU reference." Conversely, it accurately pinpoints "PIP is the clearest weak spot," observing that RTDL Embree outperforms RTDL OptiX by a significant margin for the PIP workload, indicating an underlying "RTDL OptiX PIP lowering/runtime problem." These observations are consistent with the provided performance data and are explicitly checked in the unit tests.

### Risks Identified

*   **Schema Risk:** Low. The JSON evidence summary is well-structured and comprehensive, with no apparent schema-related issues.
*   **Provenance Risk:** Low. The use of SHA-256 hashes for query streams, even when not directly committed to the repository, provides strong cryptographic assurance of their integrity and traceability. The original paths of all imported files are also recorded.
*   **Fairness Risk:** Low. The report demonstrates awareness of potential fairness issues in direct performance comparisons due to differing phase boundaries between RayJoin and RTDL metrics. This awareness, coupled with explicit authorization boundaries, mitigates fairness concerns.
*   **Timing-Contract Risk:** Medium. While acknowledged and accounted for in the claim boundaries, the differing phase boundaries between RayJoin's reported query times and RTDL's full runtime measurements present an inherent challenge for precise timing-contract comparisons. The significant performance discrepancy for PIP OptiX also points to a functional but not yet optimized timing-contract for that specific path within RTDL. The report's explicit identification of this as a "weak spot" and a "next work" item demonstrates good risk management.

## Conclusion

The Goal2209 artifact package and its accompanying interpretation provide a solid foundation for understanding the current state of RTDL's integration with RayJoin-exported query streams. The explicit claim boundaries and detailed analysis contribute to a high level of confidence in the reported findings. The identified weak spot in PIP OptiX and the differing timing-contract boundaries are clearly stated, allowing for targeted future work. The automated tests further bolster the review process.
