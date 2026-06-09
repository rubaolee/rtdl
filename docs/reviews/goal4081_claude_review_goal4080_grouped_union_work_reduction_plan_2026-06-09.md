# Goal4081 Claude Review: Goal4080 Grouped-Union Work-Reduction Plan

Date: 2026-06-09
Reviewer: Claude (external read-only)
Artifact reviewed: `docs/reports/goal4080_fixed_radius_grouped_union_work_reduction_plan_2026-06-09.md`
Supporting evidence: Goals 4071, 4074, 4075, 4078, 4079 (pod JSON and markdown reports)

## Verdict

`accept-with-boundary`

The plan is correctly grounded in the evidence chain, names the right next engineering target, preserves the app-agnostic native boundary, and respects explicit partner choice. Three gaps in the acceptance bars prevent a clean `accept`: no minimum work-reduction threshold, no ngsim_dense regression bar, and no partition-build-overhead measurement requirement. These should be addressed in the Goal4082 scope before proceeding to implementation.

---

## 1. Is Goal4080 Correctly Grounded in the Goal4074-4079 Evidence?

**Yes, with one unverifiable citation.**

Every figure in the plan's evidence table was verified against the raw pod artifacts:

| Plan claim | Source artifact | Verified |
| --- | --- | --- |
| Partition previews 6.1x-12.8x slower at 65K clustered | Goal4071 pod JSON rows: CuPy 0.682616 s / 0.094191 s = 7.25x; Numba 1.208361 s / 0.094191 s = 12.83x | Correct |
| Native grouped-union pass dominates (Goal4074) | Goal4074 JSON: `grouped_native_sec` 0.087859 / `elapsed_sec` 0.093321 = 94.1% clustered; 0.030176 / 0.036245 = 83.2% road | Correct |
| Reset fusion does not materially move route timing (Goal4075) | Goal4075 pod: clustered after/before = 1.003x, road = 0.969x | Correct |
| Path compression reverted, no material win (Goal4078) | Goal4078 pod: clustered 0.997x, road 1.012x; decision `revert_probe_no_material_win` | Correct |
| 273,911,978 candidate hits, 273,834,399 same-root culled, 547,999,682 root calls (clustered3d) | Goal4079 pod JSON `clustered3d_65536.json` telemetry array `[4]`, `[5]`, `[8]` for `same_root_on_direct_off` variant (last_telemetry, repeat 2) | Exact match |
| ~2 root finds per candidate | 547,999,682 / 273,911,978 = 2.001 | Correct |

The plan also cites "Goal3999 / Goal4014 / Goal4066" for the claim that partition summaries are useful for capacity control. Those reports are not included in the provided evidence chain and could not be verified independently. The characterization is consistent with the Goal4071 narrative (partition-convergence is slow but graph-correct), but the reviewer cannot confirm the specific claims about capacity control and safe-full/ambiguous classification accuracy from the provided artifacts alone.

The causal chain the plan draws—same-root culling is effective but happens after expensive candidate traversal, therefore work must be reduced upstream before the root-check stage—is directly supported by the Goal4079 JSON. The 99.972% cull rate on clustered3d confirms the opportunity; the ~2 root-finds-per-candidate figure confirms the cost even before culling takes effect.

---

## 2. Are the Acceptance Bars Strict Enough?

**Mostly yes. Three gaps identified.**

**Strengths:**

- The performance bar requires beating the current recommended route on *production timing*, not telemetry timing. This is critical: Goal4079 telemetry elapsed (~0.209 s) is roughly 2.2x the production elapsed (~0.093 s, Goal4074), because diagnostic counters add atomic overhead. Accepting only non-telemetry comparisons closes a significant loophole.
- The correctness bar uses normalized component-size signature equality, as established in Goal4071. This correctly handles the `cluster_sizes` vs `component_sizes` schema difference between full RT-DBSCAN and the graph-component-only route.
- The completeness bar (fail-closed on overflow, incomplete coverage, unsupported partner/device, stale metadata) is appropriate.
- The claim-discipline bar is comprehensive and consistent with the established project boundary.
- The app-agnostic boundary bar explicitly lists forbidden vocabulary and matches the existing native_engine_row_contract pattern (`generic_prepared_fixed_radius_grouped_union_3d_all_items_self_device_parent_workspace`) seen in all pod artifacts.

**Gap 1 — No minimum work-reduction threshold.**
The "Work reduction" bar reads: "Demonstrate lower candidate/root work than Goal4079 for the rows it claims to improve." A candidate that reduces clustered3d candidate hits by 0.1% would pass this bar literally while adding substantial complexity. Recommend requiring a stated minimum reduction (e.g., "at least 50% reduction in candidate hits on the profile with the highest safe-full fraction") before promotion from candidate to `accepted_preview`.

**Gap 2 — No ngsim_dense regression bar.**
The performance bar covers clustered3d_65536 and road3d_65536 but does not mention ngsim_dense_65536. Goal4079 measured ngsim_dense with a much lower cull rate (99.397%) and lower absolute candidate volume (12M hits vs 273M). A partition-convergence approach that partitions too coarsely could increase ngsim_dense traversal overhead without providing a work reduction on boundary pairs. The promotion gate should require no regression on ngsim_dense_65536 production timing.

**Gap 3 — Partition-build overhead not measured.**
The required contract (step 2) says "build or consume partition columns with AABBs and counts." The Goal4082 scope ("expose partition summary columns to the native candidate") does not require measuring how long partition column construction takes. If partition column build time on device is non-trivial relative to the ~93 ms total clustered elapsed, the work reduction may not produce net speedup. Goal4082 should be required to record partition-build elapsed time as a separate counter, comparable to the Numba signature elapsed recorded in Goal4074.

---

## 3. Does the Plan Preserve the App-Agnostic Native-Engine Boundary?

**Yes. The boundary is well-enforced.**

The candidate name `prepared_fixed_radius_partition_convergence_grouped_union_3d` uses only vocabulary from the allowed list (fixed-radius, partition, convergence, grouped-union). The forbidden list (DBSCAN, cluster, epsilon, min-points, road, trajectory, benchmark-app labels) is explicit and complete relative to the current native ABI surface.

The required contract (steps 1-7) uses only generic language: "3D points and radius," "partition columns," "component parent/label/signature columns compatible with the existing fixed-radius grouped-stream component contract." There is no DBSCAN vocabulary in any of the required contract items.

The implementation sequence explicitly prohibits adding a new default route at Goal4081: "add no new default route." This is consistent with the project's existing pattern where every new route candidate begins as a non-default, must pass all acceptance bars, and requires external consensus before promotion.

The native_engine_row_contract string visible in all Goal4079 JSON artifacts (`generic_prepared_fixed_radius_grouped_union_3d_all_items_self_device_parent_workspace`) confirms the existing boundary is enforced at the artifact level. The plan's candidate is a natural extension of this naming convention.

---

## 4. Does the Plan Respect Explicit User Partner Choice and Avoid Hidden Dispatch?

**Yes. Partner discipline is explicitly required.**

The acceptance bar reads: "No app-shaped native ABI, no DBSCAN vocabulary in native/core runtime symbols, no hidden dispatch, no automatic partner selection." The phrase "no automatic partner selection" appears in both the acceptance bar and the boundary section, making it a hard gate rather than a guideline.

The plan does not describe any dispatch logic that would select Numba vs CuPy based on device availability, data size, or any other runtime signal. The implementation sequence (Goals 4081-4085) treats the candidate as an explicit opt-in route, not a transparent replacement.

This is consistent with the established project pattern: Goal4074 explicitly compares `direct_side_effect` as a caller-controlled toggle (`grouped_union_direct_side_effect=True`), not as an auto-promoted default. The Goal4079 JSON confirms that variants are invoked by explicit caller label (`same_root_on_direct_off`, `same_root_off_direct_off`), not by automatic dispatch.

One observation: the plan does not specify how the candidate primitive will be invoked in the Goal4085 comparison harness (whether it requires the same partner keyword as the current recommended route or a new keyword). The implementation should be careful not to let the comparison harness auto-select the candidate based on profile characteristics.

---

## 5. What Should the Main AI Implement or Measure Next?

**Recommended sequence with augmentations:**

The plan's five-step sequence is correct in order and scope. The following measurements should be added or clarified at specific steps:

**At Goal4081 (feasibility):**
- Measure the number of partition pairs for each of the three target profiles at representative partition counts (e.g., 64, 128, 256 partitions). This determines whether the partition-pair classification step scales to a reasonable problem size.
- Confirm that the existing grouped-union OptiX path has a clean integration point for partition pair ranges without requiring a new PTX build. If not, report the estimated rebuild cost.

**At Goal4082 (partition summary bridge):**
- Record partition-build elapsed time as a new named counter: `partition_summary_build_sec`. This must be included in the Goal4085 production-timing comparison so that partition-build overhead is visible in the net elapsed.
- Estimate the safe-full fraction for each target profile at each partition count explored. If the safe-full fraction is below ~50% for clustered3d (the highest-candidate-volume profile), the work reduction will be limited and Goal4083 may not be worth the complexity.

**At Goal4085 (comparison):**
- Use `repeat=6, warmup=2` (same as Goal4074) for production-route comparison, not the `repeat=3` telemetry protocol used in Goal4079.
- Report candidate hits, same-root culls, reported candidates, and root calls for the new candidate, comparable to the Goal4079 baseline table. Without this, the "Work reduction" acceptance bar cannot be verified.
- Include ngsim_dense_65536 in the comparison even if the plan's performance bar only requires clustered3d and road3d to improve. A regression on ngsim_dense should block promotion.

**Simpler alternatives considered and rejected:**
- AABB-only pre-filter on the existing RT pipeline (without partition union): this would reduce candidate hits only at the per-point level and would not address the structural problem of ~2 root-reads per surviving candidate. Goal4078 already showed that reducing root-read work alone (path compression) does not move the needle; the volume reduction must happen before candidate traversal begins.
- Increasing the BVH leaf size to coarsen traversal: this changes an OptiX build parameter, not the union-find work, and would likely hurt correctness or increase false negatives.

The partition-convergence hybrid proposed in Goal4080 is the right approach. The key engineering risk is whether partition-build time plus boundary traversal time is less than the 273M candidate traversal time it replaces. Goal4082 must measure this before Goal4083 is implemented.

---

## Summary

| Question | Finding |
| --- | --- |
| Correctly grounded in Goal4074-4079 evidence? | Yes; all cited figures verified against raw JSON; one citation (Goal3999/4014/4066) unverifiable from provided artifacts |
| Acceptance bars strict enough? | Mostly yes; three gaps: no minimum work-reduction threshold, no ngsim_dense regression bar, no partition-build overhead requirement |
| App-agnostic native-engine boundary preserved? | Yes; forbidden vocabulary explicit and consistent with existing ABI naming |
| Explicit user partner choice respected, no hidden dispatch? | Yes; "no automatic partner selection" is a hard gate; no dispatch logic described |
| What to implement or measure next? | Goal4081 feasibility (partition pair count + integration point); Goal4082 adds partition-build elapsed as a counter and estimates safe-full fraction before Goal4083 implementation; Goal4085 uses production-route protocol and includes ngsim_dense |

**Verdict: `accept-with-boundary`**

Proceed with Goal4081, conditioned on adding (a) a minimum work-reduction threshold to the acceptance bars before Goal4083, (b) a ngsim_dense regression gate, and (c) partition-build overhead measurement at Goal4082.
