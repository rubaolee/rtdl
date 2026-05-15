# Review: Goal2056 Control-App RawKernel Pod Follow-Up

- **Reviewer:** Gemini CLI (Independent Review)
- **Date:** 2026-05-15
- **Verdict:** `accept-with-boundary`

## Executive Summary

Goal2056 successfully leveraged an active NVIDIA L4 pod to collect performance and correctness evidence for former-control applications migrated to the v2 Python+CuPy RawKernel+RTDL architecture. The review confirms that the work adheres to the user-approved fairness rule: comparing v2 against a v1.8 Python+RTDL baseline without user-defined C/C++ extensions.

The work is accepted with a clear boundary: it demonstrates significant speedups for specific database and polygon workloads at moderate scales (up to 4096 and 1024 copies respectively) while explicitly documenting scalability and environment limitations that prevent a broader v2.0 readiness claim.

## Evidence Validation

### 1. Database Analytics (4096 Copies)
- **Artifact:** `docs/reports/goal2056_database_rawkernel_cupy_optix_l4_4096.json`
- **Result:** v2 median (0.0749s) vs v1.8 median (0.3008s) = **0.249x ratio** (~4.0x speedup).
- **Correctness:** `all_match_v1_8_python_rtdl_oracle` is `true`. Payload signatures match.

### 2. Polygon Workloads (1024 Copies)
- **Artifact:** `docs/reports/goal2056_polygon_rawkernel_cupy_optix_l4_1024.json`
- **Apps:** `polygon_pair_overlap_area_rows` (0.929x ratio) and `polygon_set_jaccard` (0.866x ratio).
- **Correctness:** Both apps show modest speedups and perfect parity with the v1.8 oracle.

### 3. Pod Environment Repair
- The report documents a successful repair of the pod environment (installing `libgeos-dev`) to resolve build failures in the v1.8 oracle, ensuring baseline measurements were achievable.

### 4. Negative Findings & Boundaries
The work is transparent about the following hard boundaries:
- **Scalability:** Polygon workloads encountered `CUDA driver error: out of memory` at 4096 copies, indicating that candidate paging or memory-bounded contracts are still required for large-scale polygon control.
- **Graph App:** A full run at 4096 copies was blocked by the graph v1.8 baseline execution time, suggesting the need for smaller copy sizes or skipped baselines for future graph scaling tests.

## Boundary Definition

**Accepted Claims:**
- v2 RawKernel Database app is ~4x faster than v1.8 at 4096 copies on L4.
- v2 RawKernel Polygon apps are modestly faster than v1.8 at 1024 copies on L4.
- Pod environment is now capable of building GEOS-dependent oracles.

**Prohibited Claims:**
- broad v2.0 release readiness.
- broad all-control-app or all-scale speedup.
- Polygon scalability to 4096 copies.
- Package-install readiness.

## Conclusion

The artifacts and reports provided under Goal 2056 are high-quality, honest, and technically sound. The use of the `accept-with-boundary` verdict is appropriate given the mixture of clear wins and documented technical obstacles.

**Final Verdict:** `accept-with-boundary`
