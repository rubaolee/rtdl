# Goal5010-5012: Point-Location Query-Many Diagnosis And Reuse Result

Date: 2026-07-05

## Verdict

`completed_point_location_query_point_reuse_win__full_overlay_query_many_now_about_1_22s__10x_still_not_reached`

Goals5010-5012 continue from Goal5009.

Goal5009 measured the full writer-free binary overlay body in the
prepared-base / same-domain / distinct-query regime:

```text
~1.47-1.49s/query
```

The bottleneck had moved away from LSI and into point-location/downstream.

Goals5010-5012 answer:

1. Which part of point-location is slow?
2. Can any of it be reused generically?
3. Does that reuse move the full overlay body?

## Artifacts

Probes:

```text
history/internal_docs/goal5010_point_location_query_many_probe.py
history/internal_docs/goal5011_point_location_query_point_reuse_probe.py
history/internal_docs/goal5012_overlay_shared_point_query_probe.py
```

POD artifacts:

```text
history/internal_docs/goal5010_point_location_query_many_artifacts_2026-07-05/rtdl_goal5010_point_location_query_many.json
history/internal_docs/goal5011_point_location_query_point_reuse_artifacts_2026-07-05/rtdl_goal5011_point_location_query_point_reuse.json
history/internal_docs/goal5012_overlay_shared_point_query_artifacts_2026-07-05/rtdl_goal5012_overlay_shared_point_query.json
```

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

## Goal5010: Point-Location Cost Decomposition

Goal5010 split point-location into:

1. reusable right-base locator (`left vertices in right map`);
2. per-query left locator (`right vertices in left map`);
3. query-point preparation;
4. actual point-location traversal/output.

### Reusable right-base direction

```text
prepare reusable right locator:          3.888s
prepare left query points:               0.055s
left vertices in right map run:          0.008s
```

This cost is setup-like and reusable.  It is not the stable per-query blocker.

### Per-query left locator direction

For distinct left/query maps:

| Batch | Total PL body | Prepare left locator | Prepare right query points | Run right vertices in left |
|---|---:|---:|---:|---:|
| 1 | `0.778s` | `0.445s` | `0.308s` | `0.0247s` |
| 2 | `0.790s` | `0.453s` | `0.313s` | `0.0245s` |
| 3 | `0.780s` | `0.444s` | `0.312s` | `0.0246s` |

The point-location traversal itself is fast:

```text
~0.025s
```

The cost is preparation:

```text
left locator prepare:       ~0.45s/query
right query-point prepare:  ~0.31s/query
```

## Goal5011: Reuse Prepared Query Points Across Locators

Source audit showed that the native point-location call consumes:

```text
(prepared locator, prepared query points)
```

as separate handles.  Goal5011 tested whether the constant `right.points`
prepared query-point buffer can be reused across same-domain left locators.

Result:

```text
shared_prepare_points_sec = 0.301s
```

Local prepared points vs shared prepared points:

| Batch | Local prepare points | Local run | Shared run | Same hash/count? |
|---|---:|---:|---:|---|
| 1 | `0.290s` | `0.0243s` | `0.0238s` | yes |
| 2 | `0.288s` | `0.0243s` | `0.0237s` | yes |
| 3 | `0.290s` | `0.0247s` | `0.0237s` | yes |

The shared buffer produced identical positive counts and face hashes for all
three locators.

Interpretation:

```text
prepared point-location query points are reusable across same-domain locators
for this workload.
```

This is a generic point-location buffer reuse opportunity, not RayJoin overlay
logic.

## Goal5012: Full Overlay With Shared Right Query Points

Goal5012 connected the reuse back to the full writer-free binary overlay body.

The probe prepares the constant right-vertex query point buffer once, keeps the
bootstrap locator alive for lifetime safety, and passes the same prepared points
to each distinct left locator.

Setup outside the per-query body:

```text
bootstrap locator prepare:       0.443s
shared right query points prepare: 0.303s
```

Full overlay body:

| Query | Total body | Prepare LSI query | Prepare left PL | Pipeline hot | LSI phase | Downstream | Rows | Pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| query 1 | `4.828s` | `0.088s` | `0.440s` | `4.300s` | `3.072s` | `1.229s` | `428322` | `15014` |
| query 2 | `1.206s` | `0.047s` | `0.446s` | `0.713s` | `0.145s` | `0.568s` | `428322` | `15014` |
| query 3 | `1.235s` | `0.044s` | `0.445s` | `0.746s` | `0.143s` | `0.603s` | `428322` | `15014` |

Stable body over queries 2-3:

```text
~1.22s/query
```

This improves Goal5009:

```text
~1.48s/query -> ~1.22s/query
```

The overall improvement versus warm-process fresh fast-pack is now:

```text
4.22s / 1.22s ~= 3.46x
```

## What This Proves

1. The main point-location traversal is not slow (`~0.025s` for the heavy
   right-vertices-in-left query).
2. A constant query-point batch can be prepared once and reused across
   same-domain locators with identical output hashes/counts.
3. Full overlay query-many body improves materially:

```text
~1.48s -> ~1.22s
```

4. The optimization is generic in shape:

```text
prepared point-location query-point buffer reuse
```

not a RayJoin-specific output or overlay shortcut.

## What This Does Not Prove

This does not prove:

- 10x (`~0.42s`) full overlay;
- cold CLI one-shot speedup;
- distinct-domain speedup;
- author-performance parity;
- device-resident carrier payoff;
- that the shared prepared-points behavior is already a documented public RTDL
  contract.

The current usage is evidence for a product/API contract, not yet a released
API guarantee.

## Remaining Bottleneck

After shared query-point reuse, the main remaining stable costs are:

| Component | Approximate cost |
|---|---:|
| prepare left point-location locator | `~0.445s/query` |
| downstream after LSI | `~0.57-0.60s/query` |
| LSI phase | `~0.14s/query` |
| prepare LSI query handle | `~0.045s/query` |

The biggest single remaining target is:

```text
prepare left point-location locator
```

That cost exists because the distinct left/query map becomes the base map for
the `right vertices in left map` direction.  Unlike LSI right-base reuse, this
base changes with each query.

## Next Goal

Goal5013 should decide whether `prepare left point-location locator` can be
reduced generically.

The likely product direction is:

```text
generic fixed-domain / resident point-location workspace
```

or a documented conclusion that this `~0.445s/query` locator prepare is the
current non-fusion floor for distinct-query overlay.

Do not reopen device-resident carrier or RayJoin-specific kernels to hide this.

## Claim Boundary

Authorized:

- full overlay query-many body improved to `~1.22s/query` in the measured
  same-domain distinct-query regime;
- current speedup over warm-process fresh fast-pack is about `~3.5x`;
- prepared query-point buffer reuse is a real generic candidate.

Not authorized:

- no 10x claim;
- no `~0.42s` claim;
- no public API guarantee for cross-locator prepared-points reuse until it is
  formalized;
- no author-ratio claim;
- no RayJoin-specific core shortcut.

## Exit Label

`completed_point_location_query_point_reuse_win__full_overlay_query_many_now_about_1_22s__10x_still_not_reached`
