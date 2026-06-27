# V3 Historical Goal Completion Audit

Status: V3-only evidence audit, 2026-06-20.

This audit answers one question:

```text
Which early V3 goals were actually worked on, and how far did they get?
```

It does not authorize release wording or public performance claims. It separates
"we did work" from "users can rely on this as a V3 capability."

## Completion Scale

| Level | Meaning |
| --- | --- |
| `D0 design/preflight` | Design, review, or gate only. No runtime user capability. |
| `D1 tested skeleton` | Code/tests exist, but no real benchmark-route delivery. |
| `D2 internal evidence/prototype` | Measured scripts/artifacts exist; claim is still internal or row-scoped. |
| `D3 current benchmark route closed` | Used to close one or more current benchmark app routes under narrow claim boundaries. |
| `D4 user/public claim authorized` | Safe for user docs/public claims after evidence, review, and wording gates. |

Most historical V3 work reached `D2` or `D3`. Very little reached `D4`.

## Executive Finding

The early V3 goals were not imaginary. A large amount of work exists from
Goal4377 through Goal4614:

- design gates for an execution graph / prepared graph architecture;
- scripts and reports for same-stream, no-hidden-copy, prepared hit-stream, and
  partner device-ray evidence;
- benchmark-app route repair and reranking across ten apps;
- prepared graph chunk executor and graph-capture experiments;
- fused CPU/Numba and Numba CUDA partner routes;
- C ABI / embedding / zero-copy preparation work later fenced out of V3 scope.
  This is now treated as a hard OUT boundary for V3, not as weakly related V3
  evidence.

The problem is completion level and claim boundary:

```text
The history proves serious implementation and evidence work.
It does not prove that V3 shipped a general graph compiler, true zero-copy
runtime, automatic optimizer, or broad V3-over-V2 performance win.
```

## Major Goal Families

| Goal family | Main evidence | Completion | What was actually achieved | What was not achieved |
| --- | --- | --- | --- | --- |
| V3 strategy and preflight | Goal4377, Goal4384, Goal4392, Goal4393, Goal4414 | `D0-D1` | V3 was framed as an app-agnostic execution graph / prepared graph / device-resident / fused-continuation performance line. M1 IR design and review gates were created. | This did not by itself ship user runtime behavior or performance claims. |
| Execution graph IR and skeleton | Goal4393-M1, Goal4394-M2, Goal4395-M3, Goal4396-M7 | `D1` | IR schema, validators/skeleton, instrumentation, and pilot preparation existed. | No production-grade graph compiler became the V3 user front door. |
| Same-stream and no-hidden-copy evidence | Goal4405-M10 through Goal4413-M17; scripts `v3_0_m10` through `v3_0_m17` | `D2` | Same-stream, transfer-counter/no-hidden-copy windows, hit-stream audits, prepared hit-stream evidence, and partner device-ray evidence were measured. | Not an end-to-end true-zero-copy product contract; not public zero-copy wording. |
| Device-side grouped / continuation bridge | Goal4415-M18 through Goal4424-M27 | `D2` | Device-side grouped contract, ranked-summary bridge, max-nearest device reduction, Hausdorff/DBSCAN/outlier/RTNN bridge experiments, facility and triangle partner dual rows. | Not a generalized device-resident stream runtime exposed as a polished V3 feature. |
| Prepared primitive route refresh | Goal4425-M28 through Goal4431-M34 | `D2-D3` | RayDB prepared grouped refresh, contact broadphase, LibRTS prepared operations, robot prepared any-hit, RayJoin active-count, Barnes-Hut frontier lowering refresh. | Route-specific evidence, not broad whole-app speedup or paper reproduction. |
| Aggregate frontier / device columns | Goal4432-M35 through Goal4439-M42 | `D2` | Aggregate-frontier device-column contracts and OptiX/CuPy/Numba pipelines were built and measured. | For Barnes-Hut, this remained OptiX-library CUDA device-column evidence, not RT-core Barnes-Hut speedup. |
| Barnes-Hut fused routes | Goal4440-M43 through Goal4450-M54, Goal4458-M62, Goal4483-M87, Goal4512, Goal4517-M121, Goal4518-M122, Goal4523-M127 through Goal4527-M131, Goal4541-M142 | `D2-D3` | CPU/Numba and Numba CUDA fused routes were built; route reranks identified scale-dependent winners; current Barnes-Hut was closed as a mixed-explicit route. | RT-native hierarchical traversal was not solved; naive all-node OptiX traversal was rejected; no public N-body/RT-core speedup claim. |
| RTNN graph/partner route | Goal4443-M47, Goal4459-M63, Goal4460-M64, Goal4498-M102 through Goal4509-M113, Goal4516-M120 | `D2-D3` | RTNN large/clustered/shell app bridge evidence, KITTI bounded recipe, point-file front door, chunked partner runtime, and reusable prepared graph chunk executor contract. | Not exact paper reproduction, not author-code superiority, not broad ANN-index acceleration. |
| Triangle counting | Goal4453-M57 through Goal4482-M86, Goal4492-M96 through Goal4494-M98, Goal4511-M115, Goal4521-M125, Goal4530-M133, Goal4531-M134, Goal4539-M140, Goal4540-M141 | `D2-D3` | Major route tuning: device geometry, summary fast paths, no-host-column route, segmented/paper-dataset probes, prepared segment replay, sort/RLE candidate, device key-payload merge, non-graph stream continuation closure. | CUDA graph capture for weighted replay remained blocked; no public RT-core or paper-speedup claim. |
| RT-DBSCAN | Goal4445-M49, Goal4452-M56, Goal4484-M88 through Goal4496-M100, Goal4510-M114, Goal4519-M123, Goal4520-M124, Goal4528-M132 | `D2-D3` | Compact component-signature route, direct-status matrix, point-column app mode, 2M point-column reuse, chunk-handle smoke, and prepared graph capture/replay experiment. | Full rows remained slower; 2M reuse is caller-owned-column only; prepared graph capture was future-shape evidence, not current route. |
| Primitive/no-partner apps | Goal4513-M117 plus app-specific prior rows | `D3` | Hausdorff/X-HD, Robot Collision, Contact Manifold, RayDB-style, and LibRTS had primitive-first or no-partner current route closure. | Still row-scoped; not broad app speedup or complete replacement of specialized systems. |
| Ten-app current route closure | Goal4515-M119, Goal4522-M126, Goal4524-M128, Goal4533-M135 through Goal4538-M139, Goal4543-M144, Goal4614-M215 | `D3` | All ten benchmark-app current routes were accounted for; queues became empty under the narrowed current-route scope; `v3_current` became canonical. | This explicitly did not authorize public release/performance claims, broad RT-core wording, paper reproduction, automatic partner selection, stable SDK, device-buffer query, external-stream, or public true-zero-copy claims. |
| OUT OF V3: C ABI / embedding / zero-copy preparation | Goal4549-M150 through Goal4613-M214; history under `docs/history/v4_preparatory_embedding/` | OUT | Header, stub library, host AABB2 proof, C client smoke, ctypes examples, symbol/version/stability docs, pkg-config/CMake/prefix/archive staging, error/concurrency smoke, CUDA metadata descriptors, DLPack-like metadata bridge. | This is not V3. It must not define V3, teach V3, justify V3 performance, or enter V3 release criteria. |
| 2026-06-20 rebuild evidence | `docs/rebuild/v3/*` and pod artifacts | `D2-D3` | Current V3 runability repaired: same RTX pod shows V3 passes more rows than V2.14 and all current serious app rows can run. | Same-row V3-vs-V2.14 raw timing is mostly parity: 46 comparisons, 10 faster, 32 within +/-5%, 4 slower, geomean 1.012x. Not broad V3 speedup. |

## App-Level Historical Outcome

| App | Historical V3 result | Completion | Claim boundary |
| --- | --- | --- | --- |
| Hausdorff / X-HD | Primitive-first exact nearest-witness/grouped-max route; threshold rows have OptiX evidence. | `D3` | No broad speedup or automatic partner claim. |
| Spatial RayJoin | Mixed explicit route: Numba for bounded PIP one-shot; RTDL/OptiX prepared batch for repeated PIP; scalar/active-count primitives for LSI/overlay. | `D3` | Full paper / Section 5.7 8/8 remains future claim expansion; unsafe graph replay fail-closed. |
| RT-DBSCAN | Direct-status compact component-signature route; self-query optimization; point-column reuse experiments. | `D3` | Full rows slower; 2M reuse is not general zero-copy; no automatic partner claim. |
| Robot Collision | Prepared grouped-segment any-hit route with NumPy lowering. | `D3` | No robotics planner or continuous collision claim. |
| Contact Manifold | OptiX native bounded witness collect. | `D3` | No manifold-native ABI or whole-app manifold solver claim. |
| RayDB-style | Primitive-first fused grouped reductions for count/sum-style queries. | `D3` | Arbitrary SQL/database acceleration not claimed. |
| Barnes-Hut | Mixed explicit route: CPU/Numba or Numba CUDA fused depending on scale; prepared RTDL/OptiX+Numba as device-column evidence. | `D3` | No RT-core Barnes-Hut speedup; RT-native hierarchical traversal remains unsolved. |
| LibRTS spatial index | Prepared AABB index query slice. | `D3` | Not full mutable LibRTS. |
| RTNN | Aggregate route, point-file front door, prepared graph partner bridge, chunked partner runtime. | `D3` | No exact paper reproduction or author-superiority claim. |
| Triangle counting | Large route exploration and prepared segment replay; current closure through non-graph stream continuation. | `D3` | CUDA graph capture blocked; no public RT-core/paper claim. |

## What Was Genuinely Done

1. The project did a real V3 implementation campaign, not just docs.
2. It built a substantial benchmark-route evidence base across all ten promoted apps.
3. It produced real measurement tooling around same-stream and no-hidden-copy windows.
4. It built several useful fused or partner-resident prototypes.
5. It repaired and classified many routes that were previously ambiguous.
6. It created a large C ABI/interop staging body, though that body was later fenced
   out of V3 user scope.

## What Was Not Finished As V3

These remain not finished as V3 user-facing capabilities:

- general production execution graph compiler;
- universal prepared graph runtime used by all apps;
- true end-to-end zero-copy device-buffer query route;
- external CUDA stream ownership/adoption proof;
- automatic backend/partner optimizer;
- broad V3-over-V2 performance win;
- public paper-reproduction or author-code superiority claims;
- RT-native Barnes-Hut hierarchical traversal;
- capture-compatible OptiX weighted replay graph route for Triangle;
- stable packaged SDK or generated bindings.

## Current Interpretation

The most accurate current interpretation is:

```text
V3 did a lot of serious engineering, but the final historical closure narrowed
the claim to benchmark-app/current-route completion. The early performance
architecture was partially built and heavily explored, but not fully promoted
into a coherent user-facing V3 performance release.
```

That means the work should not be discarded. It should be triaged:

- promote `D3` route closures that still pass current serious pod evidence;
- revive `D2` prototypes only if they can beat V2.x or current routes on serious
  workloads;
- keep M150-M214 C ABI/embedding/interop material out of V3 current scope;
- block all `D0-D2` material from user tutorials unless it is labeled as internal
  or experimental.

## Goal-Level Decision Audit

1. Did I make a foolish decision?

   Yes, earlier work treated "many goals exist and many queues are empty" as if
   it meant "V3's original performance architecture is complete."

2. What actions made that decision foolish?

   I collapsed different completion levels into one word: "done." I did not
   maintain a target-by-target table separating design, prototype evidence,
   current-route closure, and public/user claims.

3. Was there another path that avoided being stuck on the wrong idea?

   Yes. The right path was this audit format from the start: goal family,
   evidence, completion level, user claim boundary, next action.

4. Can we now try a different path that solves the real problem?

   Yes. Use this audit to rebuild V3 around the strongest `D3` routes, rerun
   serious pod evidence for any revived `D2` prototype, and allow only passing,
   claim-clean rows into V3 tutorials and release docs.
