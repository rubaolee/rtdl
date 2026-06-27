# V4 Goal4697 Specialized Tier-3 API Contract

Status: constrained API contract scaffold, not public Tier-3 support

- validation: `passed`
- candidate surface: `module_specialized_direct_device_callback`
- supported callback shape: `pure_scalar_return_numba_cabi_device_function`
- wrapper strategy: `specialize_hit_program_module_and_call_callback_as_direct_device_function`

## Accepted Contract

- language: `numba_cuda_device_function_only`
- compiler contract: `Numba C-ABI device function PTX composed into an RTDL-generated OptiX module`
- signature: one scalar state output from fixed scalar inputs; Goal4695 validated float64 state, uint32 primitive_id, float64 hit_distance, float64 weight

Accepted callback shapes:

- `custom_scalar_reduce`
- `custom_score`
- `custom_threshold`
- `custom_minmax`

## Validation Matrix

- `accepted`: `tier3_specialized_candidate_contract_accepted_not_public_support` (accepted: `True`)
- `rejected_python`: `rejected_goal4697_arbitrary_python_callback` (accepted: `False`)
- `rejected_action`: `rejected_goal4697_action_or_side_effect_callback` (accepted: `False`)
- `rejected_external_memory`: `rejected_goal4697_external_memory_mutation_callback` (accepted: `False`)
- `rejected_sbt`: `rejected_goal4697_dynamic_sbt_direct_callable_hot_path` (accepted: `False`)
- `rejected_non_scalar`: `rejected_goal4697_non_scalar_callback_signature` (accepted: `False`)

## Boundary

This contract allows internal productization work only. It is not public Tier-3 support, not raw OptiX callback support, not a release authorization, and not an app-level performance claim.
