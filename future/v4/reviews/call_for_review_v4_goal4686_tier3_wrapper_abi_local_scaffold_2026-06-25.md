# Call For Review: V4 Goal4686 Tier-3 Wrapper ABI Local Scaffold

Please review:

- `future/v4/v4_goal4686_tier3_wrapper_abi_local_scaffold_2026-06-25.md`
- `src/rtdsl/v4_goal4686_tier3_wrapper_abi_scaffold.py`
- `scripts/v4_goal4686_tier3_wrapper_abi_scaffold.py`
- `tests/v4_goal4686_tier3_wrapper_abi_scaffold_test.py`
- `future/v4/evidence/v4_goal4686_tier3_wrapper_abi_scaffold_2026-06-25.cu`

Requested verdict labels:

- `accept_goal4686_local_scaffold_continue_goal4687_compile_probe`
- `reject_goal4686_scaffold_not_semantic_optix_path`
- `accept_with_required_amendments`
- `blocked_insufficient_evidence`

## Questions

1. Does the scaffold correctly move beyond the old bare-helper PTX probe?
2. Are the semantic entries sufficient for a local compile/link spike target?
3. Is `rtdl_user_scalar_reduce` a reasonable symbol contract for Goal4687 to prove or replace?
4. Does the goal correctly leave POD, Tier-3 support, release, and speed claims unauthorized?
5. Is Goal4687 the right next step: symbol extraction/aliasing and compile probe before any full POD overhead benchmark?

## Non-Authorization

This review must not authorize:

- V4 release;
- POD spending beyond a later explicit compile/link gate;
- Tier-3 public support;
- raw OptiX callback support;
- public speedup wording;
- whole-app high-performance claims;
- app-specific native kernels;
- C ABI, embedding, true-zero-copy, or non-Python host claims.
