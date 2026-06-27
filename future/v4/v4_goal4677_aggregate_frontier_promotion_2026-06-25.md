# V4 Goal4677 Aggregate-Frontier Promotion Decision

Date: 2026-06-25

Status:

```text
goal4677_promote_aggregate_frontier_device_columns_measured_route_no_release
```

## Decision

Promote `v4_aggregate_frontier_device_columns_2d_prepared_runner` from a V4
candidate surface to a measured V4 Tier-2 operator route.

This promotion is limited to the evidence-backed route:

```text
AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D
RTDL native aggregate-frontier device columns
explicit CuPy downstream continuation
same-RT-hardware Goal4676 focused POD benchmark
```

Measured partners are:

```text
rtdl_native, cupy
```

Declared unmeasured partners remain:

```text
torch, numba
```

## Evidence

- Goal4676 result:
  `future/v4/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.md`
- Canonical Goal4676 evidence:
  `future/v4/evidence/v4_goal4676_aggregate_frontier_pod_benchmark_2026-06-25.json`
- Goal4677 validation:
  `future/v4/evidence/v4_goal4677_aggregate_frontier_promotion_2026-06-25.json`

Goal4677 validation status:

```text
passed
```

## Promotion Criteria

| Criterion | Required | Observed |
| --- | ---: | ---: |
| Goal4676 pass flag | true | true |
| all subprocesses returned zero | true | true |
| correctness companion | true | true |
| large-run checksum parity | true | true |
| host frontier materialization in V4 hot path | false | false |
| partner migration counted as speed | false | false |
| V4 frontier-only hot over V2.14 | >= 1.20x | 302.998x |
| V4 full hot over V2.14 | >= 1.20x | 310.024x |
| V4 full wall over V2.14 | >= 1.10x | 200.826x |
| V4 full hot over V3.0.2 control | >= 0.98x parity floor | 0.998x |

## Code Changes

The promotion is reflected in the machine-readable V4 front door:

- `src/rtdsl/v4_aggregate_frontier.py`
  - claim boundary now reports
    `tier2_measured_goal4677_v2_14_host_frontier_bottleneck_no_release`;
  - records Goal4676 ratios and the V3.0.2 caveat;
  - keeps release/public/broad speed claim flags false.
- `src/rtdsl/v4_operator_catalog.py`
  - moves `aggregate_frontier_device_columns_2d` from candidate catalog to measured
    Tier-2 catalog;
  - exposes it for `rtdl_native` and `cupy`;
  - keeps `torch` and `numba` unmeasured/deferred for this surface;
  - records source evidence and comparison caveat.
- `src/rtdsl/v4_scope.py`
  - updates the bounded operator scope from 8 measured surfaces and 2 candidates
    to 9 measured surfaces and 1 candidate;
  - keeps release authorization false.
- `src/rtdsl/v4_goal4677_aggregate_frontier_promotion.py`
  - validates the Goal4676 evidence before allowing promotion.
- `future/v4/README.md`
  - updates user-facing counts and the aggregate-frontier row.

## Verification

```text
py -m unittest tests.v4_goal4677_aggregate_frontier_promotion_test tests.v4_goal4675_aggregate_frontier_prepared_runner_test tests.v4_operator_catalog_test tests.v4_scope_gate_test tests.v4_frontdoor_test tests.v4_goal4676_aggregate_frontier_protocol_test
```

Result:

```text
Ran 37 tests in 2.665s
OK
```

## Important Interpretation Boundary

This promotion proves a real, focused V4 route for removing a V2.14
host-materialized aggregate-frontier bottleneck.

It does not prove:

- V4 is faster than V3.0.2 on this route.
- V4 is faster across all benchmark apps.
- the whole V4 release is high-performance.
- public speedup wording is authorized.

The V3.0.2 control is the guardrail: V4/V3.0.2 hot ratio is 0.998x because
V3.0.2 already contains the same aggregate-frontier device-column primitive
family. The honest claim is V2.14 host-frontier bottleneck removal through a
clean V4 front door.

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No. The promotion follows the frozen Goal4676 bars and records the V3.0.2 caveat
instead of hiding it.

2. If yes, what actions made it stupid?

Not applicable. The main risk was metric laundering: turning a V2.14 bottleneck
fix into a broad V4/V3 speed claim. The result explicitly forbids that.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes. Keeping the route candidate-only despite a passed serious POD gate would
have been under-using the evidence; promoting it without the caveat would have
been overclaiming. The current path is the narrow promotion.

4. Should I try a different path to solve the real problem?

Yes, the next path must move beyond this one surface: either measure/reject the
remaining ranked-summary candidate or route another app-level blocker through a
productized V4 surface. Do not re-prove aggregate-frontier unless an external
review finds a denominator flaw.

## Non-Authorization

This goal does not authorize:

- V4 release.
- public speedup wording.
- whole-app high-performance wording.
- broad V4-over-V2/V3 claims.
- V4-over-V3 speed claims for aggregate-frontier.
- RT-core speedup wording.
- true-zero-copy wording.
- Tier-3 callback/PTX support.
- raw OptiX callbacks.
- C ABI, embedding, or non-Python hosts.
- automatic partner selection.
- app-identity native kernels.

## Next Work

The next engineering goal should not reopen Goal4676 unless a reviewer rejects
the denominator. The live V4 backlog now has one remaining candidate surface:

```text
v4_fixed_radius_ranked_summary_3d_prepared_runner
```

The next useful path is to decide whether that candidate can produce material
evidence or should be explicitly rejected/deferred, then update the app-level
route map.
