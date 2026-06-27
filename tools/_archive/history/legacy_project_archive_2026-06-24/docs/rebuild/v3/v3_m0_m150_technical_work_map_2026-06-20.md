# V3 M0-M150 Technical Work Map

Status: V3-only reconstruction, 2026-06-20.

This file answers:

```text
Before the C ABI / embedding branch, what did V3 actually do?
```

Hard boundary:

```text
M150 is the boundary marker where V3 work starts drifting into embeddability.
M150-M214 are OUT of V3 current scope.
They must not be used to define V3, teach V3, or justify V3 performance.
```

## Short Answer

M0-M149 were not trivial cleanup. They were a serious V3 technical campaign:

- define an app-agnostic execution graph / prepared graph shape;
- prove same-stream and no-hidden-copy measurement windows;
- build device-side grouped and partner-continuation bridges;
- repair and rerank benchmark routes across ten apps;
- build fused CPU/Numba and Numba CUDA continuations where generic RTDL
  primitives were not enough;
- test prepared graph chunking and graph-capture boundaries;
- close current benchmark app routes under strict non-claim boundaries.

The failure was not lack of work. The failure was that the campaign ended as
`current route closed / internal evidence`, not as a polished, production-grade
V3 performance language surface.

## Phase Map

| Phase | Goals | What happened | Useful for V3 now? | Boundary |
| --- | --- | --- | --- | --- |
| Pre-M1 strategy | Goal4377, Goal4384, Goal4392 | V3 was defined as primitive planner, execution graph, device-resident streams, fused generic continuations, backend-specific lowering, phase accounting, explicit partner policy. | Yes, as design intent. | Design only; not user capability. |
| M1-M7 foundation | M1-M7 | Execution graph IR, skeleton, instrumentation, component-union/topology/frontier-vector pilots, harness prep. | Yes, as architecture seed. | Needs promotion into real user route before claim. |
| M8-M17 stream/copy evidence | M8-M17 | Aggregate-frontier lowering, grouped stream partner, same-stream evidence, no-hidden-copy evidence, hit-stream transfer audit, prepared hit-stream, partner device-ray evidence. | Yes, for reduced-copy / no-hidden-copy V3 work. | Not true zero-copy; not public wording. |
| M18-M27 device continuation bridge | M18-M27 | Device-side grouped contract, ranked summary bridge, max-nearest reduction, Hausdorff, DBSCAN, outlier density, RTNN app bridge, facility and triangle partner dual rows. | Yes, for partner-continuation design and benchmark rescue. | Not a generalized runtime. |
| M28-M34 prepared route refresh | M28-M34 | RayDB prepared grouped refresh, contact broadphase refresh, LibRTS all-ops refresh, robot any-hit refresh, Barnes-Hut vector partner, RayJoin active-count, Barnes-Hut frontier lowering. | Yes, several rows became current-route evidence. | Route-specific, not broad speedup. |
| M35-M42 aggregate frontier columns | M35-M42 | Aggregate-frontier device-column contract, OptiX device columns, CuPy/Numba vector-sum pipelines, prepared aggregate-frontier app modes. | Partly. Good for understanding device-column route costs. | For Barnes-Hut this is not RT-core speedup evidence. |
| M43-M54 Barnes-Hut fusion pivot | M43-M54 | Host baselines, CPU/Numba fused frontier, Numba CUDA fused subtree, reusable fused partner API, app front-door mode. | Yes, this is one of the most important V3 technical lines. | Partner/fused route, not RTDL RT-core traversal. |
| M55-M64 route correction / app bridges | M55-M64 | RayJoin graph replay fail-closed, RTDBSCAN route decision, Triangle device geometry and no-host-column work, Barnes-Hut rerank, RTNN clustered/shell bridges. | Yes, especially fail-closed graph boundary and app bridge evidence. | Several routes are internal evidence only. |
| M65-M86 Triangle campaign | M65-M86 | Triangle segmented 2a1, paper dataset probes, planner tuning, unique weighted segments, prepared segment replay, phase split, CuPy/Numba comparison, query-phase telemetry, sort/RLE candidate, negative compact/fused candidates. | Yes, very useful for deciding whether Triangle can be a V3 performance row. | Many candidates were rejected or non-public. |
| M87-M100 rerank and DBSCAN column campaign | M87-M100 | Barnes-Hut large-scale rerank; RTDBSCAN compact signature and direct-status matrices; point-column app mode; coordinate helper; Triangle unique prototypes; 2M point-column reuse/profiles. | Yes, this is core evidence for route choice. | Point-column reuse is not general zero-copy. |
| M101-M113 performance/paper/graph bridge | M101-M113 | Barnes-Hut RT-native feasibility, RTNN paper dataset targets/KITTI recipe/same-input gates, RTNN chunked partner runtime, prepared graph chunk executor. | Yes, but selectively. M113 is a reusable shape, not a finished universal graph compiler. | Paper claims and author-superiority remain blocked. |
| M114-M128 clean-target audits | M114-M128 | RTDBSCAN, Triangle, Barnes-Hut, primitive apps, RayJoin, all-app clean-target closeout, prepared graph adoption gate, route adequacy consistency, benchmark implementation queue. | Yes, this tells us which routes were considered closed and why. | "Queue empty" only meant narrowed current-route scope. |
| M129-M149 closure and guardrails | M129-M149 | Barnes-Hut RT-native wrapper/fail-closed/semantic gates, RTDBSCAN prepared graph capture, Triangle device payload merge and graph-capture audit, V3 claim closeout, app completion gate, consensus, source-tree/test-matrix/legacy runner work. | Yes, mainly for boundaries and current-route closure. | Still not public performance; graph capture remains partly blocked. |
| M150 | Goal4549 | Embeddability strategy intake. | No for V3 current scope. | This is the hard OUT boundary for V3. |

## What To Keep For V3

These are the parts worth keeping or reviving for V3:

- M1-M7 execution graph concepts, but only when tied to benchmark routes;
- M8-M17 same-stream / no-hidden-copy measurement discipline;
- M18-M27 device continuation contracts and partner evidence;
- M28-M34 prepared route refresh rows;
- M43-M54 Barnes-Hut fused CPU/Numba and Numba CUDA route work;
- M65-M86 Triangle performance campaign, especially accepted/rejected candidate
  lessons;
- M87-M100 RTDBSCAN direct-status / point-column evidence;
- M101-M113 prepared graph chunk executor and RTNN chunked partner runtime;
- M114-M149 clean-target audits, only as route-classification evidence.

## What Is Out

The following must be excluded from V3 current scope:

- M150-M214 C ABI / embedding / SDK / ctypes / pkg-config / CMake / external
  runtime / CUDA metadata / DLPack-like bridge work;
- true zero-copy as a product claim;
- external CUDA stream adoption as a product claim;
- language binding packages;
- stable installed SDK;
- C ABI OptiX/Embree execution.

This material may exist in history, but it is not V3.

## What M0-M149 Mean For A Rebuilt V3

M0-M149 say V3 should not be reduced to docs cleanup. They show the right V3
technical center:

```text
execution graph discipline
prepared/reused routes
same-stream and no-hidden-copy evidence
device-resident continuation where measured
fused continuations where route-specific evidence wins
serious benchmark-app closure
```

The rebuilt V3 decision should be:

```text
Revive M0-M149 items only when they can be converted into current, passing,
serious benchmark evidence. Keep M150-M214 out.
```

## Goal-Level Decision Audit

1. Did I make a foolish decision?

   Yes, earlier I let M150-M214 sit near the V3 story as if they were adjacent
   V3 evidence. That blurred the scope.

2. What actions made that decision foolish?

   I grouped C ABI / embedding / zero-copy preparation with real V3 execution
   graph and benchmark-route work instead of declaring a hard OUT boundary at
   M150.

3. Was there another path that avoided being stuck on the wrong idea?

   Yes. Split the map into M0-M149 V3 technical work and M150-M214 out-of-scope
   embeddability work.

4. Can we now try a different path that solves the real problem?

   Yes. Rebuild V3 from M0-M149 evidence, retest the strongest routes on the
   pod, and prevent M150-M214 from entering V3 user docs or release criteria.
