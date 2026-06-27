# Call For Review: V4 Goal4685 Tier-3 Wrapper/Direct-Callable ABI Protocol Gate

Please review:

- `future/v4/v4_goal4685_tier3_wrapper_abi_protocol_gate_2026-06-25.md`
- `src/rtdsl/v4_goal4685_tier3_wrapper_abi_protocol.py`
- `tests/v4_goal4685_tier3_wrapper_abi_protocol_test.py`

Requested verdict labels:

- `accept_goal4685_protocol_continue_goal4686_local_spike`
- `reject_goal4685_protocol_missing_required_stage`
- `accept_with_required_amendments`
- `blocked_insufficient_evidence`

## Questions

1. Does Goal4685 correctly avoid repeating the old bare-helper PTX `optixModuleCreate` probe?
2. Are the required stages complete for a real wrapper/direct-callable ABI spike?
3. Is the planner boundary correct: scalar Numba callbacks are spike-only, action-shaped callbacks rejected?
4. Are the reliability, correctness, and overhead gates strict enough?
5. Is Goal4686 properly limited to local scaffold/protocol implementation, with POD later?
6. Are the non-authorization boundaries complete?

## Non-Authorization

This review must not authorize:

- V4 release;
- POD spending;
- Tier-3 public support;
- raw OptiX callback support;
- public speedup wording;
- whole-app high-performance claims;
- app-specific native kernels;
- C ABI, embedding, true-zero-copy, or non-Python host claims.
