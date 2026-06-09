# Goal4204: Gemini Review of Goal4201/4202 RT-DBSCAN Policy Decision

Date: 2026-06-09
Reviewer: Gemini CLI
Verdict: `accept-with-boundary`

## Summary

This review covers the Goal4201/Goal4202 chain regarding the deterministic boundary-assignment policy for fixed-radius grouped-stream front doors. The investigation successfully quantified the performance cost of the theoretically robust `lowest_component_root_two_pass` policy and demonstrated that the optimized `lowest_candidate_then_root` (one-pass) route maintains parity with the deterministic reference contract across several standard test datasets.

## Technical Analysis

### 1. Timing Methodology (Goal4201)
The methodology in `scripts/goal4201_rt_dbscan_boundary_policy_fair_timing.py` is sound. It correctly:
- Alternates the execution order of policies to mitigate warm-up or thermal biasing.
- Uses `cuda.synchronize()` to ensure accurate kernel timing.
- Captures multiple repeats and reports median ratios.
- Finding: Two-pass is 1.4x to 1.9x slower than one-pass on non-trivial datasets (e.g., `clustered3d`, `road3d`), which justifies keeping it as an explicit machinery rather than the default route.

### 2. Reference Parity (Goal4202)
The comparison against the CPU reference contract (`src/rtdsl/predicate_aware_boundary_union.py`) is valid. The `goal4202` script correctly:
- Reproduces candidate pairs and predicate flags on the CPU.
- Uses a stable O(n²) reference implementation to verify native outputs.
- Confirms that both one-pass and two-pass policies match the reference labels for the tested scales (up to 1024 points).
- Finding: One-pass parity is likely achieved because the "observed root" captured during the OptiX traversal is resolved through the final warmed-up `parent` array in the Numba label consumer.

### 3. Policy Decision
The current decision—keep `lowest_component_root_two_pass` as an explicit reference route and continue using one-pass as the performance default—is technically conservative and correct. While one-pass matches the reference in the tested scenarios, the two-pass route is the only one that guarantees the "lowest root" property by construction (the first pass fully warms the union-find structure before the second pass assigns boundary points).

## Claim Boundary Audit

I have verified that the following claim boundaries are strictly maintained:
- **No Speedup Claims:** Reports and metadata explicitly state `public_speedup_claim_authorized: false`.
- **No Release Readiness:** Front-door status remains `candidate_requires_native_implementation` or `accepted_preview` without release authorization.
- **No Broad RT-Core Acceleration Claims:** Performance is scoped to specific grouped-stream primitives.
- **No Hidden Dispatch:** All policy selections are explicit in the `prepare` calls.

## Required Evidence for Promotion

Before promoting the one-pass route to a "deterministic-bound" policy status, the following evidence is required:
1. **Adversarial Fixtures:** Testing on synthetic fixtures specifically designed to trigger root-shadowing (e.g., overlapping clusters where the first observed root for a boundary point is not the global minimum for that component).
2. **Larger Scale Parity:** Signature-only parity checks at scales (e.g., 1M+ points) where full label materialization is impractical for the CPU reference.
3. **Formal Policy Renaming:** Renaming the "one-pass" route to reflect its deterministic guarantee (if proven) rather than its implementation detail.

## Conclusion

The Goal4201/4202 evidence is high-quality and supports the current architectural direction. The two-pass route provides a vital correctness baseline, while the one-pass route provides the necessary performance for production workloads, with evidence suggesting they are functionally equivalent for the majority of use cases.
