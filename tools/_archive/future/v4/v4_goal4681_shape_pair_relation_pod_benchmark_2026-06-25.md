# V4 Goal4681 Shape-Pair Relation Focused POD Benchmark

Date: 2026-06-25

Status:

```text
goal4681_correct_same_primitive_but_no_speed_credit_do_not_promote
```

## Bottom Line

Goal4681 did not produce V4 speed credit.

The focused same-primitive shape-pair relation benchmark ran correctly on the
RTX A5000 POD. V2.14, V3.0.2, and V4 current all returned the same serious
active count, and the V4 route did not materialize the row stream on the hot
path. But V4 did not beat the strongest V2.14 denominator:

| Metric | Result |
| --- | ---: |
| V4/V2.14 hot ratio | 0.963x |
| V4/V2.14 wall ratio | 0.605x |
| V4/V3.0.2 hot ratio | 0.977x |

Required bars were `>=1.20x` hot over V2.14, `>=1.10x` wall over V2.14, and
`>=0.98x` hot parity floor over V3.0.2. This route failed all three performance
bars.

## Evidence

Local evidence directory:

```text
future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/
```

Canonical summary:

```text
future/v4/evidence/v4_goal4681_shape_pair_serious_2026-06-25/summary.json
```

POD source directory:

```text
/root/rtdl_v4_candidate_pod/future/v4/evidence/v4_goal4681_shape_pair_serious_20260625_021946
```

Hardware:

```text
NVIDIA RTX A5000, driver 570.195.03
```

Dataset:

```text
generated 64x64 square-grid CDB pair, 4096 shapes per side
```

This is a generated focused same-primitive benchmark input. It is not RayJoin
paper input and does not authorize paper/app-level claims.

## Serious Metrics

| Version | Active Count | Hot Seconds | Wall Seconds |
| --- | ---: | ---: | ---: |
| V2.14 | 16129 | 0.0006163493 | 0.0023321919 |
| V3.0.2 | 16129 | 0.0006251819 | 0.0010750704 |
| V4 current | 16129 | 0.0006399006 | 0.0038555562 |

Pass/fail flags:

| Gate | Result |
| --- | --- |
| all subprocesses returned zero | pass |
| correctness companion | pass |
| serious active-count parity | pass |
| V4 hot-path row-stream materialization | false |
| V4 hot bar over V2.14 | fail |
| V4 wall bar over V2.14 | fail |
| V4 hot parity floor over V3.0.2 | fail |

## Interpretation

This result is useful, but not in the hoped-for direction.

It proves that the V4 wrapper can execute the same generic prepared-left
shape-pair active-count primitive correctly. It also proves that this route is
not a material V4 performance lever against V2.14. V2.14 already had the
prepared-left executor route, so V4 is mostly productizing and refacing an
existing primitive, not creating a faster execution path.

Therefore the route must not be promoted into the measured V4 catalog as speed
evidence. It may remain an internal/productization path or future coverage item.

## Code And Tests

Added:

- `scripts/v4_goal4681_shape_pair_relation_pod_benchmark.py`
- `src/rtdsl/v4_goal4681_shape_pair_relation_result.py`
- `tests/v4_goal4681_shape_pair_benchmark_script_test.py`
- `tests/v4_goal4681_shape_pair_result_test.py`

Validation:

```text
py -m unittest tests.v4_goal4681_shape_pair_result_test tests.v4_goal4681_shape_pair_benchmark_script_test tests.v4_goal4680_shape_pair_relation_protocol_test tests.v4_goal4679_relation_topology_target_test tests.v4_operator_catalog_test tests.v4_scope_gate_test
```

Result:

```text
Ran 34 tests in 1.105s
OK
```

## Goal-Level Decision Audit

1. Did I make a stupid decision?

No on the final experiment. There was a near-miss: the original script assumed
public CDB slices existed on the POD. When they did not, I did not substitute the
tiny fixture as serious evidence.

2. If yes, what actions made it stupid?

The risky action would have been accepting tiny fixture data or a weak fallback
denominator. I avoided it by generating a documented 4096-shape focused input
and keeping the same-primitive V2.14 denominator.

3. Was there another path that avoided getting stuck on a stupid idea?

Yes. Treat this as a falsifiable route probe. Once it failed the speed bars,
record it as no speed credit instead of polishing or rebranding it.

4. Should I try a different path to solve the real problem?

Yes. Goal4682 should close this route as no-promotion and select the next target
only if it can plausibly introduce a runtime lever absent from V2.14, not just a
V4 wrapper around a V2.14 primitive.

## Non-Authorization

This goal does not authorize:

- V4 release.
- measured-catalog promotion for this route.
- public speedup wording.
- whole-app high-performance wording.
- broad V4-over-V2/V3 claims.
- RayJoin paper reproduction claims.
- app-identity native kernels.
- partner migration as speed evidence.
- Tier-3 callbacks, C ABI, embedding, or non-Python hosts.

## Next Work

Goal4682: disposition and next-target selection after the shape-pair relation
no-speed result. The next target must not be another wrapper around a V2.14
same primitive unless it has a concrete material-improvement hypothesis before
POD spend.
