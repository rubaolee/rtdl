**1. Real RT backend or hidden CPU fallback?**

Real RT backend. `embree_runtime.py:750` routes `conjunctive_scan`/`grouped_count`/`grouped_sum` to `_run_db_embree()`, which calls native Embree library functions directly (`rtdl_embree_run_conjunctive_scan` etc.). The native side creates an actual `RTCDevice`/`RTCScene`, builds `DbRowBox` user-primitive AABBs, and dispatches through the Embree BVH (`QueryKind::kDbScanRay`, `kDbGroupedCountRay`, `kDbGroupedSumRay`). The CPU fallback path in `run_embree` exists only for Jaccard workloads, and is explicitly labeled as such.

**2. Inside Goal 416 contract?**

Yes. The implementation matches the accepted contract on every axis:
- `DbScanXYZ` lowering: rows encoded as per-row AABB/cube primitives on up to 3 uniform-encoded `x/y/z` axes, exact refine at hit time — matches Goal 416 exactly.
- `DbGroupAggScan` lowering: group key on `y`, scan clause on `z`, aggregate distribution on `x` — matches.
- Runtime ceilings enforced in both Python and native C++: `kDbMaxRowsPerJob = 1_000_000`, `kDbMaxCandidateRowsPerJob = 250_000`, `kDbMaxGroupsPerJob = 65_536` — match Goal 416 exactly.
- Single-group-key enforcement and integer-only sum rejection both present and tested.

**3. Any material overclaim left?**

None found. The report explicitly states: scalar `rtcIntersect1` only (no SIMD/packet overclaim), Embree is "slightly slower than CPU oracle" (no performance-win claim), no prepared-mode claim, no RT-core claim (that's OptiX territory). Performance numbers are published honestly with the explanation that this is a first-wave correctness path.

---

**ACCEPT**
