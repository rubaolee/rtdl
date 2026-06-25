# Call For Review: V4 Goal4631 Tier-3 Spike Execution Decision

Date: 2026-06-24

Requested verdict labels:

- `accept_goal4631_defer_tier3_not_supported`
- `accept_with_required_amendments`
- `reject_tier3_should_continue_before_goal4632`
- `reject_overclaiming_or_route_drift`

Primary document:

- `future/v4/v4_goal4631_tier3_spike_execution_decision_2026-06-24.md`

Code and tests:

- `src/rtdsl/v4_tier3_spike_decision.py`
- `tests/v4_goal4631_tier3_spike_decision_test.py`

Supporting evidence:

- `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.json`
- `future/v4/evidence/v4_tier3_numba_ptx_probe_2026-06-24.md`
- `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.json`
- `future/v4/evidence/v4_tier3_optix_module_link_probe_2026-06-24.md`
- `future/v4/tier3_numba_ptx_spike.md`
- `future/v4/tier3_optix_module_link_spike.md`
- `future/v4/reviews/goal4630_completion_consensus_and_review_debt_2026-06-24.md`

Focused test result:

```text
py -m unittest tests.v4_tier3_callback_spike_protocol_test tests.v4_tier3_numba_ptx_probe_test tests.v4_tier3_optix_module_link_probe_test tests.v4_goal4631_tier3_spike_decision_test tests.v4_goal4630_pushdown_recognizer_test
Ran 24 tests
OK
```

Review objective:

Decide whether Goal4631 correctly closes Tier-3 as spike-only/deferred and not V4.0 public support.

Questions:

1. Does the decision correctly distinguish Stage 1 narrow PTX evidence from a protocol pass?
2. Does the decision correctly interpret the Stage 2 `optixModuleCreate` failure?
3. Is it correct that correctness and overhead stages cannot run yet?
4. Is it correct that V4.0 release cannot depend on Tier-3?
5. Are the future Tier-3 requirements sufficient before any future support claim?
6. Do the code and tests make the non-support boundary machine-checkable?
7. Are all non-authorization boundaries preserved?

Non-authorization requirements:

- Do not authorize V4 release.
- Do not authorize Tier-3 callback support.
- Do not authorize raw OptiX callback support.
- Do not authorize arbitrary callback support.
- Do not authorize measured-catalog promotion.
- Do not authorize broad speedup claims.
- Do not authorize true-zero-copy wording.
- Do not authorize C ABI / embedding claims.
- Do not authorize app-specific native kernels.

