# V4 Goal4680 Shape-Pair Relation Protocol Gate

Date: 2026-06-25

Status:

```text
goal4680_shape_pair_relation_local_static_frontdoor_protocol_passed_not_pod_run
```

## Decision

Create the local/static V4 frontdoor and protocol gate for:

```text
v4_shape_pair_relation_active_count_2d_prepared_left_executor
```

Generic primitive:

```text
SHAPE_PAIR_RELATION_ACTIVE_COUNT_2D_PREPARED_LEFT_EXECUTOR
```

This is a V4 engineering target only. It is not added to the measured operator
catalog and is not advertised as an open candidate surface.

## What Was Added

- `src/rtdsl/v4_shape_pair_relation.py`
  - V4 wrapper over the existing app-agnostic prepared-left executor ABI.
  - claim boundary blocks release wording, POD wording, broad speed wording, app
    identity kernels, and partner-migration-as-speed.
  - fake-runner tests verify runtime metadata and reject hot-path row-stream
    materialization.
- `src/rtdsl/v4_goal4680_shape_pair_relation_protocol.py`
  - frozen same-primitive focused benchmark protocol for the next POD run.
  - strongest V2.14 denominator is required.
  - no silent fallback to weaker CPU/Numba/all-CuPy route is allowed.

## Denominator Lock

The V2.14 denominator for the next focused run is:

```text
prepared_optix_shape_pair_active_count_device_continuation_reuse
```

This is the strongest same-primitive V2.14 route when present. If the checked
V2.14 tree cannot run that route, the benchmark must fail or be reclassified.
It must not silently fall back to a weaker route.

## Frozen Bars

| Gate | Required value |
| --- | ---: |
| correctness parity | required |
| V4/V2.14 same-primitive hot ratio | >= 1.20x |
| V4/V2.14 same-primitive wall ratio | >= 1.10x |
| V4/V3.0.2 hot parity floor | >= 0.98x |
| hot-path row-stream materialization | forbidden |
| partner migration counted as speed | false |
| app-identity kernel allowed | false |

If the next POD run misses these bars, the work may still count as V4 route
coverage/productization, but not as formal V4 speed evidence.

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No. I did not run POD before freezing the same-primitive denominator and the
bars.

2. If yes, what actions made it stupid?

Not applicable. The avoided stupid action was turning a historical V2.14
primitive into a V4 speed claim before measuring V4 against V2.14.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes. Keep the wrapper out of the public catalog, freeze protocol first, and run
only a focused POD benchmark next.

4. Should I try a different path to solve the real problem?

Yes. Goal4681 should implement and run the focused POD benchmark. If the
strongest V2.14 denominator is unavailable, stop and reclassify instead of
accepting a weaker denominator.

## Non-Authorization

This goal does not authorize:

- V4 release.
- public speedup wording.
- whole-app high-performance wording.
- broad V4-over-V2/V3 claims.
- app-identity native kernels.
- raw RayJoin native kernels.
- partner migration as speed evidence.
- Tier-3 callbacks.
- C ABI, embedding, or non-Python hosts.

This goal also does not itself authorize a completed POD result. It creates the
gate that makes Goal4681 a legitimate focused POD benchmark goal.

## Verification

Local verification command:

```text
py -m unittest tests.v4_goal4680_shape_pair_relation_protocol_test tests.v4_goal4679_relation_topology_target_test tests.v4_goal4678_ranked_summary_disposition_test tests.v4_goal4677_aggregate_frontier_promotion_test tests.v4_operator_catalog_test tests.v4_scope_gate_test
```

Result:

```text
Ran 39 tests in 1.216s
OK
```

## Next Work

Goal4681: implement and run
`scripts/v4_goal4681_shape_pair_relation_pod_benchmark.py` on the current POD.
The run must produce v2.14, v3.0.2, and v4_current rows, raw subprocess logs,
and a summary JSON with same-primitive ratios and pass/fail flags.
