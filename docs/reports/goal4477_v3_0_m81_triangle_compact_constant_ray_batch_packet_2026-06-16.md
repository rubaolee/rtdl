# Goal4477 / V3.0 M81: Triangle Counting Compact Constant-Ray Batch

## Verdict

M81 adds a correct, app-agnostic OptiX prepared ray-batch ABI for the common layout:

- `ids`, `ox`, and `oz` are partner-owned device columns.
- `oy`, direction, and `tmax` are constants.
- Native code packs the generic 3-D rays on GPU and exposes the batch through the same prepared ray-batch weighted any-hit primitive.

This ABI is valid and tested, but it is not the current Triangle Counting performance route. The current best remains M78: `numba_direct + generic prepared ray-batch weighted any-hit using full ray columns`.

## Measured Result

Best M81 run is the better of two `w1/r3` pod runs per dataset. M78 is the current best packet from Goal4474/Goal4475.

| Dataset | Count | M78 total | M81 best total | M78 / M81 | M81 result | M78 query | M81 query | M78 traversal | M81 traversal |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| com-lj | 177,820,130 | 5.404s | 6.532s | 0.83x | slower by 20.9% | 0.180s | 0.180s | 0.175s | 0.175s |
| soc-LiveJournal1 | 285,730,264 | 11.669s | 13.562s | 0.86x | slower by 16.2% | 0.264s | 0.266s | 0.257s | 0.259s |
| com-orkut | 627,584,181 | 35.379s | 37.623s | 0.94x | slower by 6.3% | 1.732s | 1.729s | 1.687s | 1.684s |

All counts match M78.

## Phase Reading

| Dataset | M78 segment ray build | M81 segment ray build | M78 prepared batch build | M81 prepared batch build | Reading |
|---|---:|---:|---:|---:|---|
| com-lj | 1.264s | 1.298s | 0.672s | 0.656s | Tiny prepared-pack win is overwhelmed elsewhere. |
| soc-LiveJournal1 | 1.299s | 1.684s | 0.961s | 0.965s | No prepared-pack win; segment construction is worse. |
| com-orkut | 8.147s | 8.519s | 6.118s | 6.772s | Query/traversal is stable; build path worsens. |

The compact ABI targeted `prepared_ray_batch_build`. That phase is not the dominant remaining bottleneck on com-lj/soc-LiveJournal1, and it is not stable enough on com-orkut to justify switching. RT traversal and native query pack medians remain essentially unchanged, so M81 does not expose an RT-core efficiency problem.

## Interpretation

M81 is useful as a generic runtime capability, but not as the promoted Triangle Counting route. It proves that RTDL can accept a more compact, app-agnostic prepared ray layout without adding graph-specific native engine logic. It also proves that this is not where the remaining Triangle Counting performance debt mainly lives.

Next target: partner materialization and segment-ray construction, especially unique-key materialization and repeated large temporary allocations, while keeping the primitive contract generic.

## Claim Boundary

- Do not claim M81 improves Triangle Counting performance.
- Do not claim public RT-core triangle-count speedup from this packet.
- Do not switch current-best route from M78.
- Do keep the compact ray-batch ABI as tested app-agnostic runtime surface.

## Artifacts

- `goal4477_v3_0_m81_triangle_compact_ray_batch_com_lj_w1r3_2026-06-16.json`
- `goal4477_v3_0_m81_triangle_compact_ray_batch_com_lj_w1r3_rerun_2026-06-16.json`
- `goal4477_v3_0_m81_triangle_compact_ray_batch_soc_livejournal1_w1r3_2026-06-16.json`
- `goal4477_v3_0_m81_triangle_compact_ray_batch_soc_livejournal1_w1r3_rerun_2026-06-16.json`
- `goal4477_v3_0_m81_triangle_compact_ray_batch_com_orkut_w1r3_2026-06-16.json`
- `goal4477_v3_0_m81_triangle_compact_ray_batch_com_orkut_w1r3_rerun_2026-06-16.json`
- `goal4477_v3_0_m81_triangle_compact_constant_ray_batch_packet_2026-06-16.json`
