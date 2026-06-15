# Goal4383 Triangle Counting Large RT-Graph P3

Date: 2026-06-14

## Verdict

P3 is implemented and measured. The triangle-counting row is no longer only a tiny repeated 4,096-ray fixture. It now has same-contract OptiX-vs-Embree evidence up to:

- 524,288 RT-Graph fixture copies;
- 1,048,576 ray probes;
- 2,621,440 triangle primitives;
- 1,048,576 expected triangle-count contribution;
- generic `PREPARED_TRIANGLE_SCENE_3D_RAY_ANY_HIT_WEIGHTED_SUM_V1`;
- no hit-row materialization;
- matching oracle counts on both OptiX and Embree.

This is still synthetic RT-Graph-shaped fixture scaling, not a full paper-dataset speedup claim. It is now strong large-input evidence for the prepared weighted any-hit summary primitive.

## Performance Matrix

Timing basis: `rt_graph_2a1_generic_rt`, fixture `degree_oriented_two_triangles`, detail `summary`. Embree uses 64 threads. Rows use the same generic ray/triangle summary contract.

| Copies | Rays | Triangles | Counts match | Embree total | OptiX total | Total speedup | Embree hot query | OptiX hot query | Hot-query speedup |
| ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 65,536 | 131,072 | 327,680 | yes | 6.158s | 2.342s | 2.63x | 302.127ms | 2.814ms | 107.37x |
| 262,144 | 524,288 | 1,310,720 | yes | 23.420s | 9.157s | 2.56x | 1182.260ms | 10.537ms | 112.20x |
| 524,288 | 1,048,576 | 2,621,440 | yes | 44.229s | 18.134s | 2.44x | 2106.430ms | 19.574ms | 107.61x |

## Explanation

The result is reasonable and useful.

The hot prepared ray/triangle any-hit summary is exactly the part where RT cores should help. On the largest row, OptiX performs the hot query in 19.6ms while Embree takes 2.11s, a 107.6x hot-query advantage.

The total speedup is much smaller because the benchmark still spends substantial time outside the native traversal: loading/building the RT-Graph contract, lowering graph relations into rays and triangles, preparing the scene, and serializing Python objects. That non-RT work is shared architecture overhead and explains why full total speedup is 2.44x rather than 107x.

This supports a prepared-primitive statement, not a full graph-system statement.

Allowed:

> On large synthetic RT-Graph-shaped triangle-counting inputs, RTDL's generic prepared weighted any-hit summary shows OptiX hot-query speedups around 108x over Embree with matching counts. End-to-end total speedup is about 2.4-2.6x because Python graph lowering and scene preparation remain in the timed path.

Not allowed:

> RTDL reproduces the full RT-Graph paper speedups.

Not allowed:

> The whole triangle-counting application is 108x faster.

## Evidence Files

- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14/triangle_2a1_embree_c65536_r5.json`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14/triangle_2a1_optix_c65536_r5.json`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14/triangle_2a1_embree_c262144_r3.json`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14/triangle_2a1_optix_c262144_r3.json`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14/triangle_2a1_embree_c524288_r2.json`
- `docs/reports/goal4383_triangle_large_rt_graph_2026-06-14/triangle_2a1_optix_c524288_r2.json`

## Remaining Debt

The data-scale blocker is removed for the synthetic RT-Graph-shaped route. The remaining public-readiness debt is provenance:

- not exact RT-Graph paper datasets;
- not authors-code `rt_tc`/`bs_tc` timing comparison;
- Python graph lowering is still timed and not yet streamed/fused.

The v2.14 wording should therefore be "large RT-Graph-shaped prepared primitive row", not "full RT-Graph reproduction."
