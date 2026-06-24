# Review: Goal 415 and Goal 416 — v0.7 RT DB Execution Interpretation and Lowering Contract

Date: 2026-04-15
Reviewer: Claude Sonnet 4.6
Documents reviewed:
- `docs/goal_415_v0_7_rt_db_execution_interpretation.md`
- `docs/reports/goal415_v0_7_rt_db_execution_interpretation_2026-04-15.md`
- `docs/goal_416_v0_7_rt_db_lowering_runtime_contract.md`
- `docs/reports/goal416_v0_7_rt_db_lowering_runtime_contract_2026-04-15.md`
- `docs/reports/goal412_rt_db_workload_analysis_for_next_version_2026-04-15.md`

---

## Review question 1: Is Goal 415 honest and coherent about the distinction between semantic DB engines and future RT engines?

**Verdict: Yes, with one missing operational detail.**

The honesty boundary is the most important structural feature of the 415 report, and it holds. The three-tier split — `cpu_python_reference` as semantic truth, `cpu` as native oracle, `postgresql` as external correctness anchor — is correctly labeled as non-RT. The report explicitly refuses to let any of those count as an RT backend. That is the right call and it is stated clearly.

The definitions of `DenormTable`, `PredicateSet`, and `GroupedQuery` all include a "does not mean" section. These exclusions are correct and well-chosen:

- `DenormTable` is not a live table or a transactional abstraction.
- `PredicateSet` is not arbitrary boolean logic.
- `GroupedQuery` is not arbitrary SQL grouping semantics.

The execution-stage split (semantic engines execute full semantics directly; RT engines execute only after a candidate-discovery contract is defined) is coherent and matches what Goal 412 recommended.

**One missing operational detail**: the report introduces `traverse(..., mode="db_scan")` and `traverse(..., mode="db_group")` without specifying where these mode strings live in the actual API surface. They are used as conceptual labels, not API signatures. This is acceptable at this design stage, but the report should note explicitly that these are semantic descriptions pending concrete API closure in Goal 416 and the backend goals. A reader doing a backend implementation should not treat these mode strings as already-defined API.

---

## Review question 2: Is Goal 416 a bounded and implementable RT lowering for Embree/OptiX/Vulkan?

**Verdict: Mostly yes, but one area is genuinely underspecified.**

The two-lowering structure (`DbScanXYZ` and `DbGroupAggScan`) is the right architecture decision. Separating the scan case from the grouped case avoids the mistake of forcing one layout to carry both workloads. The backend-neutral primitive contract (row_id, primary coordinates, exact scalar payload, optional group key code, optional aggregate value) is clean and does not entangle the three backends.

AABB/cube primitives are the right choice. Embree has first-class AABB support for custom primitives. OptiX supports them via custom intersection programs. Vulkan supports them via `VK_KHR_acceleration_structure` AABB geometry. The statement "AABB support is natural across Embree, OptiX, and Vulkan" is accurate, but the report should note that AABB performance characteristics differ between OptiX/Vulkan and Embree: OptiX and Vulkan AABB intersection requires custom closest-hit/intersection shader code, while Embree's custom geometry API is host-CPU-bound. This is not a contract problem but it is a performance expectation problem a backend implementer will encounter.

The over-boundary rule for `DbScanXYZ` (>3 scan clauses: partition into groups, run one RT job per group, intersect row-id bitsets host-side) is sound. Row-ids are unique per row, so bitset intersection across multiple RT jobs is correct. This works.

**The underspecified area is `DbGroupAggScan`, specifically the x-axis for `grouped_count`.**

The report states:

> for `grouped_count`, `x` may be a constant or row-spread coordinate

The word "may" is doing too much work here. There are two cases:

1. If `x` is a constant for all rows, every row has the same x coordinate. The BVH has no useful structure on the x-axis. The scan region on x degenerates to a single plane. This is technically functional but wastes one dimension of the layout.
2. If `x` is a row-spread coordinate (e.g., a row-index-based spread), the BVH gets better distribution but the meaning of the x-axis is synthetic, not data-derived.

The report does not say which to use, when to use each, or what the BVH quality implications are. A backend implementer cannot derive this from the current text. Goal 416 should specify a concrete default: for `grouped_count`, use a deterministic row-index spread on x, and document that this is synthetic distribution, not a data attribute.

The `grouped_sum` x-axis case (distributes the measure field) is better specified but still defers the exact encoding choice to backend implementation. The report says "the exact numeric value remains in payload," which is correct — the spatial coordinate can approximate while the payload is exact. This is an acceptable deferral.

---

## Review question 3: Does the proposed contract stay within what RTScan and RayDB actually justify?

**Verdict: Yes for the core, with one slightly generous attribution.**

`DbScanXYZ` is direct RTScan lineage:
- Uniform encoding of multiple columns into 3D coordinates: RTScan.
- Region-based ray queries (cuboid query regions): RTScan.
- Approximate spatial discovery + exact refine: RTScan.
- Short matrix-style rays: RTScan.

All four elements are in the 412 analysis of RTScan. The `DbScanXYZ` lowering does not exceed what RTScan demonstrates.

`DbGroupAggScan` is RayDB lineage:
- Offline BVH build: RayDB.
- Fused scan + group + aggregate in one RT job: RayDB.
- Emit partials, merge host-side: consistent with RayDB's approach of keeping non-RT work outside the fused core.
- Bounded to one group key: an appropriate first-wave restriction that is more conservative than RayDB's demonstrated scope.

**The one slightly generous attribution** is the over-boundary decomposition for >3 scan clauses. Goal 416 says:

> This mirrors RTScan's grouped-predicate logic

RTScan's grouped-predicate logic is about building separate attribute-group BVHs and selecting which BVH to use per query. It is not precisely "run multiple RT jobs and intersect bitsets host-side." The bitset-intersection approach is a reasonable adaptation but is not a direct RTScan result. The claim should be "inspired by RTScan's attribute grouping" rather than "mirrors." This is a minor phrasing issue, not a design error, but it should be corrected to avoid misleading future reviewers.

The first-wave exclusion of `avg/min/max` on RT backends is more conservative than what RayDB demonstrates (RayDB does support these). This conservatism is acceptable and honest. The report does not need to justify it further because the goal is a first-wave contract, not a complete one.

---

## Review question 4: Are any claims overstated, missing a key limitation, or likely to produce a bad backend design?

**Five concrete issues follow. Issues 1 and 2 are the ones that could directly cause a bad backend design.**

### Issue 1 (backend design risk): x-axis encoding for `grouped_count` is underspecified

Already noted above. A backend implementer cannot make a correct decision from the current text. The risk is that two different backends make different choices, and then the cross-engine correctness gate (Goal 429) finds mismatches that are caused by layout choices, not logic errors. This needs to be resolved before any backend implementation begins.

**Concrete fix**: Add a sentence: "For `grouped_count`, use a synthetic row-index spread on `x` in the range `[0, N)` normalized to `[0, 1]`. This is not a data attribute; it exists only to distribute rows across the x-axis and improve BVH quality."

### Issue 2 (backend design risk): no explicit maximum on group cardinality

The first-wave support bound says "exactly one group key" and "secondary conjunctive refine clauses." It does not say how many distinct values the group key can have. The emit/merge rule says "final merge remains bounded host-side." That claim is only true if group cardinality is bounded by a small constant. For a group key with millions of distinct values, the partial emit table can be arbitrarily large and the "bounded host-side" claim becomes misleading.

Goal 412 mentioned this risk in the RayDB section: "when all hits contend on the same aggregate slot, atomic accumulation can collapse parallelism." The dual problem — too many distinct groups — is equally real.

**Concrete fix**: State an explicit first-wave group cardinality limit (e.g., ≤ 256 distinct group key values, or "small enough that the partial accumulator table fits in a pre-allocated host-side buffer"). The exact number matters less than the existence of a stated bound.

### Issue 3 (minor omission): Data Sieving is not in the build lowering

The `DbScanXYZ` probe lowering mentions "If Data-Sieving-style summaries exist, shrink the refine region first." But the build lowering does not mention constructing those summaries. This creates a one-sided reference: the probe side can optionally use Data Sieving summaries, but the build side has no instruction to build them. A backend implementer reading only the build lowering will not know to include this.

**Concrete fix**: Add an optional step 5 to the `DbScanXYZ` build lowering: "Optionally, build per-column approximate range summaries (Data-Sieving-style) for use during probe-side region shrinkage."

### Issue 4 (missing assumption): no BVH rebuild policy stated

Neither Goal 415 nor Goal 416 states what happens when the `DenormTable` changes between queries. Goal 412 stated "BVHs must be pre-built offline" but that assumption is not carried forward into the lowering contract. A backend implementer will encounter this question immediately when building the Embree backend.

**Concrete fix**: Add one sentence to the `DbScanXYZ` and `DbGroupAggScan` build lowering sections: "The acceleration structure is built once per `DenormTable` version. If the table changes, the acceleration structure must be fully rebuilt before the next probe."

### Issue 5 (minor, not a design risk): NULL handling is explicitly absent

The report does not say what RTDL does with NULL values in scan columns or group keys. Since RTDL is "not a DBMS," the answer is probably "caller must supply clean data without NULLs." But this should be stated explicitly so that backend implementations do not each make their own choice. An unstated assumption here could cause behavior divergence between Embree (where a NaN coordinate produces undefined BVH behavior) and PostgreSQL (which has standard NULL semantics).

**Concrete fix**: Add one sentence to the `DenormTable` definition in Goal 415: "Columns used in scan or group positions must contain no NULL or NaN values. Handling of NULL/NaN is a pre-condition on the caller, not a runtime responsibility of RTDL."

---

## Summary

| Item | Verdict |
|---|---|
| Goal 415 honesty boundary | Correct and well-stated |
| Goal 415 execution split | Coherent and matches Goal 412 |
| Goal 415 missing detail | `traverse` mode strings need API closure note |
| Goal 416 two-lowering structure | Correct architecture decision |
| Goal 416 primitive contract | Clean and backend-neutral |
| Goal 416 `DbScanXYZ` | Sound and implementable |
| Goal 416 `DbGroupAggScan` x-axis for count | Underspecified — fix before backend work begins |
| Goal 416 group cardinality bound | Missing — must be stated |
| Attribution "mirrors RTScan" | Slightly generous — soften phrasing |
| Data Sieving in build lowering | Absent — minor gap |
| BVH rebuild policy | Unstated — should be explicit |
| NULL handling | Unstated — should be explicit |

The two issues that could directly produce a bad backend design are:

1. The underspecified x-axis encoding for `grouped_count` in `DbGroupAggScan`
2. The missing group cardinality bound

Both need a concrete fix before any backend implementation begins. All other issues are minor clarifications. The overall framework across Goals 415 and 416 is honest, stays within what the papers justify, and does not overclaim RTDL's scope.
