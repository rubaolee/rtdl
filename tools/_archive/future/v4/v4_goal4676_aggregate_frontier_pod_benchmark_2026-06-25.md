# V4 Goal4676 Aggregate-Frontier Focused POD Benchmark

Date: 2026-06-25

Status:

```text
goal4676_pass_true_v4_aggregate_frontier_candidate__continue_goal4677_candidate_decision__no_release_authorization
```

## Purpose

Goal4676 tested one named V2.14 bottleneck with a frozen, serious POD protocol:
Barnes-Hut aggregate-frontier traversal plus weighted-vector continuation.

The question was not "is V4 globally faster than V2/V3?" The question was:

```text
Can the V4 aggregate-frontier device-column front door remove the V2.14
host-materialized frontier hot path on the same logical workload, same RT
hardware, and same explicit partner continuation?
```

## Evidence Files

- Protocol: `future/v4/v4_goal4676_aggregate_frontier_protocol_freeze_2026-06-25.md`
- Canonical summary: `future/v4/evidence/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.json`
- Raw evidence directory: `future/v4/evidence/v4_goal4676_serious_2026-06-25/`
- Script: `scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py`
- Protocol module: `src/rtdsl/v4_goal4676_aggregate_frontier_protocol.py`
- Runner surface: `src/rtdsl/v4_aggregate_frontier.py`

## POD Run

POD:

```text
root@194.68.245.170 -p 22089
```

Workspace:

```text
/root/rtdl_v4_candidate_pod
```

Command:

```text
/root/rtdl_v4_venv/bin/python scripts/v4_goal4676_aggregate_frontier_pod_benchmark.py --profile serious --partner cupy --out-dir future/v4/evidence/v4_goal4676_serious_2026-06-25
```

Main serious run shape:

| Field | Value |
| --- | ---: |
| body_count | 32768 |
| theta | 0.5 |
| bucket_size | 32 |
| max_depth | 32 |
| repeat | 7 |
| warmup | 2 |
| frontier_capacity_multiplier | 700 |
| explicit partner | cupy for V3/V4 device continuation; V2.14 denominator uses host-materialized frontier plus CPU Numba continuation |

The profile also ran a smaller correctness companion at body_count 2048.

## Pass/Fail

| Gate | Result |
| --- | --- |
| all subprocesses returned zero | pass |
| correctness companion | pass |
| large-run checksum parity | pass |
| V4 host frontier materialization in hot path | false |
| partner migration counted as speed | false |
| V4 frontier-only hot bar over V2.14 >= 1.20x | pass |
| V4 full hot bar over V2.14 >= 1.20x | pass |
| V4 full wall bar over V2.14 >= 1.10x | pass |

## Ratios

| Ratio | Value |
| --- | ---: |
| V4 frontier-only hot over V2.14 | 302.998x |
| V4 full hot over V2.14 | 310.024x |
| V4 full wall over V2.14 | 200.826x |
| V4 full hot over V3.0.2 control | 0.998x |

## Median Timings

| Route | Median Hot Seconds | Median Wall Seconds | Notes |
| --- | ---: | ---: | --- |
| V2.14 OptiX host frontier + host/Numba continuation | 34.792420 | 34.792420 | `host_frontier_materialization_in_hot_path: true` |
| V3.0.2 device columns + explicit partner continuation | 0.111952 | 0.194823 | V3.0.2 already has this primitive family |
| V4 candidate runner + explicit partner continuation | 0.112225 | 0.173246 | `host_frontier_materialization_in_hot_path: false` |

## Correctness

The serious run used checksum parity across the same logical frontier and weighted-vector output:

| Route | force_x | force_y |
| --- | ---: | ---: |
| V2.14 | -4733.575645891911 | 46717.65234663441 |
| V3.0.2 | -4733.575645891676 | 46717.6523466357 |
| V4 current | -4733.575645893308 | 46717.65234663877 |

The correctness companion also passed at body_count 2048.

## Interpretation

This is a real focused V4 candidate result against V2.14 because the measured
V2.14 denominator includes the bottleneck that V4 is designed to remove:
host-materialized aggregate-frontier rows plus a host continuation boundary.

This is not a broad V4-over-V3 performance win. V3.0.2 already contains the
same aggregate-frontier device-column primitive family, so V4 and V3.0.2 are
expected to be close here. The measured V4/V3.0.2 hot ratio is 0.998x, which is
parity/slight regression, not a V4 speedup claim.

The useful conclusion is narrower and stronger:

```text
V4 has a productized front door for a device-resident aggregate-frontier route
that removes a serious V2.14 host-frontier bottleneck on this workload.
```

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No on this goal. The work stayed on a named blocker and used a frozen POD
protocol before accepting the result.

2. If yes, what actions made it stupid?

Not applicable. The avoided failure mode was overclaiming this as a whole-app
or V4-over-V3 win. The report records the V3 parity caveat explicitly.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes: stop at the focused evidence boundary and continue to a candidate
promotion/no-go decision instead of trying to turn one focused result into a
release headline.

4. Should I try a different path to solve the real problem?

Yes, after Goal4677. If this candidate is promoted, the next real work is to
route additional benchmark-app surfaces through the same kind of productized
front door and then run a frozen all-app gate. If this candidate is not
promoted, do not keep polishing this line.

## Claim Boundary

This result does not authorize:

- V4 release.
- public speedup wording.
- whole-app high-performance wording.
- broad V4-over-V2/V3 claims.
- RT-core speedup wording.
- true-zero-copy wording.
- automatic partner selection.
- Tier-3 callback/PTX support.
- raw OptiX callbacks.
- C ABI, embedding, or non-Python hosts.
- app-identity native kernels.

## Next Authorized Goal

Goal4677 should decide whether this result promotes
`AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D` from candidate to measured V4 route, or
keeps it as candidate-only pending additional review.

Goal4677 must preserve the V3 caveat and must not authorize release.
