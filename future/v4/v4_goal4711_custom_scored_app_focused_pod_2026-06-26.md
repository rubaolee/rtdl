# V4 Goal4711 Custom Scored App Focused POD Result

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `fail_focused_app_gate_not_high_performance`

## Goal

Run the frozen Goal4710 focused app-level benchmark for:

`ray_triangle_custom_scored_accumulation`

The test asks whether V4's constrained specialized Numba scalar callback in an
RTDL-generated OptiX hit program produces a material V4-over-V2/V3 app-level
win on a custom-callback workload.

## Evidence

- JSON: `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.json`
- Markdown: `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.md`
- POD stdout log: `future/v4/evidence/v4_goal4711_custom_scored_app_pod_2026-06-26.stdout.log`
- Source: `src/rtdsl/v4_goal4711_custom_scored_app_result.py`
- Script: `scripts/v4_goal4711_custom_scored_app_pod.py`
- Tests: `tests/v4_goal4711_custom_scored_app_result_test.py`

POD:

- Host: `root@194.68.245.170 -p 22089`
- Workspace: `/root/rtdl_v4_candidate_pod`
- Python: `/usr/bin/python3`

## Denominator

Denominator discovery was completed before V4 timing.

- V2.14 root: `/root/rtdl_v2_14_tag`
- V3.0.2 root: `/root/rtdl_v3_0_2_tag`
- Result: neither tree exposed a specialized custom-callback route.
- Both trees did expose existing weighted-sum routes, which remain control rows
  only.

Selected denominator:

`materialized_hit_id_plus_device_callback_reduce_fallback`

This is not a slow CPU fallback. It traces the same OptiX geometry,
materializes hit IDs on device, then evaluates the callback and reduces in a
separate device kernel. It does not receive V4's callback-in-hit fusion.

## Correctness

All 24 rows completed and passed correctness.

Matrix:

- callbacks: `weighted_sum` control, plus primary `affine_score`,
  `threshold_score`, `minmax_score`
- regimes: `dense_hits`, `sparse_hits`, `no_hit_empty_reduction`
- scales: `262144`, `524288`
- repeats: `7`
- warmups: `2`

## Performance

Primary custom-callback rows only:

| callback | geomean V3 baseline / V4 | min | max | verdict |
|---|---:|---:|---:|---|
| `affine_score` | `1.033x` | `1.014x` | `1.072x` | fail `<1.10x` per-callback floor |
| `threshold_score` | `1.030x` | `1.017x` | `1.058x` | fail `<1.10x` per-callback floor |
| `minmax_score` | `1.024x` | `1.017x` | `1.035x` | fail `<1.10x` per-callback floor |

Primary geomean:

- V4 over V2.14 denominator: `1.029x`
- V4 over V3.0.2 denominator: `1.029x`

Frozen bars:

- V4 custom callbacks vs V2.14 geomean must be `>=1.50x`: failed.
- V4 custom callbacks vs V3.0.2 geomean must be `>=1.20x`: failed.
- every primary callback must be `>=1.10x` over V3.0.2 in dense/sparse:
  failed.

Control row:

- `weighted_sum` geomean was `1.036x`, but it is control only and cannot support
  the app-level claim.

## Interpretation

The constrained specialized callback path works functionally and is a real V4
capability, but it does not produce a material performance win for this focused
app under the frozen protocol. The measured gain is roughly parity plus a small
increment, not formal high-performance V4 evidence.

Goal4711 therefore closes this target as a failed high-performance proof. It
does not authorize:

- V4 release wording;
- formal high-performance V4 wording;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support;
- all-app benchmarking.

## Immediate Engineering Consequence

Do not continue trying to sell `ray_triangle_custom_scored_accumulation` as the
second formal high-performance V4 proof. The next useful goal must either:

1. redesign the runtime lever so callback-in-hit fusion removes a larger cost
   than this target exposes; or
2. select a different app-level target with a pre-written hypothesis for a
   material V4-specific win; or
3. reframe V4 as bounded operator/capability progress until a formal
   high-performance target is proven.

## Validation

Local:

```text
py -m py_compile scripts/v4_goal4711_custom_scored_app_pod.py src/rtdsl/v4_goal4711_custom_scored_app_result.py
py -m unittest tests.v4_goal4711_custom_scored_app_result_test
```

Remote:

```text
/usr/bin/python3 -m py_compile src/rtdsl/v4_goal4711_custom_scored_app_result.py scripts/v4_goal4711_custom_scored_app_pod.py src/rtdsl/v4.py
/usr/bin/python3 scripts/v4_goal4711_custom_scored_app_pod.py --dry-run
/usr/bin/python3 -m unittest tests.v4_goal4711_custom_scored_app_result_test
/usr/bin/python3 scripts/v4_goal4711_custom_scored_app_pod.py --warmups 2 --repeat 7 --json-out /root/v4_goal4711_full_20260626.json --md-out /root/v4_goal4711_full_20260626.md
```

## Goal-Level Decision Audit

1. Was I being stupid?

Yes, during the first smoke runner version.

2. If yes, what action made the decision stupid?

I initially labeled a materialized contribution route as the V2/V3 fallback,
but that route evaluated the callback inside the OptiX hit program. That gave
the fallback the V4-only capability and made the comparison conceptually wrong.

3. Is there another path that avoids being stuck on that bad premise?

Yes. The corrected denominator materializes hit IDs only, then evaluates the
callback and reduces in a separate device kernel. V4 alone gets callback-in-hit
fusion.

4. Can I now try the different path that actually solves the problem?

Yes. The full Goal4711 run used the corrected denominator and produced the
failure result above.
