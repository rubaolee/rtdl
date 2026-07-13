# Goal5008: Distinct-Query Prepared-Base LSI Regime Result

Date: 2026-07-05

## Verdict

`completed_lsi_distinct_same_domain_query_many_regime_demonstrated__overlay_query_many_still_unproven`

Goal5008 executes P2 from the owner directive: prove or reject the
prepared-base / same-domain / distinct-query regime before any 10x claim.

The result is positive for **LSI only**:

```text
one prepared right/base + one established scale-domain workspace
serves three distinct same-domain full-size query batches at ~0.117s/query
```

This is not same-input replay.  Each measured query uses a new query handle and
a distinct query input.

This does **not** yet prove full overlay 10x.  It proves that the LSI part of
the target regime exists.

## Artifacts

POD:

```text
root@157.157.221.29 -p 25248
repo: /root/rtdl_goal4988
```

Probe:

```text
history/internal_docs/goal5008_distinct_query_many_lsi_probe.py
```

POD artifact copied locally:

```text
history/internal_docs/goal5008_distinct_query_many_lsi_artifacts_2026-07-05/rtdl_goal5008_distinct_query_many_lsi.json
history/internal_docs/goal5008_distinct_query_many_lsi_artifacts_2026-07-05/rtdl_goal5008_distinct_query_many_lsi.log
```

## Method

The probe uses the public generic LSI route:

```text
prepare_planar_map_lsi_2d_optix(right.lsi_segments)
lsi.prepare_query(query_segments)
query.run_bounded_pair_id_device_columns(max_rows=1000000)
```

It first runs a tiny generic LSI prewarm to remove global compile noise.

Then it loads top4 County x Zipcode:

```text
left_lsi_segments  = 1,705,027
right_lsi_segments = 9,982,960
capacity           = 1,000,000
```

The query sequence is:

1. `domain_seed_full_query`: full top4 County query, used to establish the
   base/query scale-domain workspace.
2. `distinct_same_domain_query_1`: new query handle, full-size query with
   shifted segment IDs and tiny in-domain perturbations.
3. `distinct_same_domain_query_2`: another distinct same-domain query.
4. `distinct_same_domain_query_3`: another distinct same-domain query.
5. `distinct_far_domain_query`: one far-domain query to verify workspace rebuild.

The three same-domain batches keep the same coordinate domain but are not the
same prepared query replay.

## Results

| Query | Meaning | Rows | Elapsed | Scaled cache ensure | Grouped range ensure | OptiX launch |
|---|---|---:|---:|---:|---:|---:|
| `domain_seed_full_query` | first full query builds scale-domain workspace | `428322` | `1.658s` | `0.687s` | `0.967s` | `0.00218s` |
| `distinct_same_domain_query_1` | new distinct query, same domain | `428322` | `0.1172s` | `0.1135s` | `0.000001s` | `0.00219s` |
| `distinct_same_domain_query_2` | new distinct query, same domain | `428322` | `0.1178s` | `0.1141s` | `0.000001s` | `0.00220s` |
| `distinct_same_domain_query_3` | new distinct query, same domain | `428322` | `0.1176s` | `0.1140s` | `0.000001s` | `0.00219s` |
| `distinct_far_domain_query` | changed scale domain | `0` | `1.484s` | `0.615s` | `0.867s` | `0.00009s` |

The prepared right/base itself took:

```text
prepare_right_base_sec = 1.263s
```

## Interpretation

This closes the specific uncertainty from the owner directive.

### What Is Proven

The LSI query-many regime is real:

```text
prepared base + same scale-domain + distinct query batches
```

After one seed query establishes the scale-domain workspace, subsequent
distinct same-domain query batches run at:

```text
~0.117s LSI/query
```

The expensive right-side grouped range ensure stays reused:

```text
grouped_range_ensure ~= 0.000001s
```

The remaining per-query LSI cost is the left/query scaled cache:

```text
scaled_cache_ensure ~= 0.114s/query
```

The far-domain query confirms the boundary:

```text
changed scale domain -> 1.484s
```

So the previous Goal5003 warning remains correct: this regime exists only when
the query stays in the same scale domain.

### What Is Not Proven

This is not yet a full overlay 10x result.

It does not measure:

- reprojection;
- sort;
- PIP;
- midpoint PIP;
- carrier/group construction;
- downstream consumer;
- paper text writer.

It also does not prove:

- cold CLI one-shot speedup;
- distinct-domain fresh speedup;
- author-performance parity;
- device-resident carrier payoff.

## Claim Boundary

Authorized:

- `query-many` wording is now authorized **for LSI only**, and only with the
  qualifier:

```text
prepared base / same scale-domain / distinct query batches
```

- The current measured LSI body in that regime is about:

```text
~0.117s/query on top4 County x Zipcode-sized query batches
```

Not authorized:

- no full overlay query-many claim yet;
- no 10x claim yet;
- no fresh one-shot claim;
- no device-resident reopening;
- no author-ratio claim.

## Next Goal

Proceed to Goal5009:

```text
prepared-base same-domain distinct-query writer-free binary overlay body
```

Goal5009 should extend the current app/probe so that the same three distinct
query batches are measured through the full writer-free binary overlay body:

```text
LSI -> reprojection -> sort -> PIP -> midpoint PIP -> carrier -> binary consumer
```

The required output is a per-query table:

```text
query_id | LSI | downstream | total writer-free body | rows | descriptor pairs
```

Only if the total body approaches the `~0.42s` target may the 10x claim be
considered.  If total body remains near `~0.117s + ~0.33s ~= ~0.45s`, that is
close and useful.  If it is materially higher, the bottleneck must be named.

## Exit Label

`completed_lsi_distinct_same_domain_query_many_regime_demonstrated__overlay_query_many_still_unproven`
