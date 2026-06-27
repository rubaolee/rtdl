# V4 Goal4692: Tier-3 Support Decision After Yellow Overhead

Date: 2026-06-25
Status: `goal4692_tier3_direct_callable_yellow_pivot_to_specialized_device_callback`

## Decision

Do not promote OptiX SBT direct-callable Tier-3 support from the current
evidence.

Continue Tier-3 through a different implementation track:

```text
module_specialized_direct_device_callback_in_hit_program
```

Evidence:

- `future/v4/evidence/v4_goal4692_tier3_support_decision_2026-06-25.json`
- `future/v4/evidence/v4_goal4692_tier3_support_decision_2026-06-25.md`

## Why

Goal4691 measured the SBT direct-callable path at `1.6705538933080346x` over
the same Numba callback called as a direct device function. That is:

- above the `<=1.50x` pass bar;
- below the `>2.00x` hard-kill bar;
- therefore yellow.

The direct device-function denominator is not fake: it used the same Numba
C-ABI callback body, composed into the generated OptiX module, and passed
correctness. It is the better next Tier-3 candidate because it avoids per-call
OptiX callable SBT overhead.

## Consequence

The next goal must prove the specialized direct device callback inside an
OptiX hit-program-shaped wrapper, not merely inside a raygen microbench.

Goal4693 should therefore build a minimal traversal/hit-program probe where:

- a generated OptiX hit program calls the Numba callback as a normal device
  function;
- output correctness is verified;
- no SBT direct callable is used;
- no app-identity kernel is introduced.

## Boundary

Not authorized:

- public Tier-3 callback support
- direct-callable support
- arbitrary callback support
- callback performance claims
- V4 release or tag claims

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The measured yellow result was not promoted or discarded.

2. If yes, what action made it stupid?
   The bad action would be to keep polishing the direct-callable path despite
   the frozen overhead miss, or to hard-kill Tier-3 despite a working faster
   direct-device callback denominator.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Use module-specialized direct device callback composition for the hot
   path, and keep SBT direct callable as experimental/dynamic only.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4693 should move the direct-device callback from raygen microbench
   into an OptiX hit-program-shaped probe.
