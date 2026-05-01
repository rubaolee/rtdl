# Goal670: Gemini Engine Optimization Consensus Review

Date: 2026-04-20

## Overview

This is the cross-consensus review of the three primary engine performance optimization reports (OptiX, HIPRT, Vulkan) evaluated against the Goal 669 Apple RT visibility count playbook.

## Engine-Specific Verdicts

### OptiX (Codex)
**Verdict: ACCEPT WITH NOTES**

- **Validity and Actionability:** Highly valid and actionable. Correctly prioritizes prepared ray/triangle any-hit with scalar count, mirroring the Apple RT playbook.
- **Overclaims Check:**
  - *Scalar vs Row:* Explicitly warns not to compare scalar-count OptiX against full-row Embree/Vulkan/HIPRT.
  - *Prepared vs First-query:* Emphasizes reporting first-query and repeated-query costs separately.
  - *Mechanism Honesty:* Correctly boundaries OptiX RT traversal vs CUDA compute vs host-indexed paths, specifically noting that current graph workloads use a host-indexed native C++ path, and GTX 1070 results are not RT-core evidence.
- **Blockers:** None for general optimization, but correctly blocks performance claims for graph workloads until a real GPU/prepared strategy exists.

### HIPRT (Claude)
**Verdict: ACCEPT WITH NOTES**

- **Validity and Actionability:** Valid and actionable. Prioritizes prepared 2D ray/triangle and any-hit to reduce the dominant JIT/context setup overhead.
- **Overclaims Check:**
  - *Scalar vs Row:* Highlights output-contract reduction as the next high-value step.
  - *Prepared vs First-query:* Thoroughly distinguishes between one-shot (cold) and prepared query times.
  - *Mechanism Honesty:* Explicitly documents that HIPRT-on-NVIDIA/Orochi (GTX 1070) is not AMD GPU validation and does not use hardware RT cores.
- **Blockers:**
  - Large-scale claims are blocked by unquantified OOM risks (seen in previous graph evidence).
  - Any kNN performance claim for `k > 64` is blocked by a silent correctness bug (silent zero-result).
  - AMD claims are blocked until validated on actual AMD hardware.

### Vulkan (Gemini 3 Preview)
**Verdict: ACCEPT WITH NOTES**

- **Validity and Actionability:** Valid and actionable. Correctly identifies BVH caching and output materialization as critical optimizations.
- **Overclaims Check:**
  - *Scalar vs Row & Memory:* Focuses heavily on the catastrophic O(N*M) worst-case buffer allocation for workloads like LSI and PIP, advocating for pre-computed workload capacity or two-pass materialization.
  - *Mechanism Honesty:* Notes that Jaccard workloads currently fall back to the CPU oracle. Driver variability (`shaderc` across NVIDIA/AMD/Intel) is flagged.
- **Blockers:** The catastrophic memory allocation contract is a hard blocker preventing Vulkan from running large-scale claims (e.g., long exact-source packages).

## Overall Verdict
**Verdict: ACCEPT WITH NOTES**

### Consensus Summary
All three reports validate the core lessons from Goal 669:
1. **Prepared Contexts:** Moving geometry build and setup costs out of the hot loop is mandatory for all engines.
2. **Reduced Output Contracts:** Returning scalar counts/flags instead of materialized rows is the next major step for OptiX and HIPRT.
3. **Mechanism Honesty:** Reports correctly maintain strict boundaries. OptiX and HIPRT reviews explicitly forbid claiming RT-core acceleration when running on Pascal/compute, and the OptiX review forbids claiming RT traversal for host-indexed graph paths.
4. **Memory Guardrails:** Vulkan and HIPRT reviews both identify memory limits (Vulkan's O(N*M) buffer limits and HIPRT's large-scale OOM risk) as critical blockers for production-scale claims.

These reports serve as a strong, honest roadmap for the next phase of RTDL engine optimization.