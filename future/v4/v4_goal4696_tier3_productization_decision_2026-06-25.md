# V4 Goal4696: Tier-3 Productization Decision

Date: 2026-06-25
Status: `goal4696_productize_constrained_specialized_tier3_candidate_not_public_support`

## Decision

Goal4696 accepts the Goal4695 result as sufficient to continue productizing a
constrained Tier-3 candidate surface:

- candidate: `module_specialized_direct_device_callback`
- supported callback shape: `pure_scalar_return_numba_cabi_device_function`
- evidence basis: Goal4695 measured `1.0355240926982583x` overhead versus the
  inline hit-program formula under the frozen Goal4694 protocol
- next goal: `Goal4697 constrained specialized Tier-3 API contract scaffold`

This decision does not promote public Tier-3 support. It only authorizes a
bounded productization path for one callback shape that has already passed a
real `optixTrace -> closesthit` overhead probe.

Evidence:

- `future/v4/evidence/v4_goal4696_tier3_productization_decision_2026-06-25.json`
- `future/v4/evidence/v4_goal4696_tier3_productization_decision_2026-06-25.md`

## Accepted Surface

The accepted candidate is a module-specialized direct-device callback path:

1. User callback is compiled as a Numba C-ABI device function.
2. RTDL specializes an OptiX module around that callback symbol.
3. The hit program calls the callback as a normal device function.
4. The path avoids SBT direct-callable hot-path overhead.

This is narrower than arbitrary OptiX callback support, but it is the first
Tier-3 route that has both correctness evidence and focused overhead evidence.

## Rejected Shapes

The following remain rejected for V4.0 productization:

- `arbitrary_python_callback`
- `action_or_side_effect_callback`
- `external_memory_mutation_callback`
- `dynamic_sbt_direct_callable_hot_path`

The SBT direct-callable route remains `experimental_yellow_not_public_support`
because Goal4691 measured `1.6705538933080346x`, above the frozen pass bar.

## Required Before Public Support

Before any public Tier-3 support claim, the following gates must be completed:

- stable API contract
- negative validation for rejected callback shapes
- compile/cache/error-reporting behavior
- at least one app-route validation using the specialized callback path
- external 3-AI review

## Boundary

Not authorized:

- public Tier-3 support
- arbitrary callback support
- action-shaped callback support
- app-level speedup claims
- V4 release or tag claims

## Goal-Level Decision Audit

1. Was I being stupid?
   No. The decision follows the measured split: SBT direct callable failed the
   pass bar, while specialized hit-program callback passed the focused overhead
   gate.

2. If yes, what action made it stupid?
   The bad action would be to turn one scalar callback success into a broad
   callback-support claim. This decision explicitly rejects that.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Productize the constrained specialized route and keep dynamic/general
   callback support experimental until separate evidence exists.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4697 should define the API contract and negative validation first,
   then an app-route validation can test whether the route creates real user
   value.
