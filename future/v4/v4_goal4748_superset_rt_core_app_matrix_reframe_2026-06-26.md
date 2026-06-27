# V4 Goal4748 - Superset RT-Core App Matrix Reframe

Date: 2026-06-26

Status: `reframe_complete_not_benchmark_execution`

Decision:
`v4_must_be_superset__compatibility_and_new_performance_are_separate`

## Correction

V4 is not an enemy of V2.14 or V3. V4 must be the current user-facing superset
of mature RTDL RT-core work. Existing V2.14/V3 RT-core routes are allowed and
expected in V4 as compatibility/inherited routes.

The forbidden claim is narrower:

```text
Do not count inherited V2.14/V3 functionality as a new V4 performance win.
```

The correct user-facing matrix therefore has two fairness questions:

1. **Compatibility fairness:** can V4 fairly expose and compare the same app
   route that V2.14/V3 already had?
2. **New-performance fairness:** can V4 fairly claim the route is faster because
   of a new V4 generic operator/runtime mechanism?

## RT-Core-Only Benchmark App Implementation Matrix

Embree is excluded from primary denominators here. It may exist as a CPU/control
reference elsewhere, but this table is about NVIDIA OptiX/RT-core routes.

| App | V2.14 RT-core implementation | V3 implementation | V4 current/superset implementation | Compatibility fair? | New-performance fair? |
| --- | --- | --- | --- | --- | --- |
| `rt_dbscan` | Mixed explicit RT-DBSCAN route: prepared fixed-radius/count-threshold in 3D plus grouped stream component labels; CuPy/Numba continuation variants. | Same family: grouped stream / component-union continuation work, V3 runtime surface around the existing route. | Generic V4 fixed-radius count-threshold plus graph/component-union operator route. | **Yes.** Same app semantics and RT-core family can be compared across V2.14/V3/V4. | **Partly, but modest.** Current evidence is about `1.086x` vs V2.14 and `1.083x` vs V3; below a major-performance bar. |
| `raydb_style` | Primitive-first OptiX grouped count/sum/min/max/avg reductions; serious route uses prepared grouped reduction. | Same prepared grouped-reduction family, with V3 route evolution. | V4 grouped-i64/device-output grouped reduction route. | **Yes.** Full app route is same RT-core grouped-reduction family. | **Yes but small.** Latest repaired row is about `1.103x` vs V2.14 and `1.105x` vs V3; useful repair, not a major headline. |
| `triangle_counting` | Generic RT graph / ray-triangle any-hit composition; serious route used OptiX weighted any-hit sum with CuPy. | Segmented/prepared replay and weighted any-hit route family. | V4 weighted any-hit / grouped route through generic ray-triangle surfaces. | **Yes.** Same benchmark app semantics and RT-core route family. | **Yes, with attribution caution.** V4 is about `6.381x` vs V2.14 and `1.043x` vs V3. The V4/V3 row is the cleaner incremental signal. |
| `librts_spatial_index` | Prepared OptiX AABB spatial-index query primitive. | Same prepared AABB query family. | V4 AABB all-ops/count prepared runner. | **Yes.** This is a clean same-primitive app comparison. | **No major win.** V4 is about `1.003x` vs V2.14 and `1.004x` vs V3; this is compatibility/parity. |
| `hausdorff_xhd` | Route audit records OptiX active-frontier/nearest-witness style work, but the old serious timed V2.14 row used Embree. A strict V2.14 RT-core CLI route exists for threshold decision, not the same exact nearest-witness metric. | Exact `optix_device_max_nearest` plus CuPy global max continuation. | V4 point-group nearest-witness plus adaptive CuPy global argmax continuation. | **V3/V4 yes; V2.14 not yet.** V4 must either expose the inherited V2.14 route as compatibility or establish a same-semantics V2.14 exact RT-core denominator. | **V4/V3 yes: `2.546x`. V4/V2.14 no.** The `201581x` Embree-denominator row is invalid as a V2.14 RT-core claim. |
| `robot_collision` | Prepared OptiX any-hit collision flags/count, including device-buffer modes. | Same family of prepared any-hit/flag stream work. | V4 must expose inherited prepared any-hit collision route as compatibility; current generic any-hit flag subroute exists. | **Should be yes after route binding.** It is wrong to say V4 cannot support it; V4 should inherit/support the V2.14 route. | **Not yet.** Existing evidence repairs a native boundary but does not prove a full-app same-primitive V4 speed win over V2.14. |
| `contact_manifold` | Prepared bounded OptiX collect-k / contact-witness primitive. | Same collect/witness route family and partner plumbing. | V4 must expose inherited bounded collect-k/contact route as compatibility; no fresh generic bounded-witness route is proven. | **Should be yes after route binding.** V4 should carry the V2.14 route rather than mark the app unsupported. | **No.** A new V4 performance claim needs a fresh generic bounded-witness route or a measured same-primitive improvement. |
| `rtnn` | Prepared OptiX fixed-radius ranked-summary aggregate. | Same ranked-summary/top-k/nearest aggregate family. | V4 ranked-summary candidate runner. | **Yes.** Serious same-family rows exist. | **No.** Current serious rows are parity/slower: about `0.999x` and `0.994x` vs V2.14 at the recorded scales. |
| `spatial_rayjoin` | Mixed explicit RT-core relation/topology route: point/closed-shape batch count, segment-pair exact count, shape-pair active count; partner continuation as needed. | V3 topology/runner experiments around the same route family. | V4 must expose inherited relation/topology route as compatibility; current V4-new relation-topology route is not complete. | **Should be yes after compatibility binding.** It is wrong to erase the inherited route from V4. | **No.** The measured shape-pair subprobe is not a full app route and is slower (`0.963x` vs V2.14 hot, `0.977x` vs V3 hot). |
| `barnes_hut` | OptiX aggregate-frontier membership plus explicit force/vector partner continuation; V2.14 route had host-frontier/CPU continuation bottleneck. | Device-column/partner continuation route family. | V4 aggregate weighted workflow runner plus explicit partner continuation. | **Yes.** Focused full app workflow rows exist for V2.14/V3/V4. | **Yes vs V2.14, no vs V3.** V4 is about `282.468x` vs V2.14 from host-frontier removal, but about `1.003x` vs V3. Not an RT-core force-law headline. |

## What This Means For V4

V4 user status should be reported as:

```text
10/10 benchmark apps should be supported by V4 either through inherited RT-core
compatibility routes or V4 generic routes.
```

Performance status should be separate:

```text
Only rows with same-semantics RT-core evidence can claim V4 speedup. Inherited
routes count as support, not as new performance wins.
```

## Immediate Engineering Consequences

1. Stop describing Spatial/Contact as simply "no V4 route".
   - Correct: inherited compatibility route must be carried into V4.
   - Also correct: no new V4 generic performance route is proven yet.

2. Split public tables into:
   - app support/compatibility table;
   - performance delta table.

3. Build the next runner around this classification:
   - inherited compatibility route parity for all 10 apps;
   - V4-new performance rows only where evidence exists.

4. Keep the Hausdorff V2.14 row blocked until same-semantics RT-core evidence
   exists.

## Non-Authorization

This reframe does not authorize a final V4 tag, broad speedup claim, all-app
speedup claim, Hausdorff V4/V2.14 claim, arbitrary callback claim, or
app-specific native kernel claim.

## Goal-Level Decision Audit

1. Was I foolish?

Yes.

2. What action made the decision foolish?

I treated "not a new V4 speed win" as if it meant "not a V4 route". That wrongly
excluded inherited V2.14/V3 capabilities from the current V4 user surface.

3. Was there another path?

Yes. Separate compatibility/support from new-performance attribution.

4. Can I now try a different path that actually solves the problem?

Yes. Make V4 a compatibility superset first, then report V4-new speedups only
where same-semantics RT-core evidence supports them.
