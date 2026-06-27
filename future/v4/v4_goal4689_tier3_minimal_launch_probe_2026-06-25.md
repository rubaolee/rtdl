# V4 Goal4689: Tier-3 Minimal Launch Correctness Probe

Date: 2026-06-25
Status: `minimal_launch_correctness_passed_not_support`

## Result

Goal4689 passed its narrow POD gate on
`root@194.68.245.170:22089`:

- Numba scalar callback PTX generated: `true`
- semantic launch wrapper compiled with `--keep-device-functions`: `true`
- combined callback + wrapper PTX generated: `true`
- OptiX module creation succeeded: `true`
- raygen/miss/hitgroup/direct-callable program groups created: `true`
- OptiX pipeline creation succeeded: `true`
- `optixLaunch` succeeded: `true`
- pipeline log reported `direct callable call(s): 1`
- output value: `5`
- expected value: `5`
- callback output matched expected: `true`

Evidence:

- `future/v4/evidence/v4_goal4689_tier3_minimal_launch_probe_2026-06-25.json`
- `future/v4/evidence/v4_goal4689_tier3_minimal_launch_probe_2026-06-25.md`

## What Actually Moved

Goal4688 proved that the semantic wrapper plus Numba callback PTX could form an
OptiX module/program groups/pipeline. Goal4689 proves the next, stricter fact:
the pipeline can actually launch and invoke a direct callable that calls the
Numba-generated callback body.

The minimal callback is:

```text
state + hit_distance * weight + primitive_id * 0.0
```

The launch wrapper calls:

```text
optixDirectCall<void>(0)
```

with the callable record at SBT index `0`. The direct callable then calls the
Numba callback with `(hit_distance=1.0, primitive_id=0, weight=2.0, state=3.0)`,
so the expected output is `5.0`.

## Boundaries

This goal still does not authorize public Tier-3 support. It proves one scalar
callback shape can launch and produce the correct value.

Not authorized:

- arbitrary callback support
- action-shaped callback support
- callback overhead/performance claims
- app-level speedup claims
- V4 release or tag claims
- app-identity kernels

Goal4690 should freeze an overhead protocol before any timing result is used.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. After Goal4688 passed, the next concrete unknown was launch correctness,
   not another app benchmark or wording pass.

2. If yes, what action made it stupid?
   The risky action would have been to count module/pipeline creation as
   runnable Tier-3 callback support. Goal4689 avoids that by requiring
   `optixLaunch` and output parity.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Keep the test scalar and deterministic, and prove the exact ABI path
   before measuring overhead or generalizing callback support.

4. Can I now try the different path that actually solves the problem?
   Yes. The next path is Goal4690: define and then measure overhead against a
   native equivalent and/or direct baseline, with a kill condition if callable
   overhead is too high.
