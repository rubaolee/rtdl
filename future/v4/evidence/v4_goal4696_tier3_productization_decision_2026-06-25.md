# V4 Goal4696 Tier-3 Productization Decision

Status: constrained productization candidate, not public Tier-3 support

- validation: `passed`
- productization candidate: `module_specialized_direct_device_callback`
- supported callback shape: `pure_scalar_return_numba_cabi_device_function`
- SBT direct callable status: `experimental_yellow_not_public_support`

## Decision

productize a constrained candidate surface for module-specialized Numba scalar callbacks, but do not authorize public Tier-3 support

## Rejected Shapes

- `arbitrary_python_callback`
- `action_or_side_effect_callback`
- `external_memory_mutation_callback`
- `dynamic_sbt_direct_callable_hot_path`

## Required Before Public Support

- stable API contract
- negative validation for rejected callback shapes
- compile/cache/error-reporting behavior
- at least one app-route validation using the specialized callback path
- external 3-AI review

## Boundary

This is not public Tier-3 support, not a release authorization, and not an app-level performance claim.
