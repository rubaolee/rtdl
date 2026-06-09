# Goal4201: RT-DBSCAN Boundary Policy Fair Timing

Date: 2026-06-09

## Purpose

Goal4198 proved that the explicit `lowest_component_root_two_pass` policy runs
on RTX hardware. Goal4201 asks the next engineering question: is this two-pass
policy a candidate for promotion, or is it only a correctness/reference route?

The answer from the RTX 4000 Ada sweep is clear: the policy is correct for the
tested counts-only signatures, but it is not fast enough to promote as the
default. The second RT traversal is the cost center.

## Method

The tracked runner is:

`scripts/goal4201_rt_dbscan_boundary_policy_fair_timing.py`

It compares the default `lowest_candidate_then_root` policy against the explicit
`lowest_component_root_two_pass` policy under the same prepared OptiX+Numba
front-door contract. It warms both policies, alternates measurement order, keeps
prepared handles resident, and records claim-boundary fields as false.

Pod command:

```bash
python3 scripts/goal4201_rt_dbscan_boundary_policy_fair_timing.py \
  --preset clustered3d_16k \
  --preset clustered3d_64k \
  --preset road3d_64k \
  --preset ngsim_dense_64k \
  --warmup 2 \
  --repeat 5 \
  --output docs/reports/goal4201_rt_dbscan_boundary_policy_fair_timing_rtx4000ada/fair_timing_repeat5.json
```

Artifacts:

- `docs/reports/goal4201_rt_dbscan_boundary_policy_fair_timing_rtx4000ada/fair_timing_repeat5.json`
- `docs/reports/goal4201_rt_dbscan_boundary_policy_fair_timing_rtx4000ada/fair_timing_repeat5.stdout`

## Results

| Dataset | Points | Default median sec | Two-pass median sec | Two-pass / default | Same signature |
| --- | ---: | ---: | ---: | ---: | --- |
| `clustered3d` | 16,384 | 0.009845 | 0.017632 | 1.791x | yes |
| `clustered3d` | 65,536 | 0.078566 | 0.148616 | 1.892x | yes |
| `road3d` | 65,536 | 0.015426 | 0.022593 | 1.465x | yes |
| `ngsim_dense` | 65,536 | 0.017833 | 0.017881 | 1.003x | yes |

All cases preserve the counts-only signature. The clustered and road-shaped
cases show the expected cost: the second prepared RT pass makes the policy
roughly 1.5x to 1.9x slower. The dense-grid case has no negative-label boundary
work, so the policies are effectively tied.

## Decision

Do not promote `lowest_component_root_two_pass` as the default route. Keep it as
an explicit policy/reference option for parity testing and policy-sensitive
users.

The next generic performance target is a single-traversal boundary-candidate
resolution path:

1. collect boundary candidate roots during the primary traversal;
2. after predicate-true union roots settle, rebase candidate roots through the
   final parent array on device;
3. assign deterministic lowest-root boundary labels without a second RT
   traversal.

That is a runtime/primitive improvement, not an RT-DBSCAN app-specific trick.

## Boundary

Goal4201 does not authorize release, route promotion, public speedup claims,
whole-app speedup claims, broad RT-core claims, true-zero-copy claims, automatic
partner selection, or app-specific native engine logic.
