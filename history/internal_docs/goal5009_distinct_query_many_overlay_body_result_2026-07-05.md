# Goal5009: Distinct-Query Prepared-Base Full Binary Overlay Body Result

Date: 2026-07-05

## Verdict

`completed_distinct_query_many_overlay_body_measured__10x_not_reached__next_target_point_location_and_downstream`

Goal5009 extends Goal5008 from LSI-only to the full writer-free binary overlay
body.

Goal5008 proved that LSI can serve distinct same-domain query batches at about:

```text
~0.117s LSI/query
```

Goal5009 asks the harder question:

> Does the full writer-free binary overlay body reach the 10x target
> (`~0.42s/query`) in that same prepared-base / same-domain / distinct-query
> regime?

Answer:

```text
No.  Stable full overlay body is ~1.47-1.49s/query.
```

This is a real improvement over the `~4.22s` warm-process fresh fast-pack route,
but it is not 10x.

## Artifacts

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Probe:

```text
history/internal_docs/goal5009_distinct_query_many_overlay_probe.py
```

POD artifact copied locally:

```text
history/internal_docs/goal5009_distinct_query_many_overlay_artifacts_2026-07-05/rtdl_goal5009_distinct_query_many_overlay.json
history/internal_docs/goal5009_distinct_query_many_overlay_artifacts_2026-07-05/rtdl_goal5009_distinct_query_many_overlay.log
```

## Regime

The measured regime is:

```text
prepared right/base
same scale-domain
three distinct full-size left/query batches
writer-free binary overlay body
fast-pack route
no device-resident carrier
```

The probe includes per-query preparation that the full overlay body needs:

- new LSI query handle for the distinct left/query batch;
- new left-side point-location locator for `right vertices in left map`.

The base-side point-location locator for `left vertices in right map` is reused.

## Method

Each distinct query batch is a full-size top4 County query variant:

- same coordinate domain;
- same topology size;
- tiny in-domain geometry perturbations on interior points;
- new query object;
- not same prepared-query replay.

The full body measured per query is:

```text
prepare_lsi_query
+ prepare_left_point_location
+ run_pipeline writer_free_hot_sec
```

`run_pipeline writer_free_hot_sec` includes:

```text
LSI -> reprojection -> sort -> PIP -> midpoint PIP -> carrier -> binary consumer
```

## Results

The first distinct query still pays full pipeline warmup:

| Query | Total body | Prepare LSI query | Prepare left PL | Pipeline hot | LSI phase | Downstream | Rows | Pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| query 1 | `5.638s` | `0.101s` | `0.428s` | `5.109s` | `2.857s` | `2.252s` | `428322` | `15014` |

After that, the stable distinct same-domain overlay body is:

| Query | Total body | Prepare LSI query | Prepare left PL | Pipeline hot | LSI phase | Downstream | Rows | Pairs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| query 2 | `1.470s` | `0.061s` | `0.424s` | `0.985s` | `0.117s` | `0.868s` | `428322` | `15014` |
| query 3 | `1.491s` | `0.060s` | `0.426s` | `1.005s` | `0.117s` | `0.888s` | `428322` | `15014` |

Stable median over queries 2-3:

```text
total body: ~1.48s/query
```

Compared with the current warm-process fresh fast-pack route:

```text
4.22s / 1.48s ~= 2.85x
```

Compared with the 10x target:

```text
target: ~0.42s/query
current stable body: ~1.48s/query
gap: ~3.5x above target
```

## Stable Body Breakdown

For the stable queries, the main costs are:

| Component | Query 2 | Query 3 | Meaning |
|---|---:|---:|---|
| prepare left point-location | `0.424s` | `0.426s` | per-query left-map locator build |
| vertex PIP map1 in map0 | `0.330s` | `0.340s` | right vertices queried against the distinct left map |
| reprojection | `0.197s` | `0.196s` | device-columnar reprojection |
| sort map0+map1 | `0.142s` | `0.148s` | current Numba bitonic sort |
| LSI phase | `0.117s` | `0.117s` | Goal5008 regime confirmed inside full body |
| grouped carrier | `0.095s` | `0.095s` | compiled CPU carrier |
| prepare LSI query handle | `0.061s` | `0.060s` | per-query handle setup |
| vertex PIP map0 in map1 | `0.056s` | `0.059s` | left vertices against reusable right map |
| consumer | `0.016s` | `0.016s` | descriptor pair consumer |

The decisive fact:

```text
LSI is no longer the blocker in the query-many regime.
```

The blocker has moved to point-location and downstream stages.

## Interpretation

Goal5008 was positive for LSI.  Goal5009 is more sobering for the full overlay.

What is now true:

1. Prepared-base / same-domain / distinct-query LSI exists.
2. Full overlay in that regime is faster than fresh one-shot:

```text
~4.22s -> ~1.48s
```

3. Full overlay is still not 10x:

```text
~1.48s, not ~0.42s
```

The missing performance is not hidden in LSI anymore.  It is in:

- per-query left point-location preparation;
- right-vertices-in-left PIP;
- reprojection and sort;
- remaining CPU carrier work.

## Claim Boundary

Authorized:

- prepared-base / same-domain / distinct-query LSI regime exists;
- full writer-free binary overlay body in that regime has now been measured;
- current stable full overlay body is about `~1.48s/query`;
- this is about `~2.85x` better than the `~4.22s` warm-process fresh fast-pack
  route.

Not authorized:

- no 10x claim;
- no `~0.42s` full overlay claim;
- no cold CLI one-shot claim;
- no author-performance parity claim;
- no device-resident carrier reopening;
- no broad RTDL speedup claim.

## Next Target

The next meaningful work is no longer LSI compile prewarm.  Goal5009 shows the
next targets in order:

1. **Point-location query-many design**
   - Can the left-side point-location preparation and `right vertices in left`
     query be made reusable or cheaper in a generic way?
   - Current cost: `~0.424s prepare + ~0.335s PIP`.

2. **Generic ordering primitive**
   - Current sort cost: `~0.14-0.15s`.
   - Goal5007 showed current POD lacks CuPy/CUB/Thrust bindings, so this needs
     real generic RTDL ordering infrastructure rather than app-specific code.

3. **Downstream columnar/carrier path**
   - Current carrier cost: `~0.095s`.
   - Smaller than point-location, but still visible.

The first target is the biggest: point-location in the distinct-query full
overlay body.

## Exit Label

`completed_distinct_query_many_overlay_body_measured__10x_not_reached__next_target_point_location_and_downstream`
