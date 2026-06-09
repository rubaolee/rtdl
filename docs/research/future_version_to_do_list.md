# Future Version To-Do List

This file catches design ideas that should not interrupt the current release or internal-preview lane.

## Prepared-Session Residency And Amortization

- Goal3872 measured four scene-heavy prepared rows on an A5000 with `repeat=50`:
  Hausdorff/X-HD, LibRTS spatial index, RTNN, and triangle counting. Hot
  prepared queries are tiny relative to one-time prepare/setup work, especially
  RTNN (`~12757x` prepare/query ratio) and triangle counting (`~2606x`).
- Future user-facing work should make prepared-session residency clearer:
  prepare once, issue many queries, and report hot query timing separately from
  cold scene construction/import/JIT. This is a language/runtime ergonomics
  issue as much as a raw kernel issue.
- If persistent prepared-session caches are added, they must be explicit:
  stable cache keys, visible lifetime/invalidation policy, backend/partner
  ownership, memory-pressure behavior, and no hidden automatic partner/backend
  selection. A cache hit may be a resident-session optimization, but it is not a
  true-zero-copy or public speedup claim by itself.
- Guardrail phrase for future audits: no hidden automatic partner/backend selection.
- Guardrail phrase for future audits: not a true-zero-copy or public speedup claim.
- Keep the primitive boundary generic. Prepared session concepts are things
  like fixed-radius threshold, AABB index query, ranked neighbor summary, and
  ray/triangle weighted sum. App-specific interpretation remains in Python
  examples or benchmark adapters.

## Legacy Versioned Helper Names

- Audit and, where safe, alias or migrate compatibility helper names that still carry historical version labels in example Python code, such as selected `v2_5` Triton preview helpers and `v2_6` Numba compact-mask / neutral-handoff helpers.
- Rationale: Goal3519 cleaned the active learner Markdown surface to v2.8, while Goal3520 confirmed that several Python source helpers retain older labels as compatibility/protocol names. They should not block the v2.8 internal closeout, but future user-facing APIs should prefer current generic names or explicit `legacy_` aliases.
- Boundary: do not rename public or semi-public helper functions casually. Add aliases and migration tests first, preserve existing scripts, and keep historical protocol identifiers stable where artifacts or tests depend on them.
- Goal3800 started this migration for the two active benchmark compact-mask examples: RayJoin and triangle counting now expose current `primitive_first_plan` and `segmented_compact_mask_numba_plan` aliases while preserving the legacy `v2_5_plan` and `v2_6_numba_compact_mask_plan` routes as compatibility shims. Continue this pattern only where the old versioned name is app-facing; keep historical protocol constants stable.
- Goal3802 applied the same pattern to RayDB's app-facing helper layer: current aliases now exist for the primitive-first plan, Numba grouped-reduction continuation, and grouped-reduction typed-stream continuation. Internal protocol constants, artifact keys, and implementation helpers still keep their historical labels.
- Goal3804 added current aliases for the Barnes-Hut grouped-vector typed-stream and RTNN ranked-summary typed-stream benchmark helpers. The legacy v2.8 descriptor and runner names remain available for historical reports and tests.
- Goal3808 cleaned the two remaining low-risk app-facing candidates from Goal3806: Contact Manifold now exposes `describe_bounded_witness_session`, and LibRTS now exposes `primitive_first_plan_payload` plus `--mode primitive_first_plan`. The RayJoin topology-reference helper remains intentionally versioned because it marks a bounded future/reference lane, not a promoted public route.
- Goal3810 refreshed the inventory after Goal3808. Active examples still contain 32 versioned definitions, but zero remaining low-risk app-facing alias candidates: the survivors are compatibility shims, RayDB internals/protocol descriptors, an RT-Graph protocol descriptor, and the intentionally versioned RayJoin topology-reference lane.

## Generic Closed-Shape Boundary Selection

- Add a generic prepared point-to-closed-shape boundary-selection primitive inspired by the RayJoin PIP benchmark gap.
- Candidate generic concept: `point_closed_shape_best_boundary_crossing_2d` or `point_closed_shape_first_crossing_2d`.
- Rationale: RayJoin's fast PIP path traces one upward ray per point and keeps the best crossing boundary event/edge on device. RTDL's current generic point/closed-shape membership count can now use device-filtered scalar count and `z_point` traversal, but it still trails RayJoin on the same slice because it is a membership-count contract over polygon AABBs rather than an edge-range best-crossing contract.
- Engine boundary: this must stay generic. The native engine should expose prepared edge/range traversal and return typed boundary-event columns such as query id, shape id, boundary id, crossing parameter, and tie-break status. RayJoin-specific map ids, simulation-of-simplicity policy, polygon assignment interpretation, and output-chain logic stay in the benchmark app or partner layer.
- Likely prerequisites: prepared edge AABB/range acceleration, deterministic tie-break policy, typed boundary-event columns, optional per-query best-event reduction, and same-contract validation against the existing exact inclusive membership path.
- Boundary: do not merge RayJoin-specific `closest_eid` semantics into the public engine ABI. This belongs in a future v2.8-or-later / v3.0 primitive design, not in the current v2.8 route-tuning evidence.
- v2.8 closed-shape exact stream: Goal3422 initially framed the public CDB miss as a topology-aware closed-boundary refinement contract gap. Goal3424 refined that diagnosis: the immediate mismatch came from duplicate public point/shape ids and a partner helper that collapsed public ids into one geometry instance. Future exact-refinement streams must carry both public ids and input/prepared instance ordinals. Topology-aware closed-boundary contracts remain future work for datasets where instance-aware simple-ring semantics still fail the chosen oracle.

## RayJoin PIP Scalar-Count Lessons

- Goal3300 proved that materializing generic boundary-event columns plus grouped count is the wrong performance route for PIP membership/count on the 512-feature RayJoin slice: the grouped count is cheap, but boundary-event column production emits thousands of rows and is much slower than scalar count.
- Goal3303 ruled out two easy scalar-count knobs: prepared closed-shape edge layout was slower on the A5000 slice, and `crossing_only` boundary mode failed exact inclusive validation (`129 != 1430`).
- Goal3306 showed that resident prepared point-probe columns help repeated-query timing modestly: point upload leaves the timed lane and PIP prepared-query median improved from about 0.343 ms to 0.317 ms on the same A5000 commit. The native count pass stayed near 0.261 ms, so this is not enough to close the RayJoin gap and is not a one-shot win if point-column preparation is charged to a single query.
- Goal3308 moved the prepared-points count buffer and launch-parameter buffer into the reusable point-probe handle. This improved the PIP prepared-query median again to about 0.303 ms, but the native count pass still stayed near 0.262 ms.
- Goal3310 added a generic prepared-points batch count surface. It improved repeated-query per-request throughput to about 0.242 ms at 32 queued requests on the A5000 RayJoin PIP slice, but it exposed the native scalar-count traversal floor instead of closing the one-shot RayJoin gap.
- Goal3312 tested CUDA graph replay for the prepared-points batch count path. The graph replay returned zeros on a live A5000 smoke while trusted single/batch counts returned the exact count, so the Python wrapper now fails closed on replay mismatch. Do not use this graph path as performance evidence until the native replay mismatch is fixed.
- Goal3314 added an opt-in stream pool for the generic prepared-points batch scalar-count path. On the A5000 RayJoin PIP slice, 8 streams at 32 requests improved repeated-query per-request median time from about 0.236 ms to about 0.0365 ms while preserving exact count 1430. This is repeated-query throughput evidence only, not one-shot RayJoin latency evidence.
- Goal3316 made the `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT=auto` policy reachable from the probe and recorded effective stream counts in the artifact. On the same A5000 slice, auto selected 8 streams at 32 requests and 16 streams at 64 requests, reaching about 0.0359 ms/request and 0.0343 ms/request respectively. The next runtime ergonomics step is a persistent prepared batch executor or stream pool so streams are not created/destroyed on every batch call.
- Goal3318 added that persistent prepared batch executor for the generic prepared-point scalar-count path. It modestly improved the auto path to about 0.0349 ms/request at 32 requests and 0.0332 ms/request at 64 requests by reusing streams, count buffers, and launch-parameter buffers. The remaining cost is now mostly traversal/count work, so the next large RayJoin-relevant leap likely needs a more compact generic closed-shape predicate-count primitive or prepared boundary/range acceleration.
- Current best direction is still the generic scalar-count lane, now with `device_filtered_prepared_points_validated + inclusive + z_point + scalar count pipeline` when repeated query points can be prepared. Further improvement likely requires a more compact fused native scalar-count path or another generic closed-shape predicate-count primitive that reduces per-request traversal overhead.
- Goal3320 broadened validation beyond the original county start0 slice. The prepared-point scalar-count executor remained exact and fast on `br_soil_start256_count512.cdb`, but mismatched the exact CDB oracle on full `br_county.cdb` and `br_county_start256_count512.cdb`. Treat this as a topology/degeneracy contract boundary: the current primitive is valid for checked simple-chain domains, while broad CDB support likely needs a generic face/topology-aware closed-shape membership primitive with ring/chain identity, deterministic boundary ownership, and duplicate policy.
- Goal3321 added an app-level `preflight_rayjoin_pip_fast_count_domain(...)` helper so benchmark code can record whether a selected generic fast PIP count route matches exact prepared count before treating that input domain as safe. Keep this as Python policy; do not move CDB/RayJoin topology decisions into the native engine.
- Goal3322 localized the county start256 mismatch to 7 overcounted point IDs (+12 total) with no undercounts, while soil start256 remained exact. Several mismatching county rows have duplicate coordinates. This strengthens the hypothesis that the next reusable primitive needs explicit topology/degeneracy/ownership semantics, not another host batching tweak.
- Goals3327-3337 refined that topology direction: the fast device-column route emits specific extra shape ids; those extras are face-adjacent; a generic owner-face filter can recover the known exact rows if the caller supplies owner-face ids; simple point-chain left/right owner policies are insufficient; local incident topology contains the needed owner face for all 7 known mismatches but ties with other faces. Future work should define a deterministic, generic vertex/face ownership derivation contract and then lower explicit owner-face filtering to device/native code. Do not let the native engine infer RayJoin/CDB ownership semantics implicitly.
- Goals3658, 3660, and 3663 changed the current best validated route for PIP scalar count on checked county slices: the tuned generic device predicate (`RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS=1e-9`) makes the one-shot/sequential prepared-points route exact and faster than the prior project-owned CuPy dense baseline, and the persistent batch executor gives strong repeated-request throughput on both 512 and 4096 public-CDB slices. This is still a validated-domain throughput contract, not full RayJoin reproduction or one-shot RTDL-beats-RayJoin evidence.
- Goal3665 wired the validated-domain preflight into the repeated-count runner and scoped the tuned device-predicate epsilon into that preflight. The `count16545` full-county probe still fails exactness (`47264 != 47262`) and now fails before RayJoin timing starts. Future topology-aware work should treat this as the live blocker for broad CDB PIP, not as a performance tuning problem.
- Goal3671 superseded the v2.9 closeout framing and added a generic side-aware owner-face filter over caller-supplied `(owner_face_id, owner_side)` columns. On the A5000 full-county CDB probe, the side-aware CuPy continuation repaired the tuned candidate row stream from `47264` rows to exact multiset parity at `47262` rows by dropping `(893, 16312)` and `(894, 16312)`. This is constructive topology-continuation evidence, but the app/data-layer derivation of owner-side columns is still the next blocker before any automatic/default RayJoin route.
- Goal3673 made that repair ordinal-aware and selective. A full-county all-point owner-side probe overfiltered badly (`22639` rows, `24623` missing), proving side ownership is not a universal replacement for membership. The new selective ordinal-aware CuPy continuation passes non-selected rows through and filters only caller-selected ambiguity ordinals; on the A5000 full-county CDB probe it removed the same two extras and matched the exact `47262`-row multiset. The next major direction is a generic ambiguity-set derivation contract (`candidate stream + topology/boundary signals -> selected input ordinals`) that remains caller/data-layer policy or a generic primitive, not hidden RayJoin/CDB logic in the native engine.
- Goal3675 added generic relation-status and boundary-element ordinal columns to the closed-shape candidate stream, plus a Numba count-only boundary-contact continuation. Full-county A5000 evidence showed exact count parity (`47262`) but also localized the performance bottleneck: one-shot exact candidate-column routes spend about `21-24 ms` mostly on stream allocation/free/materialization, while the resident candidate-stream Numba count is about `1.50 ms` and native traversal itself is about `0.44 ms`. Future work should promote reusable native output buffers and/or a generic exact scalar-count primitive that avoids row-stream materialization for count-only workloads. Keep this generic: relation status, boundary element ordinal, invalid-contact count, and reusable stream ownership are engine concepts; RayJoin/CDB ownership policy stays outside the native ABI.
- Goals3677-3681 added a prepared relation-status filtered candidate-column producer, a composed exact Numba scalar-count helper, a resident exact counter, and a sqrt-free boundary-contact Numba test. Final A5000 full-county evidence showed all-candidate count-only at about `0.00046 s`, one-shot corrected exact count at about `0.00281 s`, and resident corrected exact count at about `0.00153 s`, all exact at `47262`. The negative lesson is equally important: boundary-status rows were dense (`47241 / 47264`), so relation-status filtering alone is not a sparse selector on this workload. The next real leap should be a generic native/reusable scalar-correction primitive or reusable candidate-output workspace that avoids producing dense boundary columns for scalar count-only use.
- Goal3684 implemented the first measured native scalar-correction fix for that dense-boundary weakness. The new generic OptiX relation-status corrected scalar-count route keeps float RT traversal, validates boundary contacts against double prepared lookup buffers, downloads only scalar counters, and stays exact (`47262`) on the same full public county dataset. Clean-commit A5000 hot median was about `0.000517 s`, versus about `0.001825 s` for the resident Numba corrected path in the same packet, with no dense boundary-row stream materialized. Next work is external review, default-route/promotion discipline, and reuse of this scalar-correction pattern for other dense-boundary benchmark rows without app-shaped engine vocabulary.
- Goal3686 added a reusable native scalar-count executor for the Goal3684 primitive. Clean-commit A5000 full-county evidence stayed exact (`47262`) and measured the resident native executor at about `0.000474 s`, versus about `0.000511 s` for one-shot native scalar correction and about `0.001814 s` for the resident Numba corrected path in the same packet. This closes the first reusable correction-workspace step for scalar count-only workloads; route promotion still needs external review and claim-boundary discipline.
- Goal3688 wired the resident native scalar-count executor into the current safe RayJoin count composite for the PIP leg while leaving LSI and overlay on their existing exact RTDL/OptiX count paths. Clean A5000 source-scoped evidence at `4096` chains matched the dense all-CuPy same-contract baseline for all three count legs and measured about `205x` composite speedup versus dense all-CuPy (`1.430913 s` to `0.006967 s`). Treat this as an internal candidate-route result pending external review and broader count-scale validation, not a RayJoin paper reproduction or public speedup claim.
- Goal3690 broadened that same candidate route across `512/1024/2048/4096` chains. All rows matched the dense all-CuPy same-contract baseline, with geomean candidate speedup about `95.8x` and minimum speedup about `50.3x`. The PIP leg itself is now consistently faster but only modestly (`1.27x-2.33x`), so future RayJoin work should stop chasing tiny scalar-count tweaks and instead compare against the original RayJoin implementation and focus on the remaining full-route benchmark contract.
- Goal3691 compared RTDL against the original RayJoin checkout on the same bundled Brazil sample files. Cross-map PIP was promising (`0.000471 s` RTDL versus `0.000880 s` RayJoin query time), but RayJoin's PIP output did not print a count oracle. LSI initially became the live blocker: RTDL exact prepared LSI measured `0.011886 s` versus RayJoin `0.000897 s` and reported `20859` intersections versus RayJoin's checked `20860`.
- Goal3693 localized the Goal3691 LSI row-count gap to exactly one RayJoin pair after normalizing RTDL's one-based edge ids: `(230119, 226567)` is missing from RTDL and there are no RTDL extras. The pair is an endpoint-near segment intersection; exact arithmetic gives `t ~= 7.57e-5`, while simulated float32 candidate emission rounds enough to make `t < 0` and drops the candidate. Future LSI/RayJoin work should add a generic robust segment-pair candidate-emission policy, such as ambiguous near-boundary candidate emission or a high-precision/scaled predicate mode, then rerun pair-set parity before timing claims. Keep this app-agnostic: no RayJoin/CDB names in the native ABI.
- Goals3697-3698 applied and validated the first generic repair: widening the OptiX segment-pair conservative candidate slack from `1e-4` to `1e-3` recovered the missing endpoint-near LSI pair. On the A5000 same-source RayJoin probe, RTDL now matches RayJoin's checked `20860` LSI count and the normalized pair set has `0` missing and `0` extras.
- Goals3725, 3729, and 3733 superseded the old LSI performance blocker for the bundled Brazil count contract. The generic grouped-range direct exact-count front door keeps one generic segment record per primitive (`max_size=1`) and evaluates the exact predicate in the custom intersection program; the default policy measured about `3.291x` versus the same-source RayJoin LSI query and the mixed 4096-chain composite moved the bottleneck to overlay active-count. Keep the claim boundary narrow: this is a single-contract A5000 measurement with matching counts, not RayJoin paper reproduction or public RTDL-beats-RayJoin wording.
- Goal3604 turned the constructive boundary-event signal route into a timing packet. It remained exact on 512/1024/2048 public-CDB county slices, but the route was only about `0.028x` geomean versus the dense CuPy scalar-count baseline because it pays candidate-column generation, boundary-event-column generation, selected-point derivation, and selective filtering as separate stages. Future performance work should fuse exact closed-shape membership/count into one generic primitive or compact native continuation instead of materializing a large boundary-event row stream for scalar count-only PIP.
- Goal3606 tested that same boundary-event signal on a 4096-chain public-CDB county slice across tolerances `0`, `1e-6`, `1e-5`, `1e-4`, and `1e-3`; none matched the exact count. Treat the signal as a bounded diagnostic, not a default route. Larger exact PIP support needs a stronger generic topology/ownership/tolerance contract, not just tolerance tuning.
- Keep the public claim boundary narrow: these are route-tuning facts, not RayJoin paper reproduction or broad RT-core speedup claims.

## RayJoin General Simple-Polygon Overlay Area

- Goal3467 proved the public-CDB active relation stream is not a convex-only overlay workload: 4,375 of 4,543 active relation rows require general-overlay handling, only 168 rows are both-convex, 1,033 rows exceed the 64-vertex simple threshold, and the max active pair has 1,132 vertices.
- A convex clipping continuation is still useful as a routed fast path for both-convex rows, but it cannot close the public-CDB exact-overlay gap by itself.
- The needed generic primitive is a simple-polygon overlay-area continuation over resident relation streams and geometry payload columns. It should emit per-row intersection area plus status/ownership policy columns, and optionally grouped area reductions. It must not encode RayJoin, county, map, CDB, or GIS-app names in the engine ABI.
- Likely implementation direction: keep RT cores responsible for candidate/relation production; keep exact overlay as a partner/native continuation over typed geometry payloads. Candidate algorithms include a generic arrangement/sweep continuation, triangulation plus triangle-polygon accumulation, or a robust polygon clipping library integration behind a generic primitive contract. A naive Sutherland-Hodgman clip is valid only for convex clip shapes and must be gated by the Goal3467-style complexity classifier.
- Required acceptance before any public claim: exact oracle policy for non-integer/non-orthogonal polygons, deterministic boundary-witness ownership, hard fail-closed status for unsupported topology, same-contract CPU/reference comparison, large public-CDB pod evidence, and independent review.
- Boundary: this belongs in the v2.8-or-later primitive/runtime lane if implemented as built-in generic continuation; arbitrary user-defined clipping kernels belong to the later v3.0 extension lane.

## Dense Fixed-Radius Grouped Union

- Goal3987 ruled out simple RT-DBSCAN grouped-stream route switches on the
  current `clustered3d` scale profile: blocked query ranges, direct side
  effects, and disabling same-root culling did not beat the current grouped
  stream route.
- Goal3988 showed that the existing RTDL/OptiX grouped stream is still the
  correct primitive-first route for this profile: it is about `20x` faster than
  the Numba-only prepared-grid opponent and about `86x` faster than the
  CuPy-only prepared-grid opponent at `65536` points.
- Goal3989 added atomic telemetry and same-root A/B evidence. Parent atomic
  attempts are only about `1.24` per point, same-root culling is already faster
  than disabling it, and atomics are not the sole bottleneck. The expensive
  work is the combined fixed-radius candidate traversal, repeated root reads for
  same-root culling, and remaining atomic unions.
- Goal3996 used the Goal3992 extended counters to sweep same-root and
  direct-side-effect grouped-union modes at `4096`, `16384`, and `65536`
  clustered3d points. At `65536` points, the current default saw about
  `892.8M` radius-qualified candidates for only `65,535` successful unions.
  Disabling same-root culling was slower, and direct side effects were only
  roughly neutral at the large size. Do not spend more time on these simple
  toggles as the main optimization path.
- Goal3998 rejected a per-ray source-root payload snapshot. It was app-agnostic
  and compile-fixable by increasing the grouped-union payload count, but the
  source root became too stale during concurrent union-find. On the same
  `65536` clustered3d profile, reported candidates jumped from about `1.84M` to
  `543.65M` and the default telemetry path slowed by about `1.079x`. Do not use
  stale per-ray root snapshots as the dense grouped-union solution.
- Goal3999 separated the current RT-DBSCAN benchmark radii from the Goal3996
  stress radius. At `65536` points, the current defaults are `clustered3d`
  radius `0.055`, `road3d` radius `0.030`, and `ngsim_dense` radius `0.012`,
  while the earlier `0.5` row is stress-only. A CPU partition feasibility probe
  found useful but insufficient uniform-grid signal: with radius/4 cells,
  ambiguous near-pair upper bounds still remain about `76.67%` for clustered3d,
  `70.05%` for road3d, and `53.50%` for ngsim_dense. Treat this as evidence for
  a hybrid device-resident partition plus RT boundary traversal primitive, not a
  plain grid rewrite.
- Goal4001 reran extended grouped-union telemetry at those actual radii on an
  RTX 4000 Ada. Same-root culling remains mandatory: disabling it slowed all
  three profiles. At `65536` points, default same-root culling reduced reported
  candidates to `80,719 / 273,911,978` for clustered3d, `167,285 / 85,627,372`
  for road3d, and `75,119 / 12,299,418` for ngsim_dense. Direct side effects
  avoided any-hit reports and were small-positive/neutral (`0.956x`, `0.938x`,
  `1.004x` versus default), but they do not remove traversal/root-read cost.
  The next primitive should reduce candidate/root-read work, not just move
  union side effects from any-hit to intersection.
- Goal4002 checked that direct-side-effect mode at the app column-signature
  level. Signatures matched on clustered3d, road3d, and ngsim_dense at `65536`
  points, but end-to-end ratios were mixed (`0.974x`, `1.001x`, `1.044x`
  direct/default). Do not promote direct side effects as the default grouped
  union route. Keep it as an explicit option and focus the next primitive on
  reducing candidate/root-read work.
- Goal4004 refreshed the older corrected microcell route against the current
  grouped-stream baseline. It matched output signatures but was much slower:
  about `50.19x` slower on clustered3d, `23.60x` slower on road3d, and
  `28.90x` slower on ngsim_dense at `65536` points. Do not promote the old
  partner microcell route as the dense grouped-union solution. The next route
  must be a native/device-resident partition assist or convergence-aware
  primitive that preserves the current grouped-stream strengths.
- Goal4007 added root-read telemetry to the accepted grouped-stream route. At
  actual `65536`-point benchmark radii, the default path performs about two
  readonly root finds per candidate and large parent-link traffic
  (`708.9M`, `304.9M`, and `33.2M` parent-link steps for clustered3d, road3d,
  and ngsim_dense respectively). The next primitive must reduce candidate and
  root-read work together.
- Goal4009 rejected hidden root path halving as a default. The temporary
  candidate reduced raw root-link telemetry and native micro-path time, but it
  failed the clustered3d app-level column signature and had mixed app timing.
  Root convergence changes must be explicit and deterministic, not hidden
  mutation inside readonly root checks.
- Goal4011 showed the partition-convergence direction is stronger when tested
  beyond the original radius/4 cell factor. Radius/8 partitions cut ambiguous
  pair upper bounds versus radius/4 by about `60.27%` on clustered3d, `60.90%`
  on road3d, and `91.93%` on ngsim_dense. However, radius/8 creates `16,675`,
  `18,031`, and `60,070` occupied cells, so the next primitive must use a
  compressed occupied-cell structure plus bounded near-offset enumeration, not
  a dense cell-pair matrix.
- Goal4012 hardened that lesson into the fixed-radius graph component
  front-door contract. The `partition_convergence_hybrid` candidate now
  explicitly requires compressed occupied partition keys, bounded near-partition
  enumeration, radius/8 evidence, root-read telemetry reduction, and deterministic
  convergence/staleness metadata. It also explicitly rejects dense all-cell-pair
  matrices and hidden root path halving inside readonly root checks.
- The next generic runtime primitive should be a dense fixed-radius
  grouped-union continuation, not another app-specific RT-DBSCAN trick. Candidate
  designs include component-aware root-cache snapshots with explicit staleness
  policy, multi-pass contraction, candidate compaction before union, or
  cell/partition-assisted grouped union when a prepared search structure exposes
  safe partitions.
- Engine boundary: keep the native vocabulary generic. The primitive may talk
  about fixed-radius pairs, groups, component roots, union events, partitions,
  and convergence/status counters. It must not encode DBSCAN, clustering,
  epsilon/min-points policy, or application-specific labels in native ABI names.
- Required acceptance before promotion: same-contract parity against the
  existing grouped-stream route, deterministic component-root policy, explicit
  staleness/convergence metadata when root snapshots are used, dense and sparse
  pod profiles, and external review. Treat performance results as profile-bound
  until broader datasets are measured.
- Goal4149/4150 found a strong direct-status single-pass replay win for the
  generic fixed-radius component-signature contract: same signatures versus the
  stable direct-status loop across tested `65k/131k/262k/524k/1M` factor-0.25
  packets, with roughly `~2x` replay improvement. Goal4153 then proved this
  cannot be compared directly with the conservative RT-DBSCAN current route:
  all `15/15` current-route versus single-pass rows had mismatched signatures.
  The next same-contract primitive is therefore **predicate-aware direct-status
  grouped union**: accept caller-supplied vertex predicate/core flags, union only
  predicate-compatible fixed-radius pairs, and assign non-predicate border
  points through a deterministic neighbor-root policy. Keep the contract generic
  (`vertex predicate`, `candidate pair`, `component root`, `border assignment`);
  do not encode DBSCAN/min-points semantics in the engine ABI.
