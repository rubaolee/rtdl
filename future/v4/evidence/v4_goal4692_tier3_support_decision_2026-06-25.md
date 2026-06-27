# V4 Goal4692 Tier-3 Support Decision

Status: direct-callable overhead is yellow; public Tier-3 support is not authorized

- validation: `passed`
- measured direct-callable ratio: `1.6705538933080346`
- selected next track: `module_specialized_direct_device_callback_in_hit_program`

## Decision

do_not_promote_sbt_direct_callable_support; continue Tier-3 through module-specialized direct device callback because the same Numba callback denominator ran correctly without OptiX callable SBT overhead

## Meaning

The OptiX SBT direct-callable ABI is runnable and correct, but the measured `1.67x` overhead is too high for support. The next useful Tier-3 path is module-specialized direct device callback composition: compile the user's Numba callback into the generated OptiX module and call it directly from a hit-program-shaped wrapper.

## Non-Authorization

- no public Tier-3 support
- no arbitrary callback support
- no direct-callable performance claim
- no V4 release authorization
