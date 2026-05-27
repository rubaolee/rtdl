# Goal2634 Gap Closure And RT Baseline

Status: internal engineering evidence, not public speedup wording.

## Scope

This report closes the current benchmark-path gaps raised after the first
Goal2626 Embree-vs-OptiX matrix:

1. RayDB real data movement / reduction gap.
2. Spatial RayJoin missing prepared continuation for the full route.
3. Triangle counting fallback instead of RT-core graph path.
4. Barnes-Hut contract mismatch.
5. Contact-manifold collector-only timing instead of generic RT witness discovery.

The fixes keep the native engine app-agnostic. New engine/runtime work is
expressed as generic primitives or prepared continuations, not app-specific
RayDB, RayJoin, graph, Barnes-Hut, or contact logic.

## Closure Summary

| Gap | Closure | Evidence |
| --- | --- | --- |
| RayDB real data movement / reduction | Goal2626 matrix uses `optix_partner_resident_experimental` with warm grouped-count/sum query medians. | `0005a051`, `0d987428`; latest full matrix below. |
| Spatial RayJoin prepared continuation | Overlay-seed route now uses prepared generic shape-pair relation flags for the full scoped route. | `4960079e`, `e517160e`; latest full matrix below. |
| Triangle counting fallback | Benchmark path now uses RT-Graph-style `rt_graph_2a1_generic_rt` with generic prepared 3-D ray/triangle weighted any-hit summary and CuPy-owned graph preprocessing. | `69227aec`, `ca8d96a7`, `f18fbfb2`; latest full matrix below. |
| Barnes-Hut contract mismatch | Matrix compares the same prepared fixed-radius node-coverage threshold decision contract on Embree and OptiX. | `eabbe337`, `ac0abfb3`; latest full matrix below. |
| Contact-manifold collector-only row | Matrix now uses prepared generic `AABB_INDEX_QUERY_2D` range-intersection row output plus generic `COLLECT_K_BOUNDED`, with the primary metric on prepared row-output median. | `6df8e7a8`, `56e1f9b2`; latest full matrix below. |

## Latest Standard Matrix

Pod:

- SSH command supplied by user: `ssh root@203.57.40.101 -p 10165 -i ~/.ssh/id_ed25519`
- Local key used: `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`
- GPU: NVIDIA RTX A5000, driver 565.57.01, 24564 MiB
- Pod checkout: `/root/rtdl_goal2627/rtdl`
- Commit: `56e1f9b230cdef6d803191c8804f192133b4d020`
- Command: `PYTHONPATH=src:. python3 scripts/goal2626_benchmark_embree_optix_baseline.py --scale standard --artifact-dir /root/rtdl_goal2634_full_standard_prepared_contact --timeout-sec 1200`
- Local copied evidence: `docs/reports/goal2634_full_standard_prepared_contact_pod/summary.md`
- Slim JSON: `docs/reports/goal2634_full_standard_prepared_contact_pod/summary_slim.json`

| App | Comparison group | Embree sec | OptiX sec | OptiX speedup vs Embree |
| --- | --- | ---: | ---: | ---: |
| Barnes-Hut | node coverage prepared threshold decision | 0.0388851 | 0.00855045 | 4.55x |
| Contact manifold | generic AABB broadphase + bounded collection | 0.485812 | 0.0184764 | 26.3x |
| Hausdorff/X-HD | threshold decision | 0.102451 | 0.0311073 | 3.29x |
| LibRTS spatial index | AABB index all count-only | 20.707 | 0.691477 | 29.9x |
| RayDB-style | grouped count | 0.222185 | 0.000793088 | 280x |
| RayDB-style | grouped sum | 0.243746 | 0.000977349 | 249x |
| Robot collision | prepared collision flags | 0.00853798 | 0.00161413 | 5.29x |
| RT-DBSCAN | cluster signature | 20.6102 | 1.62144 | 12.7x |
| RTNN | prepared 3-D ranked summary | 0.2638 | 0.00153247 | 172x |
| Spatial RayJoin | all-backend scoped query summary | 0.0203149 | 0.000529638 | 38.4x |
| Triangle counting | RT-Graph-style RT-2A1 summary | 0.039049 | 0.000364401 | 107x |

All promoted benchmark comparison rows now have both Embree and OptiX entries,
and OptiX is faster on the recorded standard primary metric for every row.

## Why The Listed Optimizations Were Not Fully Used Earlier

| Item | Why it was not fully used earlier | Current state |
| --- | --- | --- |
| Whole-path true zero-copy | Earlier goals first stabilized correctness, backend parity, and app-agnostic primitive contracts. Whole-path zero-copy is only safe after the data ownership and lifetime contracts are explicit. | Still not a broad claim. RayDB and several prepared paths now use partner/device-resident timing where it matters; broader zero-copy remains a next-version partner/runtime target. |
| Typed host buffers for RayDB-style columnar payloads | The initial RayDB row still used a conservative host-facing path so correctness and grouped-reduction semantics could be verified first. | The benchmark path now uses partner-resident typed grouped reduction for OptiX count/sum. |
| Partner-resident typed column execution as main benchmark path | This required a benchmark-specific reason and exact metric boundary; otherwise it would have been premature public wording. | It is now the RayDB OptiX benchmark path, bounded to grouped integer count/sum query medians. |
| Device-resident continuation for Spatial RayJoin overlay | The missing overlay route had to be expressed as generic prepared shape-pair relation flags, not a RayJoin-native continuation. | The scoped full route now uses prepared OptiX continuation for overlay-seed workloads. |
| Real RT-core triangle counting path | The first graph path was a fallback while the RT-Graph-style geometry lowering and warm query metric were validated. | The benchmark now uses generic prepared 3-D ray/triangle RT-2A1 summary with CuPy-owned graph preprocessing. |
| Same-contract Barnes-Hut hierarchical aggregate-frontier primitive | A previous native path risked app-specific force logic, so it was rejected as a benchmark contract. | Current matrix uses same-contract node-coverage threshold decision. Full hierarchical aggregate-frontier remains future generic primitive work. |
| Generic RT witness discovery for contact manifold | The app had generic AABB discovery, but the matrix timed only native `COLLECT_K_BOUNDED` over Python oracle rows. A first fix revealed OptiX index construction dominated; prepared row-output reuse was required. | Current matrix uses prepared generic `AABB_INDEX_QUERY_2D` row-output median plus generic bounded collection. No collision-specific native engine logic was added. |

## Boundary

These are exact-subpath internal benchmark results. They do not authorize
whole-app public speedup claims, package-install claims, broad zero-copy claims,
or claims that RTDL is a universal compute engine. They do support the narrower
engineering conclusion that the current promoted benchmark suite now has
same-contract Embree and OptiX rows, and that the OptiX/RT path is faster than
Embree for the recorded standard primary metrics.
