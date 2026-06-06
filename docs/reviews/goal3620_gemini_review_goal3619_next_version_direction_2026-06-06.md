# Goal3620 - Gemini Review of Goal3619 Next-Version Major Direction

Date: 2026-06-06

Reviewer: Gemini

## Verification of Proposal Soundness and Bounding

The Codex proposal for the next version's direction, focusing on "contract-and-residency first," is technically sound and honestly bounded.

### Technical Soundness

1.  **Pillar 1 (Formal Primitive Contracts):** This is a critical foundation for any robust high-performance library. Formalizing contracts with adversarial tests ensures correctness, reduces ambiguity, and enables clearer optimization targets.
2.  **Pillar 2 (Device-Resident Typed Primitive Outputs):** This directly addresses a major performance bottleneck in GPU computing: data movement between host and device. Minimizing transfers by keeping data resident on the device when possible is a well-established optimization strategy. The explicit statement that this is "not a true-zero-copy claim until measured and reviewed" demonstrates honest bounding.
3.  **Pillar 3 (Benchmark-Driven Runtime Extensions):** This approach wisely uses real-world application pressures to drive generic runtime improvements, preventing the introduction of app-specific native logic that can hinder generality and maintainability.
4.  **Pillar 4 (Partner Freedom):** Providing users with choices and evidence-based support matrices for partners, rather than imposing defaults, is a flexible and user-centric strategy that acknowledges the diversity of ecosystems.
5.  **Pillar 5 (Claim Governance):** The rigorous requirements for public claims (exact contracts, routes, datasets, baselines, correctness evidence, external review, and 3-AI consensus) are essential for maintaining credibility and preventing premature or unsubstantiated claims.

### Honest Bounding

The report explicitly and repeatedly states its limitations and what it **does not yet prove**.
*   The "Status" section clearly disclaims authorization for any release, public wording, or specific performance claims.
*   The "What This Does Not Yet Prove" section specifically lists several critical points not covered by current evidence, including RayJoin paper reproduction, RTDL beating original RayJoin, broad RT-core speedup, true zero-copy, and a complete segment-pair count contract.
*   The "Stop/Continue Rule For Performance Work" provides clear and pragmatic criteria for when to engage in further performance tuning, preventing open-ended, incremental work without significant impact.

These elements collectively demonstrate strong honest bounding within the proposal.

## Answers to External Review Questions

**1. Do you accept the Codex recommendation that the next version should be contract-and-residency first?**
Yes, this direction is accepted. Focusing on formal primitive contracts ensures correctness and clarity, which are foundational for a robust, high-performance library. Prioritizing device-resident outputs directly addresses a major performance bottleneck (data movement) in GPU computing. This approach is more sustainable than continuous app-specific tuning.

**2. Do you agree that more current-version tuning should stop unless it satisfies the stop/continue rule above?**
Yes, entirely agreed. The "Stop/Continue Rule For Performance Work" provides a clear and pragmatic framework to prevent diminishing returns from incremental tuning. Continuing tuning only for correctness fixes, large material improvements, generic capability creation, or missing evidence ensures resources are allocated effectively.

**3. Do you agree that shader injection should remain parked behind device-resident typed outputs and primitive contracts?**
Yes, agreed. Device-resident typed outputs and primitive contracts are more fundamental and broadly applicable improvements. They establish a solid base for data flow and correctness. Shader injection, while potentially powerful, can easily lead to app-specific native logic if not carefully governed by well-defined contracts and residency principles. Focusing on the latter first will likely yield more generic and durable performance gains.

**4. Are the proposed first contract targets (`segment_pair_*`) the right starting point?**
Given the context of recent RayJoin repair and route work, focusing on `segment_pair_intersection_count`, `segment_pair_left_id_dense_count`, and `segment_pair_intersection_rows` as the first contract targets seems appropriate. These are directly related to the area where significant internal performance wins have been observed, indicating a ripe area for formalization and further optimization through clear contracts. The required adversarial tests and policy definitions listed are also critical for robustness.

**5. Is the partner policy correct: user-chosen partners, measured support, no automatic public default?**
Yes, this partner policy is correct and well-reasoned. It respects user autonomy, promotes transparent evidence-based recommendations, and avoids prematurely locking into specific ecosystem partners. This approach ensures RTDL remains a flexible and generic engine.

**6. What must be added or changed before this can become a 3-AI consensus direction?**
Before this can become a final 3-AI consensus direction, the following should be addressed:
*   **Clarification on "Partner-Compatible Handoff Contracts":** While Pillar 4 mentions "partner-compatible handoff contracts," more detail or examples on what these entail would be beneficial. How will RTDL ensure seamless integration with various partners (e.g., Triton, CuPy, Numba, Torch) without prescribing their use? What are the mechanisms for these handoff contracts?
*   **Initial Primitive Definition Scope:** For Pillar 1, while the initial target primitives are clear, defining the scope or criteria for selecting *future* primitives to formalize would be helpful for long-term planning. How will the team decide which primitives get the "formal contract" treatment next?
*   **Dependency on External Components/Libraries:** The proposal implicitly relies on external components (e.g., OptiX, CuPy for baselines, potential partners). While not explicitly a "change," acknowledging and perhaps briefly outlining the strategy for managing dependencies (e.g., versioning, compatibility, updates) would add robustness to the overall direction.

## Gemini Verdict

`accept-with-boundary`
The proposed direction is sound and well-justified. The boundary aligns with Codex's self-assessment that it's an internal plan candidate and requires further reconciliation for 3-AI consensus.
