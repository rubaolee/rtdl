# Gemini Review: Goal4080 Grouped-Union Work-Reduction Plan

Date: 2026-06-09
Verdict: `accept`

## Summary

This review covers the Goal4080 plan, which proposes a new generic primitive, `prepared_fixed_radius_partition_convergence_grouped_union_3d`, to address the performance bottlenecks identified in the Goal4074-4079 evidence chain.

## Engineering Direction Evaluation

The plan shifts from "wrapper-level tuning" to "work-reduction primitive design." This is the correct response to the evidence:
- **Bottleneck Identification:** Goal4074/4079 proved that the recommended RT-core route is dominated by native candidate enumeration and redundant root-checks (culling ~99.9% of candidates after visiting them).
- **Work Reduction Strategy:** The proposed hybrid approach (partition summaries + safe-full union + ambiguous-only RT traversal) directly targets the volume of work identified in Goal4079.
- **Incremental Feasibility:** The sequence starting with Goal4081 (ABI feasibility) ensures that the complexity of partition-aware traversal is weighed against existing pipeline stability before broad implementation.

## Claim Boundary Audit

All claim boundaries are strictly enforced:
- No release authorization.
- No public speedup or paper-reproduction wording.
- No broad RT-core or whole-app acceleration claims.
- No automatic partner selection or hidden dispatch.
- No app-specific native-engine logic or vocabulary.

## Responses to Handoff Questions

1. **Is Goal4080 correctly grounded in the Goal4074-4079 evidence?**
   Yes. Goal4074/4079 showed that minor optimizations (Path Compression in 4078, Reset Fusion in 4075) do not move the needle because the underlying work (candidate enumeration) is too high. 4080 correctly targets the root cause.

2. **Are the acceptance bars strict enough?**
   Yes. Requiring the candidate to beat the current recommended route in production timing (not just telemetry) on both `clustered3d` and `road3d` is a high and necessary bar. The "fail closed" requirement for metadata staleness is also critical for correctness.

3. **Is there a simpler generic candidate that could reduce candidate/root work without building a partition-convergence route?**
   No material "simpler" candidate is evident. Goal4078 proved that even standard union-find improvements like path-halving are insufficient to overcome the candidate pressure. Spatial partition-based culling is the standard next-step for this density of fixed-radius graph.

4. **Does the plan preserve the user-choice partner principle and native app-agnostic boundary?**
   Yes. It explicitly forbids app-specific vocabulary and requires the primitive to consume partition columns that are built or selected at the partner/app level, maintaining the explicit dispatch model.

5. **What should the main AI implement or measure next?**
   Proceed with **Goal4081 (native/API feasibility)**. The investigation should focus on whether the OptiX `RayGen` or `Intersection` programs can consume partition-pair ranges without increasing register pressure or divergent branching to the point of negating the work-reduction wins.

## Final Verdict

The plan is technically sound, evidence-driven, and maintains the required architectural boundaries.

**Verdict: `accept`**
