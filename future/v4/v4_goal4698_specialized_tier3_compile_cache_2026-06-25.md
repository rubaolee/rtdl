# V4 Goal4698: Specialized Tier-3 Compile/Cache Scaffold

Date: 2026-06-25
Status: `goal4698_specialized_tier3_compile_cache_scaffold_not_public_support`

## Result

Goal4698 added the productization scaffold around the Goal4697 specialized
Tier-3 callback contract:

- deterministic cache key:
  `rtdl-v4-tier3-<sha256-prefix>`
- cache inputs:
  - contract version
  - callback symbol
  - callback PTX hash
  - toolchain fingerprint hash
  - OptiX ABI
  - compute target
  - wrapper strategy
- compile-stage classification:
  - `contract_validation`
  - `numba_ptx_generation`
  - `callback_symbol_extraction`
  - `wrapper_specialization`
  - `nvcc_wrapper_compile`
  - `optix_module_create`
  - `program_group_create`
  - `pipeline_create`
  - `launch_validation`
- fail-closed error codes for rejected callbacks and incomplete compile inputs.

Evidence:

- `future/v4/evidence/v4_goal4698_specialized_tier3_compile_cache_2026-06-25.json`
- `future/v4/evidence/v4_goal4698_specialized_tier3_compile_cache_2026-06-25.md`

## Validation

The scaffold validates:

- accepted scalar Numba candidate reaches `compile_cache_ready_not_executed`
- identical input produces the same cache key
- changed callback PTX produces a different cache key
- action-shaped callback is rejected before compile
- missing symbol/PTX/toolchain input is classified as incomplete
- `optix_module_create` failures are classified with a stage-specific error

Local verification passed:

- `py scripts/v4_goal4698_specialized_tier3_compile_cache.py --json-out future/v4/evidence/v4_goal4698_specialized_tier3_compile_cache_2026-06-25.json --md-out future/v4/evidence/v4_goal4698_specialized_tier3_compile_cache_2026-06-25.md`
- `py -m unittest tests.v4_goal4698_specialized_tier3_compile_cache_test tests.v4_goal4697_specialized_tier3_api_contract_test tests.v4_goal4696_tier3_productization_decision_test`
  - result: `10 tests OK`
- `py -m py_compile src/rtdsl/v4_goal4698_specialized_tier3_compile_cache.py scripts/v4_goal4698_specialized_tier3_compile_cache.py src/rtdsl/v4.py`

## Boundary

Not authorized:

- public Tier-3 support
- arbitrary callback support
- raw OptiX callback support
- app-level speedup claims
- V4 release or tag claims

Goal4699 should define the app-route validation protocol for the specialized
callback candidate. No public support wording is allowed before at least one
app-route validation and external 3-AI review pass.

## Goal-Level Decision Audit

1. Was I being stupid?
   No. This goal did not invent a new benchmark or claim speed. It built the
   productization mechanics needed before the next real app-route experiment.

2. If yes, what action made it stupid?
   The stupid action would have been to run another one-off POD probe without
   stable cache/error behavior. Goal4698 fixes that before more measurement.

3. Is there another path that avoids getting stuck on a bad premise?
   Yes. Treat unsupported callbacks as typed planner errors before compile,
   and treat compile/link failures as stage-specific product errors rather than
   vague stdout logs.

4. Can I now try the different path that actually solves the problem?
   Yes. Goal4699 can specify an app-route validation protocol against this
   scaffold, then the POD can be used only for the decisive app-route run.
