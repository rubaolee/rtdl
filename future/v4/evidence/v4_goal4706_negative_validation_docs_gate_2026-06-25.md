# V4 Goal4706 Negative Validation And Example Gate

- validation: `passed`
- status: `goal4706_specialized_tier3_negative_validation_docs_gate_not_public_support`
- accepted example status: `compile_cache_ready_not_executed`
- example returncode: `0`

## Negative Rows

| case | stage | error code | compile allowed |
|---|---|---|---|
| `arbitrary_python_callback` | `rejected_before_compile` | `RTDL_V4_TIER3_CALLBACK_REJECTED_ARBITRARY_PYTHON_CALLBACK` | `False` |
| `action_side_effect_callback` | `rejected_before_compile` | `RTDL_V4_TIER3_CALLBACK_REJECTED_ACTION_OR_SIDE_EFFECT_CALLBACK` | `False` |
| `external_memory_mutation_callback` | `rejected_before_compile` | `RTDL_V4_TIER3_CALLBACK_REJECTED_EXTERNAL_MEMORY_MUTATION_CALLBACK` | `False` |
| `dynamic_sbt_direct_callable_hot_path` | `rejected_before_compile` | `RTDL_V4_TIER3_CALLBACK_REJECTED_DYNAMIC_SBT_DIRECT_CALLABLE_HOT_PATH` | `False` |
| `non_scalar_variable_length_output` | `rejected_before_compile` | `RTDL_V4_TIER3_CALLBACK_REJECTED_ACTION_OR_SIDE_EFFECT_CALLBACK` | `False` |

## Boundary

This gate validates fail-closed behavior and a bounded candidate example only. It does not authorize public Tier-3 support, release wording, or performance claims.
