# Goal3285 Fused Segment Pack Ordering RayJoin LSI Probe

Date: 2026-06-04

## Verdict

Goal3285 adds a generic `pack_segments(..., order_mode=...)` path and wires the
RayJoin LSI benchmark route to use it directly. The implementation is accepted
as a reusable preparation primitive, but the pod evidence does **not** promote
ordered segment packing as the default RayJoin/LSI route.

The useful result is diagnostic:

- Locality-aware ordering can reduce the OptiX prepared query phase.
- Host-side ordered packing is still too expensive at this scale.
- The next serious target is packed/prepared column layout or resident
  preprocessing, not more Python object ordering.

## What Changed

- `rtdsl.embree_runtime.pack_segments(...)` accepts
  `order_mode={"natural","x_then_y","y_then_x","morton_xy"}`.
- `rtdsl.optix_runtime.pack_segments(...)` delegates to the shared Embree
  packing contract, preserving one generic behavior.
- Ordered packing has a fused NumPy fast path that extracts segment fields once,
  sorts centroid order, and writes the ctypes segment packet in that order.
- The RayJoin LSI prepared OptiX route now calls
  `pack_segments(records=..., order_mode=segment_order_mode)` directly instead
  of running a separate `spatial_order_segments_2d(...)` pass before packing.
- The repeated runner records `static_segment_pack_ms` separately from
  `prepare_static_scene_ms`.

No native ABI was added or renamed. No RayJoin-specific native logic was added.

## Pod Evidence

Pod: NVIDIA A40, driver 570.211.01

Command shape:

```bash
python scripts/goal3244_rayjoin_same_slice_repeated_count_runner.py \
  --rayjoin-query-exec /root/RayJoin/build/bin/query_exec \
  --rayjoin-data-dir /root/rtdl_goal3151/data/rayjoin_public_cdb \
  --rtdl-lsi-dataset "/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start256_count512.cdb + /root/rtdl_goal3151/data/rayjoin_public_cdb/br_soil_start256_count512.cdb" \
  --rtdl-pip-dataset "/root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb + /root/rtdl_goal3151/data/rayjoin_public_cdb/br_county_start0_count512.cdb" \
  --rayjoin-warmup 2 \
  --rayjoin-repeat 10 \
  --rayjoin-process-repeats 3 \
  --rtdl-warmup 1 \
  --rtdl-repeat 5 \
  --rtdl-pip-count-mode exact \
  --rtdl-lsi-segment-order MODE
```

The PIP companion lane used exact mode in this run. A prior attempt with
`z_point + crossing_only` failed validation on this slice (`129 != 1430`), so
that setting was not used for the LSI ordering artifact.

| segment order | RTDL LSI query ms | RayJoin query ms | RTDL/RayJoin query ratio | query pack ms | static segment pack ms | prepare static scene ms | visible LSI count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| natural | 0.543058 | 0.248885 | 2.182x | 19.953 | 6.864 | 1.003 | 269 |
| x_then_y | 0.419296 | 0.241518 | 1.736x | 75.984 | 25.667 | 0.869 | 269 |
| y_then_x | 0.363538 | 0.236392 | 1.538x | 61.777 | 21.466 | 0.793 | 269 |
| morton_xy | 0.460254 | 0.238991 | 1.926x | 74.636 | 25.245 | 0.953 | 269 |

Artifacts:

- `docs/reports/goal3285_fused_pack_lsi_segment_order_pod/natural.json`
- `docs/reports/goal3285_fused_pack_lsi_segment_order_pod/x_then_y.json`
- `docs/reports/goal3285_fused_pack_lsi_segment_order_pod/y_then_x.json`
- `docs/reports/goal3285_fused_pack_lsi_segment_order_pod/morton_xy.json`

## Interpretation

The ordered layouts do help the GPU-side LSI query:

- `y_then_x` improves the prepared query from 0.543 ms to 0.364 ms.
- `x_then_y` improves it to 0.419 ms.
- `morton_xy` improves it to 0.460 ms.

But the ordered pack costs dominate the end-to-end path:

- Natural query pack: 19.953 ms.
- `y_then_x` query pack: 61.777 ms.
- `x_then_y` query pack: 75.984 ms.
- `morton_xy` query pack: 74.636 ms.

So this is a useful primitive and a useful diagnosis, not a benchmark win. The
locality signal is real, but current Python/NumPy ordered object packing is the
wrong place to pay for it.

## Claim Boundary

All artifacts keep the claim boundary false for public speedup, RayJoin paper
reproduction, RT-core speedup, RTDL-beats-RayJoin, true zero-copy, and release.

This goal authorizes only an internal engineering conclusion:

> Generic segment ordering can improve the OptiX LSI traversal phase, but the
> current host-side ordered packing path is not a promoted high-performance
> RayJoin route.

## Next Engineering Target

The next useful target is a generic packed/prepared layout primitive that avoids
Python object reorder costs entirely:

- accept already-columnar segment inputs,
- preserve caller IDs,
- optionally build a reordered packet or scene layout inside the packing or
  preparation layer,
- expose phase timing for layout/reorder separately from traversal, and
- keep the primitive generic: segment records, caller IDs, layout hints, and
  prepared scenes; no RayJoin names or policy in native code.
