# Gemini Review for Goal2346 RTNN v2.2 Campaign - 2026-05-18

**Reviewer:** Gemini (Independent AI Reviewer)
**Date:** 2026-05-18

---

## Disclaimer

As an independent Gemini reviewer, this assessment is conducted without influence from Codex. This review does not represent a Codex+Codex consensus.

---

## Review Questions and Answers

### 1. Does Goal2346 correctly identify RTNN as PPoPP 2022 with open-source code at `https://github.com/horizon-research/rtnn`?

_Answer:_ Yes, Goal2346 correctly identifies RTNN as PPoPP 2022, published by Zhehuan Chen et al., and references the open-source implementation at `https://github.com/horizon-research/rtnn`. This is explicitly stated in the "Purpose" and "External Sources Found" sections of the campaign plan and verified by associated tests.

### 2. Does it correctly keep the goal bounded as optimization adoption and runtime reconstruction, not full paper reproduction?

_Answer:_ Yes, the plan clearly and repeatedly emphasizes that its goal is optimization adoption and runtime reconstruction, not full paper reproduction. This is evident in the "Purpose" statement ("This campaign is not a full paper reproduction..."), the "Verdict" section's boundaries, and the frequent distinction made in supporting documents (e.g., `v0_5_rtnn_gap_summary_2026-04-11.md`) between "exact reproduction," "bounded reproduction," and "RTDL extension."

### 3. Is the proposed RTDL design pressure generic and app-agnostic: `prepared_bounded_neighbor_search_3d`, radius+K, bounded outputs, partition/batch/sort policy, exact/approx metadata, and partner-owned output columns?

_Answer:_ Yes, the "Design Finding" section of the campaign plan thoroughly outlines a generic and app-agnostic design pressure, centered around `prepared_bounded_neighbor_search_3d`. It specifies generic inputs (build/query point columns, radius, k_max), outputs (bounded neighbor IDs/distances/counts or compact columns), policy options (exact/approximate, partitioning, batching, sorting, overflow behavior), and comprehensive metadata. The plan explicitly states that "These contracts remain app-agnostic."

### 4. Does the plan avoid speedup, release, or broad RT-core claims before pod evidence exists?

_Answer:_ Yes, the plan rigorously avoids premature speedup, release, or broad RT-core claims. The "Measurement rules" explicitly state that "No whole-language or broad RT-core speedup claim is authorized by this goal." The "Verdict" section includes "no speedup claim yet" and "no release claim" as clear boundaries. Furthermore, the "Hardware Boundary" section clearly defines the types of machines that can and cannot provide accepted performance evidence, requiring an RTX pod with CUDA/OptiX.

### 5. Are there missing risks before the first RTX pod benchmark attempt?

_Answer:_ While the plan effectively identifies and mitigates many risks related to hardware and scope, it could more explicitly articulate risks in the following areas before the first RTX pod benchmark attempt:
*   **Dependency Management:** Potential challenges or changes in the external RTNN project's dependencies or build process.
*   **Performance Variability:** Accounting for potential variability in RTX pod performance and ensuring benchmark consistency.
*   **Real-world Dataset Acquisition & Preparation:** The practical difficulties of acquiring, cleaning, and preparing "stanford_or_mesh_sample" or other real-world, non-synthetic datasets.
*   **Integration Complexity:** Unforeseen challenges in building and integrating the RTNN harness for data generation, execution, and timing parsing.
*   **Scalability:** Potential scalability issues that might arise with real-world, non-uniform datasets, which may not be apparent with synthetic data.

---

## Verdict

`accept-with-boundary`

**Boundary:**

*   No full RTNN reproduction claim.
*   No speedup claim yet.
*   No release claim.
*   No app-specific native RTDL entry point.
*   Next work must translate RTNN's lessons into generic bounded-neighbor runtime contracts and pod-measured evidence.

---
