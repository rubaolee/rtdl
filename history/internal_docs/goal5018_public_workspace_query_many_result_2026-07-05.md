# Goal5018 - Public Workspace Query-Many Probe

## Purpose

Goal5018 reruns the prepared-base / same-scale-domain / distinct-query RayJoin
binary overlay body through the public workspace query lifecycle added in
Goal5017.

This answers a narrow question:

> Can the measured `~1.2s/query` prepared-base query-many route be expressed
> through public RTDL workspace/query APIs, without app code reaching into
> private prepared locator handles?

## Route

Fixed regime:

```text
top4 County x Zipcode
prepared base = Zipcode
distinct same-domain query batches = three tiny County geometry variants
writer-free binary route
fast-pack / no device-resident carrier
public PlanarMapWorkspace2DOptix + PlanarMapWorkspace2DOptixQuery APIs
```

Not this regime:

- not cold CLI one-shot;
- not prepared replay of the same input;
- not author-performance parity;
- not 10x.

## Code

New probe:

```text
history/internal_docs/goal5018_public_workspace_query_many_probe.py
```

It uses:

- `rtdsl.prepare_planar_map_workspace_2d_optix(...)`
- `workspace.prepare_query(...)`
- `workspace.prepare_base_points_for_queries()`
- `query.prepare_query_points_in_base()`
- `query.base_points_in_query_face_id_device_columns(...)`

The probe still calls the RayJoin paper app continuation to assemble the
writer-free descriptor result. That is deliberate: RTDL owns generic workspace,
LSI, and directed point-location lifecycles; the paper app owns overlay
continuation semantics.

## POD Evidence

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Command:

```text
python history/internal_docs/goal5018_public_workspace_query_many_probe.py \
  --left Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb \
  --right Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb \
  --capacity 1000000 \
  --output /root/rtdl_goal5018_public_workspace_query_many.json
```

Local artifact:

```text
history/internal_docs/goal5018_public_workspace_query_many_result_2026-07-05.json
```

## Results

Structural anchors:

| Query | LSI rows | Descriptor pairs |
|---|---:|---:|
| 1 | 428,322 | 15,014 |
| 2 | 428,322 | 15,014 |
| 3 | 428,322 | 15,014 |

Per-query body time:

| Query | Total body incl. query prepares | Writer-free hot excl. external prepares | Notes |
|---|---:|---:|---|
| 1 | `4.657s` | `4.081s` | first-query warmup/compile effects visible |
| 2 | `1.143s` | `0.619s` | stable prepared-base query |
| 3 | `1.124s` | `0.598s` | stable prepared-base query |

Stable post-first-query total:

```text
~1.13s/query
```

Key stable query breakdown, query 3:

```text
prepare_lsi_query_sec:                      0.0605s
prepare_point_location_base_in_query_sec:   0.4116s
prepare_query_points_in_base_sec:           0.0536s
writer_free_hot_sec_excluding_prepares:      0.5981s
total_body_sec:                              1.1238s
```

The public API route is therefore at least comparable to the earlier Goal5012
hand-built route (`~1.22s/query`) and does not introduce a regression.

## Interpretation

What improved:

- The query-many path is now expressed through public RTDL workspace/query
  APIs instead of internal prepared-locator manipulation.
- The stable measured route is about `~1.13s/query`, slightly better than the
  earlier `~1.22s/query` probe, though this should be treated as same-order
  confirmation rather than a major speedup claim.

What did not improve:

- The target `~0.42s/query` is not reached.
- Query-specific point-location locator preparation remains the largest
  stable component at about `~0.41s/query`.
- Downstream continuation remains about `~0.60s/query`.
- This does not solve distinct-domain fresh workspace cost.

## Claim Boundary

Authorized:

- public workspace-query lifecycle can express the prepared-base same-domain
  distinct-query route;
- stable top4 same-domain query body is about `~1.13s/query` after the first
  warmup query;
- all claims are for the writer-free binary route, not paper text output.

Not authorized:

- no 10x claim;
- no author-performance parity claim;
- no cold CLI claim;
- no prepared same-input replay claim;
- no claim that query-specific point-location locator prepare is solved.

## Next Bottleneck

The next real target is still:

```text
prepare_point_location_base_in_query_sec ~= 0.41s/query
```

Goal5016 already decomposed this native prepare cost into duplicate
canonicalization, range build, host copy, segment pack, upload, and accel build.
The next implementation should target this generic directed point-location
prepare path, not replay-only downstream polishing.

## Exit Label

`completed_public_workspace_query_many_probe__stable_about_1_13s_per_query__no_10x`
