# Goal 1396 - v1.5 Architecture, App Migration, And Performance Comparison

Date: 2026-05-06

## Status

This document is a formal synthesis of the v1.5 work, the v1.0-to-v1.5 architecture shift, app migration meaning, and current Embree/OptiX performance evidence.

It is not a new benchmark artifact and does not authorize new public speedup wording. v1.5 per-app Embree/OptiX timing has not been collected as a complete app suite. The v1.5 evidence is claim-grade for the stable generic primitive packet, not for whole-application performance.

## 1. What v1.5 Did

v1.5 turns the post-v1.0 internal work into a reviewed generic traversal-plus-reduction primitive layer.

Stable primitive surface:

- `ANY_HIT`
- `COUNT_HITS`
- `REDUCE_FLOAT(MIN)`
- `REDUCE_FLOAT(MAX)`
- `REDUCE_FLOAT(SUM)`
- `REDUCE_INT(COUNT)`
- `REDUCE_INT(SUM)`

Active v1.5 engineering backends:

- Embree
- OptiX

Frozen before v2.1:

- Vulkan
- HIPRT
- Apple RT

Still experimental:

- `COLLECT_K_BOUNDED`

Fresh-Git pod evidence from Goal1393 validated the stable primitive packet on Linux x86_64 with Python 3.12.3:

- CPU direct `ANY_HIT + COUNT_HITS`: `ok`, hit count `256`
- Embree direct `ANY_HIT + COUNT_HITS`: `ok`, hit count `256`
- OptiX direct `ANY_HIT + COUNT_HITS`: `ok`, hit count `256`
- Prepared OptiX `ANY_HIT + COUNT_HITS`: `ok`, hit count `256`
- Stable scalar reductions: all expected values returned

Goal1394 then obtained 3-AI consensus for bounded public wording. Goal1395 concluded that `main` is ready for an explicit v1.5 release operation, but no release/tag action has been performed by those reports.

Primary evidence:

- `docs/reports/goal1393_v1_5_stable_primitive_claim_evidence_2026-05-06.md`
- `docs/reports/goal1394_three_ai_v1_5_public_wording_consensus_2026-05-06.md`
- `docs/reports/goal1395_v1_5_release_readiness_decision_2026-05-06.md`

## 2. v1.5 Architecture And Language Design Compared With v1.0

v1.0 was an app-shaped proof release. It demonstrated that RTDL can express real non-rendering workloads from Python, lower traversal-heavy parts to RT-capable backends, and document bounded performance claims. To make those apps useful and measurable, v1.0 intentionally accepted app-specific native continuations.

v1.5 changes the architecture target. Instead of treating each app as a separate native backend problem, v1.5 defines reusable app-name-free primitive contracts:

- traversal primitive: `ANY_HIT`
- count primitive: `COUNT_HITS`
- scalar float reductions: `REDUCE_FLOAT(MIN|MAX|SUM)`
- scalar integer reductions: `REDUCE_INT(COUNT|SUM)`

The practical design shift is:

| Area | v1.0 | v1.5 |
| --- | --- | --- |
| Architecture center | App-shaped proof machinery | Generic traversal-plus-reduction primitive layer |
| Native backend shape | App-specific continuations accepted where needed | App-name-free primitive contracts preferred |
| Python role | App orchestration, lowering, continuation, output shaping | Still app orchestration and lowering; not replaced |
| Public claim type | Bounded app/subpath claims where reviewed | Generic primitive readiness only |
| Speedup scope | Selected reviewed subpaths, not whole apps | No new speedup claim from v1.5 primitive packet |
| Active backend focus | Many proof surfaces exist | Embree + OptiX only |
| Frozen backends | Vulkan/HIPRT/Apple RT have proof surfaces | No new implementation effort before v2.1 |
| Collection primitive | App-specific bounded outputs in some paths | `COLLECT_K_BOUNDED` remains experimental |

v1.5 is not a universal native compute engine. It does not remove Python app-specific control, does not make whole applications native, and does not automatically improve all app performance. Its contribution is a smaller, reviewed, reusable primitive layer that apps can target.

## 3. App Reimplementation Meaning

The table below summarizes how each v1.0 app-shaped path maps toward v1.5 generic primitives. This is an architecture/migration map, not proof that every app has complete v1.5 per-app performance evidence.

| App | v1.0 implementation shape | v1.5 reimplementation direction |
| --- | --- | --- |
| `database_analytics` | Prepared DB-specific compact summaries for traversal/filter/grouping. | Map compact-summary filter/group patterns toward generic traversal plus `REDUCE_INT` / `REDUCE_FLOAT`; SQL/DBMS behavior remains outside. |
| `graph_analytics` | Visibility-edge any-hit and graph-specific native summaries. | Use generic `ANY_HIT + COUNT_HITS`; BFS frontier control and triangle-set intersection remain app/Python logic. |
| `apple_rt_demo` | Apple Metal/MPS RT proof surface. | Not an active v1.5 target; preserved as existing proof surface only. |
| `service_coverage_gaps` | Prepared fixed-radius gap-summary traversal. | Generic fixed-radius threshold/count reduction path; nearest-clinic output remains outside. |
| `event_hotspot_screening` | Prepared fixed-radius count-summary traversal. | Generic fixed-radius count plus `REDUCE_INT(COUNT)` summary. |
| `facility_knn_assignment` | Coverage-threshold prepared decision, not ranked KNN. | Generic threshold decision; ranked KNN assignment remains outside. |
| `road_hazard_screening` | Native segment/polygon compact hazard summary. | Generic traversal/count summary direction; GIS/routing remains outside. |
| `segment_polygon_hitcount` | Prepared native segment/polygon hit-count traversal. | Generic hit/count reduction target. |
| `segment_polygon_anyhit_rows` | Prepared bounded native pair-row emitter. | Still bounded; collection remains experimental, so not part of stable v1.5 primitive surface. |
| `polygon_pair_overlap_area_rows` | RT-assisted LSI/PIP candidate discovery plus exact-area native continuation. | Candidate traversal plus backend-neutral `REDUCE_FLOAT(SUM)` exact-area summary direction. |
| `polygon_set_jaccard` | Native-assisted candidate discovery plus exact set-area/Jaccard continuation. | Safe-chunk candidate traversal plus backend-neutral `REDUCE_FLOAT(SUM)` score plumbing; positive speedup remains blocked. |
| `hausdorff_distance` | Prepared fixed-radius threshold-decision traversal. | Generic fixed-radius threshold decision; exact Hausdorff/KNN rows remain outside. |
| `ann_candidate_search` | Prepared candidate-coverage threshold decision. | Generic fixed-radius threshold/count; ANN ranking/indexing remains outside. |
| `outlier_detection` | Prepared scalar density threshold-count. | Generic `REDUCE_INT(COUNT)` scalar summary. |
| `dbscan_clustering` | Prepared scalar core-count/core-flag path. | Generic scalar count for core-count; cluster expansion remains Python/app logic. |
| `robot_collision_screening` | Prepared ray/triangle any-hit count and pose flags. | Generic `ANY_HIT + COUNT_HITS`; grouped pose flags remain bounded app logic. |
| `barnes_hut_force_app` | Prepared fixed-radius node-coverage decision. | Generic fixed-radius coverage/count; force-vector reduction remains outside. |
| `hiprt_ray_triangle_hitcount` | HIPRT-specific validation/demo path. | Not an active v1.5 target before v2.1. |

## 4. Performance Comparison: v1.0 vs v1.5, Embree And OptiX

### How To Read This Section

There are two different evidence classes:

- v1.0 / v1.1 app-subpath evidence: reviewed app or subpath performance evidence, sometimes with positive OptiX wording.
- v1.5 primitive evidence: fresh-Git validation that generic primitives are correct across CPU, Embree, and OptiX on the bounded Goal1393 fixture.

There is not yet a complete v1.5 per-app timing suite for all apps on both Embree and OptiX. Therefore, the v1.5 app-performance cells below are marked as `not newly measured` unless the evidence is exactly the Goal1393 primitive fixture.

### App-By-App Matrix

The v1.0 columns summarize the reviewed app/subpath evidence that existed before the v1.5 primitive release candidate. The v1.5 columns summarize only evidence collected under the v1.5 generic primitive packet. When a v1.5 cell says `not measured`, that is intentional: no complete v1.5 per-app Embree/OptiX timing suite has been run.

| App | v1.0 Embree / baseline evidence | v1.0 OptiX / NVIDIA RT evidence | v1.5 Embree evidence | v1.5 OptiX evidence |
| --- | --- | --- | --- | --- |
| `database_analytics` | Embree remains the warm-query comparison point; warm-query median still favors Embree in reviewed mixed evidence. | Execution-unblocked with real OptiX DB BVH candidate discovery and native compact summaries, but mixed; no positive DB speedup wording. | Not measured as a v1.5 app. Embree is active for the generic primitive layer only. | Not measured as a v1.5 app. OptiX primitive fixture validates stable primitives, not DB app speedup. |
| `graph_analytics` | Embree is the comparison baseline for total graph paths; total timing is scene-preparation dominated. | Direct packed-ray OptiX traversal is around `0.0002s` at tested 30k/60k-copy scales, but total path is mixed; no graph speedup claim. | Not measured as a v1.5 app. Generic `ANY_HIT + COUNT_HITS` maps to graph visibility-style traversal but no app timing exists. | Not measured as a v1.5 app. OptiX `ANY_HIT + COUNT_HITS` is validated only on the Goal1393 primitive fixture. |
| `apple_rt_demo` | Not an Embree performance target in the NVIDIA/Embree comparison matrix. | Not an OptiX target; Apple-specific proof surface only. | Frozen before v2.1; no new v1.5 Embree timing. | Not applicable. |
| `service_coverage_gaps` | Reviewed same-semantics baseline exists for the prepared gap-summary query/native subpath. | Reviewed bounded RTX query/native subpath: `0.136545s`, `1.61x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app. Generic fixed-radius threshold/count direction only. | Not measured as a v1.5 app; prior OptiX number remains a bounded v1.0-style subpath claim. |
| `event_hotspot_screening` | Reviewed same-semantics baseline exists for the prepared count-summary query phase. | Reviewed bounded RTX query subpath: `0.165999s`, `1.55x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app. Generic fixed-radius count direction only. | Not measured as a v1.5 app; prior OptiX number remains bounded to the reviewed query phase. |
| `facility_knn_assignment` | Reviewed CPU oracle baseline for the coverage-threshold decision; ranked KNN remains outside. | Reviewed coverage-threshold RTX query: `0.111619s`, `80.60x` versus CPU oracle baseline. | Not measured as a v1.5 app. Generic threshold-decision direction only. | Not measured as a v1.5 app; prior OptiX number is not a ranked-KNN claim. |
| `road_hazard_screening` | Reviewed same-scale Embree subpath at 40k copies is the comparison baseline. | Reviewed prepared native RTX subpath: `0.230652s`, `3.53x` versus same-scale Embree at 40k copies. | No new v1.5 app timing. Embree baseline remains the older reviewed subpath baseline only. | No new v1.5 app timing. Prior OptiX claim remains bounded to compact hazard summary traversal/count. |
| `segment_polygon_hitcount` | Reviewed same-semantics baseline exists for prepared compact hit-count traversal. | Reviewed RTX query/native subpath: `0.146860s`, `1.71x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app. Generic hit/count reduction direction only. | Not measured as a v1.5 app. |
| `segment_polygon_anyhit_rows` | Reviewed same-semantics baseline exists for bounded prepared pair-row traversal. | Reviewed bounded RTX query/native subpath: `0.192639s`, `3.03x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app; bounded collection remains experimental. | Not measured as a v1.5 app; `COLLECT_K_BOUNDED` remains outside stable v1.5. |
| `polygon_pair_overlap_area_rows` | Embree is the reviewed comparison backend for the Goal1263 candidate-discovery plus exact-area pipeline. | Goal1263 reviewed bounded OptiX acceleration at 40k/80k/160k; at 160k, about `1.4x` faster candidate discovery and `1.2x` faster observed pipeline versus Embree. | No new v1.5 full-app timing. Generic direction is candidate traversal plus `REDUCE_FLOAT(SUM)`. | No new v1.5 full-app timing. Existing positive wording remains limited to candidate discovery plus exact-area continuation. |
| `polygon_set_jaccard` | Embree remains faster than OptiX in current reviewed evidence at safe chunking. | Correctness-ready at chunk `1024`, including 8192 copies, but OptiX remains slower than Embree; no positive speedup wording. | No new v1.5 app timing. Generic direction is candidate traversal plus scalar area reductions. | No new positive v1.5 speedup; prior OptiX evidence remains slower than Embree. |
| `hausdorff_distance` | Reviewed Embree directed-summary subpath is the comparison baseline. | Reviewed threshold-decision RTX subpath: `0.122389s`, `13.73x` versus Embree directed-summary subpath. | No new v1.5 app timing. Generic fixed-radius threshold decision direction only. | No new v1.5 app timing; exact Hausdorff remains outside the claim. |
| `ann_candidate_search` | Reviewed same-semantics baseline exists for candidate-coverage decision. | Reviewed candidate-coverage RTX query/native subpath: `0.105215s`, `4.86x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app. Generic fixed-radius threshold/count direction only. | Not measured as a v1.5 app; full ANN indexing/ranking remains outside. |
| `outlier_detection` | Reviewed same-semantics baseline exists for fixed-radius scalar threshold-count. | Reviewed density-summary RTX query/native subpath: `0.122348s`, `4.64x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app. Generic `REDUCE_INT(COUNT)` direction only. | Not measured as a v1.5 app; per-point labels remain outside. |
| `dbscan_clustering` | Reviewed same-semantics baseline exists for fixed-radius scalar core-count. | Reviewed core-count RTX query/native subpath: `0.122921s`, `6.62x` versus reviewed same-semantics baseline. | Not measured as a v1.5 app. Generic scalar core-count direction only. | Not measured as a v1.5 app; cluster expansion remains outside. |
| `robot_collision_screening` | Reviewed 36M chunked Embree any-hit baseline exists only for normalized per-pose wording. | Reviewed normalized per-pose RTX wording: `0.178471s` for 64M poses and `918.91x` normalized per-pose throughput versus reviewed 36M chunked Embree any-hit baseline; not same-total-work wall-time. | No new v1.5 app timing. Generic `ANY_HIT + COUNT_HITS` direction only. | No new v1.5 whole robot timing; prior OptiX wording is normalized per-pose only. |
| `barnes_hut_force_app` | Reviewed Embree node-coverage baseline exists for the threshold traversal only. | Reviewed node-coverage RTX query: `0.222256s`, `240.56x` versus Embree node-coverage baseline. | No new v1.5 app timing. Generic fixed-radius coverage/count direction only. | No new v1.5 app timing; force-vector reduction and simulation remain outside. |
| `hiprt_ray_triangle_hitcount` | HIPRT-specific validation/demo path, not an Embree-vs-OptiX app target. | Not an OptiX public wording target. | Frozen before v2.1; no new v1.5 Embree timing. | Not applicable. |

### v1.5 Primitive Performance Evidence

Goal1393 recorded timings inside `stable_primitive_evidence.json`, but those timings are evidence for the bounded primitive fixture only. They are not public speedup benchmarks and do not authorize app-level performance claims.

The claim-grade v1.5 result is correctness/parity and primitive readiness:

- direct `ANY_HIT + COUNT_HITS` works on CPU, Embree, and OptiX for the bounded fixture;
- prepared OptiX `ANY_HIT + COUNT_HITS` works for the bounded fixture;
- all stable scalar reductions return expected values;
- public speedup wording remains unauthorized by the Goal1393 artifact itself.

## 5. Conclusions

v1.5 is an architectural/language release candidate, not a new performance-release claim.

The strongest v1.5 conclusion is:

> RTDL has a reviewed generic traversal-plus-reduction primitive layer with fresh-Git Embree/OptiX validation for the stable primitive packet.

The strongest app-performance conclusion remains bounded to older reviewed subpath evidence:

> Several app subpaths have reviewed OptiX-positive evidence, while DB, graph, and Jaccard remain mixed or slower versus Embree under current evidence.

The missing performance work is clear:

- run a complete v1.5 per-app Embree/OptiX timing suite using the generic primitive paths;
- separate prepare, query, reduction, materialization, Python continuation, and validation phases;
- compare same-contract Embree and OptiX per app;
- only promote new app speedup wording after separate evidence and review.
