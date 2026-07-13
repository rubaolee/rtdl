# Goal4983 Result: LSI Prepare/Warm Strategy Decision For v2.14.3

Date: 2026-07-04

## Verdict

```text
warmup_not_product_strategy_keep_fresh_lsi_headline
```

Goal4983 decides the v2.14.3 product/benchmark treatment of the LSI producer setup cost exposed by Goal4982.

Decision:

> v2.14.3 must keep the `~2.7s` LSI producer cost in the fresh writer-free binary operator headline. A warm/prepared LSI number is not authorized as the primary result.

## Why

Goal4982 measured LSI and grouped carrier symmetrically on the top4 representative writer-free binary route.

The repeated full-route evidence is:

| Run | Hot body sec | LSI producer sec | Downstream sec | Carrier sec |
|---|---:|---:|---:|---:|
| diagnostic run | 3.668801 | 2.692300 | 0.972703 | 0.111014 |
| repeat 1 | 3.670935 | 2.763328 | 0.904126 | 0.105219 |
| repeat 2 | 3.620381 | 2.706508 | 0.910247 | 0.104357 |

The carrier side-builder first-large-call cost is no longer a stable route floor in these runs. It is about `0.10-0.11s` once warm.

The LSI producer is different. It remains about `2.69-2.76s` in repeated full-route runs.

## Invalid Evidence Rejected

Goal4982 also produced an LSI repeat diagnostic with:

```text
repeat wall_sec=0.000000
repeat native_sec=0.000000
rows=428322
```

This is rejected as product/benchmark evidence.

It may be replaying cached metadata/results, or timing the wrong code path. It does not prove that LSI production is a real `0s` warm route.

## Product Strategy

### Fresh one-shot overlay

For one-shot overlay:

```text
LSI producer cost stays in the headline.
```

The current top4 fresh writer-free binary route is therefore approximately:

```text
hot body:      3.62-3.67s
LSI producer:  2.69-2.76s
downstream:    0.90-0.97s
```

### Prepare-once/query-many

v2.14.3 may describe prepare-once/query-many as a future or diagnostic possibility only if the same prepared LSI workspace serves repeated real queries.

Current evidence does not prove that route as a product claim.

Therefore:

- no warm-only v2.14.3 headline;
- no removal of `~2.7s` LSI from fresh;
- no comparison of an amortized LSI replay number against an author's fresh overlay computation.

## Allowed Claims

Authorized:

- v2.14.3 writer-free binary route is faster than the earlier text/writer-bound route;
- Goal4977-4982 moved the downstream floor substantially;
- current top4 fresh route is still dominated by LSI producer setup/ensure work;
- carrier first-large-call warmup is not the main remaining bottleneck;
- future work should target real LSI producer preparation/reuse only after it is validated as product behavior.

Not authorized:

- no author-speed or author-parity claim;
- no `0.000s` LSI claim;
- no warm-only headline;
- no claim that v2.14.3 has solved exact LSI producer cost;
- no claim that a prepared replay is equivalent to a fresh overlay computation.

## Impact On v2.14.3 Closeout

Goal4984/4985 must use this policy:

1. fresh and warm/diagnostic numbers must always be shown side by side;
2. the primary result is fresh one-shot unless a real prepare-once/query-many use case is explicitly measured and named;
3. if no valid product warm route exists, fresh keeps the `~2.7s` LSI producer.

## Next Step

Proceed to the correctness/regression and genericity gate before producing the final v2.14.3 performance matrix.

Required for the next goal:

- local tests for the v2.14.3 route and new helpers;
- non-RayJoin genericity smoke;
- no performance matrix on an unverified build.
