# V4 Goal4693: Specialized Direct-Device Callback In OptiX Hit Program

Date: 2026-06-25
Status: `specialized_hit_callback_correctness_passed_not_support`

## Result

Goal4693 passed on the current POD `root@194.68.245.170:22089`.

This probe built a minimal OptiX custom-primitive GAS, launched a ray with
`optixTrace`, reported an intersection, executed a closest-hit program, and
called the Numba-generated callback as a normal device function from that hit
program.

Evidence:

- `future/v4/evidence/v4_goal4693_specialized_hit_callback_probe_2026-06-25.json`
- `future/v4/evidence/v4_goal4693_specialized_hit_callback_probe_2026-06-25.md`

## Key Facts

- `optixTrace` was used: `true`
- hit program was used: `true`
- SBT direct callable was used: `false`
- pipeline launch succeeded: `true`
- output value: `5`
- expected value: `5`
- callback output matched expected: `true`

The OptiX module log recorded:

- raygen `trace call(s): 1`
- closesthit semantic type: `CLOSESTHIT`
- intersection semantic type: `INTERSECTION`
- direct callable calls: `0`

## Why This Matters

Goal4691 showed that the SBT direct-callable ABI is currently too expensive
for support (`1.67x` overhead over direct device callback). Goal4693 proves the
alternative track selected by Goal4692: specialize the user's Numba callback
into the generated OptiX module and call it directly from hit-program code.

This is the first evidence in this chain that a custom user callback can sit
inside a real OptiX traversal/hit-program path without using app-identity
kernels or SBT direct-callable overhead.

## Boundary

This is still not public Tier-3 support.

Not authorized:

- arbitrary callback support
- action-shaped callback support
- performance claims
- app-level speedup claims
- V4 release or tag claims

Goal4694 should decide the next measurement/productization step for the
specialized hit-callback track.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal followed the yellow overhead decision rather than continuing
   to polish the slower SBT direct-callable path.

2. If yes, what action made it stupid?
   The bad action would have been to stay in raygen microbench land. This goal
   moved into OptiX traversal and hit-program semantics.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. The path is module-specialized direct device callback composition,
   rather than dynamic SBT direct-callable invocation for hot callbacks.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4694 should freeze the next decision: overhead measurement inside
   this hit-program shape, or productization of a constrained specialized
   callback route.
