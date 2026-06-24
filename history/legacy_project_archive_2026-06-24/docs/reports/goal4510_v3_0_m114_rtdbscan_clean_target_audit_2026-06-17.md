# Goal4510 / V3 M114 RT-DBSCAN Clean-Target Audit

## Conclusion

RT-DBSCAN is closed as an internal V3 clean target under an evidence-bounded compact-signature contract: predicate direct-status plus CuPy wins all 524k/1M same-contract rows, Numba remains the reference/no-C++ fallback, and 2M point-column reuse is useful only when the caller already owns device coordinate columns. M113 is reusable infrastructure, but it is not the current RT-DBSCAN performance path.

## Compact-Signature Winner Matrix

| Points | Dataset | Protocol | Metric | Winner | Predicate direct-status | Speedup vs grouped Numba | Speedup vs grouped CuPy |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: |
| 524,288 | clustered3d | one_shot_no_warmup | `prepare_plus_replay_sec` | `predicate_direct_status` | 4.321s | 1.76x | 1.85x |
| 524,288 | clustered3d | warmed_replay | `elapsed_sec` | `predicate_direct_status` | 1.553s | 3.26x | 3.44x |
| 524,288 | road3d | one_shot_no_warmup | `prepare_plus_replay_sec` | `predicate_direct_status` | 3.882s | 1.14x | 1.22x |
| 524,288 | road3d | warmed_replay | `elapsed_sec` | `predicate_direct_status` | 1.326s | 1.39x | 1.59x |
| 524,288 | ngsim_dense | one_shot_no_warmup | `prepare_plus_replay_sec` | `predicate_direct_status` | 3.119s | 1.01x | 1.09x |
| 524,288 | ngsim_dense | warmed_replay | `elapsed_sec` | `predicate_direct_status` | 0.337s | 1.78x | 2.58x |
| 1,048,576 | clustered3d | one_shot_no_warmup | `prepare_plus_replay_sec` | `predicate_direct_status` | 11.362s | 2.35x | 2.27x |
| 1,048,576 | clustered3d | warmed_replay | `elapsed_sec` | `predicate_direct_status` | 5.773s | 3.42x | 3.52x |
| 1,048,576 | road3d | one_shot_no_warmup | `prepare_plus_replay_sec` | `predicate_direct_status` | 10.425s | 1.18x | 1.23x |
| 1,048,576 | road3d | warmed_replay | `elapsed_sec` | `predicate_direct_status` | 5.254s | 1.39x | 1.49x |
| 1,048,576 | ngsim_dense | one_shot_no_warmup | `prepare_plus_replay_sec` | `predicate_direct_status` | 6.509s | 1.14x | 1.21x |
| 1,048,576 | ngsim_dense | warmed_replay | `elapsed_sec` | `predicate_direct_status` | 1.243s | 1.80x | 2.23x |

## 2M Point-Column Boundary

| Dataset | Scope | Caller-owned-column speedup | Charged app-total result | Decision |
| --- | --- | ---: | --- | --- |
| road3d | full count-threshold app route | 45.90x prepare | one-shot 1.02x, warm 1.00x | `reuse_columns_only` |
| clustered3d | isolated direct-status prepare only | 127.93x prepare | not full app-total evidence | `reuse only if caller owns columns` |
| ngsim_dense | isolated direct-status prepare only | 82.07x prepare | not full app-total evidence | `reuse only if caller owns columns` |

The point-column optimization is real but narrow: it removes redundant coordinate extraction/upload when the caller already owns device `x/y/z` columns. If the app constructs temporary columns solely for this route, that construction cost is charged and the app-total result is effectively flat on the measured 2M `road3d` row.

## M113 Applicability

- Current route should use M113: `False`.
- Reason: The current winning RT-DBSCAN compact-signature route is not a prepared graph chunk plus same-stream partner-reduction route. It is a prepared self-query count-threshold status producer followed by a direct-status CuPy component-signature continuation.
- Future use: Use plan_v3_prepared_graph_chunk_executor only if a future RT-DBSCAN contract genuinely needs bounded prepared chunks, per-chunk handles, and explicit partner continuation before host materialization.

## Closed

- Predicate direct-status plus CuPy is the measured best compact-signature route on all 524k/1M same-contract rows.
- Numba remains a same-contract grouped-stream fallback/reference and no-C++ partner path.
- Full Python rows remain an explicit slower output contract, not the default compact-summary route.
- Caller-owned coordinate-column reuse is validated at 2M scale, with the charged-column boundary documented.

## Still Blocked

- Exact RT-DBSCAN paper reproduction and paper-level speedup wording.
- Public broad DBSCAN acceleration wording.
- Hidden automatic partner or output-contract selection.
- Treating M113 as the current RT-DBSCAN performance path.
