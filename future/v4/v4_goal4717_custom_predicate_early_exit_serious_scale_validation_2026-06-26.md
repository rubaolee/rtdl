# V4 Goal4717 Custom Predicate Early-Exit Serious-Scale Validation

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `custom_predicate_early_exit_serious_scale_pass_not_release`

## Goal

Broaden the Goal4715 custom predicate early-exit timing result beyond the
initial focused sizes and verify that the V4 operator-pushdown surface remains
materially faster at serious app-like scale.

This goal is deliberately not an all-app release gate. It validates one V4
surface:

`v4_ray_triangle_custom_predicate_early_exit_3d_numba`

## Evidence

Evidence files:

- `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.json`
- `future/v4/evidence/v4_goal4717_custom_predicate_early_exit_serious_scale_pod_2026-06-26.md`

POD:

- host: `root@194.68.245.170 -p 22089`
- workspace: `/root/rtdl_v4_candidate_pod`
- GPU: NVIDIA RTX A5000
- driver: `570.195.03`

Command:

```text
/usr/bin/python3 scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py --scales 262144,524288 --warmups 2 --repeat 5 --json-out /root/v4_goal4717_serious_scale_20260626.json --md-out /root/v4_goal4717_serious_scale_20260626.md
```

## Result

Classification:

`pass_focused_timing_gate_not_release`

Primary early-accept rows:

- V4/V2.14 primary geomean: `4.632757911153888x`
- V4/V3.0.2 primary geomean: `4.632757911153888x`
- minimum primary V4/V3.0.2 row: `2.054686620906942x`
- maximum primary V4/V3.0.2 row: `9.673329274891774x`
- primary row count: `6`
- correctness: all primary and control rows passed

Control rows:

- V4/V3.0.2 control geomean: `1.6303665522050805x`

Denominator discovery:

- V2.14 tag root had no custom predicate any-hit early-exit route.
- V3.0.2 tag root had no custom predicate any-hit early-exit route.
- Selected denominator was the same OptiX geometry with all hit layers
  materialized to device memory, followed by separate device predicate/reduce
  work.

## Primary Rows

| scale | regime | role | correctness | V4 seconds | fallback seconds | fallback/V4 | V4 predicate invocations | fallback predicate invocations |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 262144 | `dense_early_accept_k8` | `primary` | true | `0.000284384` | `0.000584320` | `2.055x` | 262144 | 2097152 |
| 262144 | `dense_early_accept_k32` | `primary` | true | `0.000329184` | `0.002931650` | `8.906x` | 262144 | 8388608 |
| 262144 | `sparse_early_accept_k32` | `primary` | true | `0.000129888` | `0.000606880` | `4.672x` | 65536 | 2097152 |
| 524288 | `dense_early_accept_k8` | `primary` | true | `0.000508160` | `0.001117090` | `2.198x` | 524288 | 4194304 |
| 524288 | `dense_early_accept_k32` | `primary` | true | `0.000591360` | `0.005720420` | `9.673x` | 524288 | 16777216 |
| 524288 | `sparse_early_accept_k32` | `primary` | true | `0.000196768` | `0.001069980` | `5.438x` | 131072 | 4194304 |

## Interpretation

Goal4717 confirms that the custom predicate early-exit surface has a real V4
performance mechanism:

- the user supplies a constrained Numba C-ABI predicate;
- RTDL lowers it into an OptiX any-hit traversal path;
- RTDL owns the action, such as `terminate_on_first_accept`;
- primary regimes avoid materializing all candidate hits;
- the fallback must trace and materialize all candidate layers before filtering.

The win comes from operator pushdown and early termination, not from rebranding
an existing V2.14/V3.0.2 primitive.

## Boundary

Goal4717 does not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- arbitrary Python callback support;
- raw OptiX callback support;
- public Tier-3 support;
- non-Python embedding/C ABI claims.

It authorizes the next engineering step:

`Goal4718: map the measured custom predicate early-exit surface into the V4 app-level benchmark/release matrix and decide what public V4 claim it can support.`

## Goal-Level Decision Audit

1. Was I being stupid?

No. This goal did not replace app-level validation with a toy result. It ran the
same constrained V4 route at larger app-like scales and kept the claim bounded.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. If the serious-scale rows had collapsed to parity, the correct path would
be to stop treating custom predicate early-exit as a V4 performance pillar and
fall back to a capability-only claim. The measured rows stayed materially above
the frozen gate.

4. Can I now try the different path that actually solves the problem?

Yes. The useful path is to connect this measured surface to the app-level V4
release matrix and public documentation, while continuing to forbid broad
all-app speedup wording until the matrix supports it.
