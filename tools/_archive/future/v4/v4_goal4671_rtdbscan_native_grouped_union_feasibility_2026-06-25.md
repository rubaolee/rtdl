# Goal4671 RTDBSCAN Native Grouped-Union Feasibility

Date: 2026-06-25

Status: diagnostic complete; RTDBSCAN is not the second true V4 app-level win.

Decision label:

`rt_dbscan_grouped_union_no_go__pivot_required_for_second_true_v4_app_win`

## Purpose

Goal4671 was the follow-up to Goal4670. The question was narrow and falsifiable:

Can the existing generic native grouped-union trunk plausibly move RTDBSCAN from
the best observed `1.166x`/`1.163x` V4-vs-old hot-path speedup to the frozen
`1.20x` second-win bar without using app-specific DBSCAN kernels, direct-status
special contracts, or post-hoc bar lowering?

Answer: no, not with the currently available generic grouped-union levers.

## Evidence

POD:

- Host: `0256b71980f1`
- GPU: `NVIDIA RTX A5000, 570.195.03`
- Remote workspace: `/root/rtdl_v4_candidate_pod`
- Local evidence:
  `future/v4/evidence/v4_goal4671_rtdbscan_grouped_union_telemetry_20260625/summary.json`

Command shape:

```bash
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so \
  /root/rtdl_v4_venv/bin/python scripts/v4_goal4671_grouped_union_telemetry_probe.py \
  --goal Goal4671 \
  --point-counts 262144 \
  --radius 3.0 \
  --seed 20260519 \
  --profile clustered3d \
  --repeats 5 \
  --telemetry-counters 10 \
  --output future/v4/evidence/v4_goal4671_rtdbscan_grouped_union_telemetry_20260625/summary.json
```

The telemetry uses the same generic native grouped-union kernel family. It is
diagnostic only: telemetry atomics make the absolute native timings slower than
the non-telemetry app path, so these numbers are used for bottleneck structure,
not release speed claims.

## Telemetry Summary

| Variant | Median native | Candidate hits | Same-root culled | Direct hits | Reported hits | Root finds | Root link steps | Links/root | Atomic attempts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| same_root_on_direct_off | `4.009617s` | `34359607296` | `31265614560` | `0` | `3093992736` | `75985293182` | `73869489986` | `0.9722` | `539308702` |
| same_root_off_direct_off | `3.856405s` | `34359607296` | `0` | `0` | `34359607296` | `69101365174` | `77820630285` | `1.1262` | `191337434` |
| same_root_on_direct_on | `3.965580s` | `34359607296` | `31310748223` | `3048859073` | `0` | `75857144642` | `72287611000` | `0.9529` | `520368095` |
| same_root_off_direct_on | `3.822389s` | `34359607296` | `0` | `34359607296` | `0` | `69111888446` | `70391445886` | `1.0185` | `196599070` |

Interpretation:

- `same_root_off_direct_on` remains the best generic grouped-union shape, which
  matches Goal4670's app-level finding.
- Same-root culling is not a reliable win on this all-core fixture. It removes
  many union/report candidates, but the extra pre-cull root reads dominate.
- Direct side effects avoid any-hit reporting overhead and are the right generic
  direction for this shape.
- Root-find parent-link depth is already about one link per root find in the
  best variant. A path-compression or root-halving tweak is therefore not a
  credible 20% class lever here.
- The dominant remaining cost is the enormous number of candidate hits and root
  finds under the current grouped-union contract, not a shallow implementation
  oversight.

## Relation To Goal4670

Goal4670's non-telemetry app-level best true grouped-union probe was:

- direct side effect plus disabled same-root culling:
  `1.166x` vs V2.14 hot and `1.163x` vs V3.0.2 hot.

The frozen second-win bar is `>=1.20x`.

Goal4671 does not lower the bar and does not count fast direct-status rows. The
telemetry says the remaining gap is not likely to be closed by a safe generic
root-finding tweak. Repeating RTDBSCAN micro-probes would be churn.

## No-Go

RTDBSCAN should be closed as:

`no_second_true_v4_win_from_current_grouped_union_trunk`

This is not a failure of V4 as a whole. It is a stop condition for one target:
the current RTDBSCAN route is a modest generic runtime gain, not formal
high-performance V4 evidence.

Allowed future work on RTDBSCAN:

- productize direct side effect plus disabled same-root culling only as a
  bounded optimization, with no release claim by itself;
- revisit RTDBSCAN only if a new generic grouped-union algorithm changes the
  candidate/root-find count structure;
- treat direct-status routes as separate external-proof/historical routes, not
  as new V4 RT-core wins.

Forbidden:

- counting direct-status rows as V4 high-performance wins;
- adding an app-identity DBSCAN native kernel;
- lowering `1.20x` after observing the result;
- claiming whole-app high-performance V4 from this row.

## Next Action

Pivot away from RTDBSCAN for the second true V4 app-level win. The next goal
must bind to either:

- another app-level target with a plausible generic operator pushdown lever; or
- a new generic operator surface whose app mapping and old-version denominators
  are frozen before measurement.

The next target must not be a parity-only cleanup goal.

## Goal-Level Decision Audit

1. Did I do something stupid?

No for this decision. Stopping RTDBSCAN after the telemetry is the non-stupid
move. Continuing to polish a `1.166x` route as if it would become formal V4
evidence would be stupid.

2. If yes, what actions made the decision stupid?

The stupid actions would be: treating direct-status rows as true V4 wins,
pretending path compression is a proven lever despite `~1` link per root find,
or lowering the second-win bar after the run.

3. Is there another possible path that avoids being stuck on this idea?

Yes. Stop this target and select a different app-level target or generic
operator pushdown where the denominator, parity gate, and numeric bar are frozen
before the run.

4. Can I start a different path that actually solves the problem?

Yes. The correct path is to pivot to the next app-level candidate for a second
independent true V4 win, while keeping RTDBSCAN as a bounded modest-gain route.

## Non-Authorization

This goal does not authorize:

- V4 release;
- formal high-performance V4 wording;
- broad app-level speedup wording;
- RTDBSCAN speedup claims;
- direct-status rows as V4 wins;
- app-specific DBSCAN kernels;
- automatic partner selection;
- true-zero-copy, C ABI, embedding, or non-Python host claims.
