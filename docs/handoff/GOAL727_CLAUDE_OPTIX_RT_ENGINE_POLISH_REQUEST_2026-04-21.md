# GOAL 727: Claude OptiX/RTX Engine Polish Request

**Date**: 2026-04-21
**Target AI**: Claude

## Objective
Your primary task is to polish the OptiX/RTX app performance landscape. This is a targeted optimization and validation goal with strict rules of engagement. You must distinguish true hardware RT traversal from CUDA compute or host-indexed fallbacks, implement and patch only bounded low-risk improvements, rigorously test those patches, and conclude with an exact app-level RTX claim status report.

## Critical Context & Boundaries
Before you begin, you must understand the current accepted state established during the Goal 695/696 reviews:
- **No Speculative Paradigms**: Do not attempt to implement speculative paradigms that violate physical hardware limits (e.g., using "missed rays" to accumulate Barnes-Hut mass, since RT hardware does not enumerate or invoke shaders on missed BVH nodes efficiently).
- **Hardware Honesty**: Do NOT use timing data from GTX-class GPUs (like the GTX 1070) as evidence for RT-core acceleration. 
- **Existing Patches**: The fixed-radius summary paths for Outlier Detection and DBSCAN (core flags) are already implemented and proven to bypass Python dict-row materialization. They are currently classified as `cuda_through_optix` until formal RTX-phase profiling justifies changing their status.

## Required Actions
1. **Polish OptiX App Performance**: Identify and patch localized, low-risk performance bottlenecks (e.g., optimization of data packing, memory alignment, or basic OptiX kernel fine-tuning). Do not perform massive architectural overhauls. 
2. **Distinguish True Traversal**: Keep a strict division between operations that fundamentally use RT Core BVH Traversal vs. those that just use the OptiX backend library as a CUDA compute or host-indexing wrapper. 
3. **Rigorous Testing**: Every performance patch must be tested against the CPU Oracle to guarantee zero correctness degradation. 
4. **Report Exact RTX Claim Status**: Write a final assessment report stating the exact categorization for each app. You must determine if any app can now honestly be moved to `optix_traversal` based on RTX-class evidence.

## Deliverables
1. Source files patched with low-risk performance improvements.
2. Verified passing test suite logs.
3. A markdown report in `/Users/rl2025/rtdl_python_only/docs/reports/` detaling exactly what was improved, confirming strict boundary adherence, and listing the updated app-level RTX claim status.
