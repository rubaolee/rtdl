# Goal5022: Distinct LSI Query-Batch Probe

Date: 2026-07-05

## Purpose

Goal5021 proved that a prepared LSI base session can move the top4 writer-free
route window to about `1.031s`, but the measured overlay runs still used the
same top4 query batch.  Goal5022 checks the next question directly:

> Does a prepared LSI base session amortize grouped-range workspace across
> distinct query batches in the same scale/domain?

This is an LSI-only probe, not a full overlay query-many benchmark.

## Method

On the POD, load the top4 County x Zipcode representative input.  Prepare the
right/base Zipcode planar-map LSI session once.  Split the County LSI segment
records into three disjoint contiguous query batches and run each batch as a
fresh `lsi.prepare_query(...)` object.

Artifact:

- `history/internal_docs/rtdl_goal5022_distinct_lsi_query_batches_top4.json`

Claim boundary:

- same prepared base session;
- distinct LSI query batches;
- LSI-only;
- not full overlay query-many;
- no author comparison;
- no 10x claim.

## Result

| Batch | Query segments | LSI run | LSI rows | grouped_range_ensure | scaled_cache_ensure |
|---:|---:|---:|---:|---:|---:|
| 0 | 568,342 | 2.664s | 149,354 | 1.003s | 0.640s |
| 1 | 568,342 | 0.058s | 134,508 | ~0.000001s | 0.057s |
| 2 | 568,343 | 0.051s | 144,460 | ~0.000001s | 0.049s |

## Interpretation

The first distinct batch pays compile/setup plus grouped-range/scaled-cache
work.  Later distinct batches in the same prepared base/domain do not pay
grouped-range again; their LSI cost drops to `~0.05-0.06s`.

This is not same-query replay: each batch is a different set of query segments
and each uses a fresh `prepare_query(...)` object.  It is also not yet full
overlay query-many, because downstream PIP/carrier stages were not run on those
distinct batches.

## Decision

Prepared base LSI reuse is a real lever.  The next meaningful full-system goal
is no longer generic sort/hash micro-work.  It is to lift this distinct-query
prepared-base pattern into a full overlay query-many route with real downstream
consumer semantics, or to state explicitly that v2.14.3 stops at the LSI-only
proof and `1.031s` prepared-base route.

## Exit Label

```text
completed_distinct_lsi_query_batches__prepared_base_grouped_range_reuse_proven__full_overlay_query_many_unproven
```
