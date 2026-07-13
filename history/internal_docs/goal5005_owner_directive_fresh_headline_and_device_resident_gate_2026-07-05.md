# Goal5005 Owner Directive Compliance: Fresh Headline And Device-Resident Gate

Date: 2026-07-05

## Verdict

`device_resident_payoff_not_demonstrated_stop_track_for_v2_14_3`

The owner/Claude directive is accepted and enforced:

- The v2.14.3 performance headline must use the faster long-lived-process fresh fast-pack route, not the slower device-resident-carrier route.
- Device-resident carrier remains an experimental architecture track behind an explicit flag.
- No further v2.14.3 device-resident performance work is authorized until a real payoff regime is demonstrated.

## Why This Goal Was Needed

Goal4998/Goal4999 correctly removed host boundaries in the device-resident route, but Goal5004 exposed a serious framing problem: the corrected device-resident fresh route was slower than the earlier fast-pack route on the same top4 County x Zipcode representative input.

The required question was not "did we remove a boundary?" It was:

> Did the device-resident route improve a product-relevant regime enough to justify being the v2.14.3 performance route?

The answer is no.

## Inputs And Artifacts

POD:

- `root@157.157.221.29 -p 25248`
- repo: `/root/rtdl_goal4988`

Representative input:

- `Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_county.cdb`
- `Paper-reproduction-apps/rayjoin-paper/_data/top4_arcgis/top4_zipcode.cdb`

Local artifacts:

- `history/internal_docs/goal5005_owner_directive_artifacts_2026-07-05/`
- measurement script: `history/internal_docs/goal5005_owner_directive_measurement.py`

Structural anchors were stable across the measured routes:

- LSI rows: `428322`
- descriptor pairs: `15014`

## Regime Definitions

This report separates four regimes that were previously easy to mix:

1. **OS-process-cold independent process**: each run starts a new Python process. This includes Numba/CUDA/OptiX first-call effects and is highly variable.
2. **Long-lived-process fresh one-shot**: one overlay computation in a process where the app/runtime is already alive. This is the previously used v2.14.3 fresh operator regime.
3. **Prepared replay diagnostic**: same input replayed in the same prepared operator session. This is diagnostic only, not a fresh overlay result.
4. **True query-many**: one prepared base serving distinct query batches. This was not demonstrated.

## Action 1: Fresh Headline Must Be Fast-Pack, Not Device-Resident

Existing long-lived-process fresh evidence:

| Route | Source | Writer-free top4 time | Status |
|---|---:|---:|---|
| Fast-pack, no device-resident carrier | Goal4985 / Goal4977 line | `~4.220s` | v2.14.3 headline route |
| Device-resident carrier, corrected accounting | Goal5004 | `~5.004s` | experimental, slower in fresh |

Same input, same structural anchors. The device-resident route is about `+0.78s` slower in this regime.

Therefore the v2.14.3 public/headline performance route must be:

> fast-pack writer-free binary route, `~4.22s` on top4 County x Zipcode.

The device-resident-carrier route must be described as:

> experimental architecture track; currently slower for fresh one-shot; payoff not demonstrated.

## Action 2: Accounting Delta And False Precision

The midpoint device-query accounting fix added previously omitted keys:

- `midpoint_points_map0_device_query_points_sec`
- `midpoint_points_map1_device_query_points_sec`

Same-artifact old-key vs corrected-key recomputation shows:

| Regime | Accounting delta |
|---|---:|
| Device-resident fresh independent process | median `0.129s`, range `0.123-0.152s` |
| Prepared replay diagnostic | median `0.003s` |

So the earlier cross-run movement from `4.816s` to `5.004s` must not be attributed wholly to the accounting fix. The true fresh accounting correction is about `0.13s`; the remaining difference is run-to-run variance and regime noise.

The corrected reporting rule is:

- do not report microsecond-style precision such as `5.003915s`;
- report rounded values with regime and run-count context, for example `~5.0s single long-lived-process fresh run` or `median 11.6s over 5 independent cold processes`.

## Action 3: Re-Audit Device-Route Numbers With Corrected Accounting

Independent OS-process-cold runs:

| Route | Runs | Median | Min | Max | Median LSI | Median downstream |
|---|---:|---:|---:|---:|---:|---:|
| Fast-pack | 5 | `11.714s` | `5.912s` | `33.226s` | `2.957s` | `8.815s` |
| Device-resident carrier | 5 | `11.565s` | `8.117s` | `24.059s` | `2.880s` | `8.808s` |

This is not a useful product headline for either route, but it proves a stronger point: the routes are dominated by unstable first-call effects in a new Python process. Device-resident carrier does not demonstrate a fresh payoff.

Prepared replay diagnostic after corrected accounting:

| Metric | Value |
|---|---:|
| median writer-free hot | `0.918s` |
| best writer-free hot | `0.324s` |
| worst writer-free hot | `23.182s` |
| median LSI phase | `0.003s` |
| median downstream | `0.915s` |

The best replay number is still real as a same-input replay diagnostic, but it is not product evidence for fresh overlay or true query-many. It remains disallowed as a headline.

Compile-prewarm probe after corrected route:

- tiny generic prewarm elapsed: `1.249s`
- route elapsed: `50.095s`
- route writer-free hot: `24.741s`
- route LSI phase: `1.879s`

The prewarm still removes exact/split compile ensure work, but the full route remains dominated by other cold effects. It does not rescue the device-resident route as a v2.14.3 performance path.

## Action 4: Device-Resident Payoff Gate

The device-resident route did not demonstrate either required payoff:

- no distinct-input true query-many workload was measured;
- no real downstream device operator showed end-to-end win over the fast-pack route.

Therefore:

`device_resident_payoff_not_demonstrated_stop_track_for_v2_14_3`

Rules for v2.14.3 closeout:

- keep device-resident code behind explicit flags;
- keep it as experimental architecture evidence only;
- do not spend further v2.14.3 goals optimizing it;
- do not use `query-many` wording for same-input prepared replay;
- do not present the `0.324-0.918s` replay results as fresh performance.

## Corrected v2.14.3 Performance State

The honest v2.14.3 status is:

| Route | Product status | Top4 result |
|---|---|---:|
| Fast-pack writer-free binary route | primary v2.14.3 route | `~4.22s` long-lived-process fresh |
| Device-resident carrier route | experimental; payoff not demonstrated | `~5.0s` long-lived-process fresh, slower |
| Independent OS-process-cold runs | diagnostic only | both routes around `~11.6-11.7s` median, high variance |
| Prepared same-input replay | diagnostic only | median `0.918s`, best `0.324s`, not fresh |

## Non-Authorization

This goal does not authorize:

- author-performance parity claims;
- top4 author ratio claims;
- warm-only/replay headline claims;
- true query-many claims;
- broad RTDL speedup claims;
- calling the current device-resident route the v2.14.3 performance route.

## Next Step

Proceed to v2.14.3 documentation/closeout only after replacing the performance framing:

- headline fast-pack `~4.22s`;
- device-resident experimental and currently slower;
- prepared replay diagnostic only;
- no further device-resident performance goals in v2.14.3 unless a new owner decision reopens it with a real payoff workload.
