# Call For Review: V4 `goal4622` Tier-3 Callback Spike Protocol Completion

Date: 2026-06-24
Requested verdict labels:

- `accept_goal4622_complete_protocol_only_not_support`
- `reject_goal4622_incomplete`

## Review Request

Please critically review whether `goal4622` is complete as a protocol/boundary
goal only.

This goal does not implement Tier-3 callback support. It writes and gates the
falsifiable protocol that a later Tier-3 callback spike must pass before any
support or release claim can be considered.

## Goal Objective

Write and gate a falsifiable Tier-3 callback spike protocol for complex user
logic, keeping Tier-3 as spike-only/deferred and obtaining completion review
without implementing callback support.

## Files Changed Or Added

- `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- `src/rtdsl/v4_operator_catalog.py`
- `tests/v4_tier3_callback_spike_protocol_test.py`
- `tests/v4_operator_catalog_test.py`
- `future/v4/callback_and_operator_planning.md`
- `future/v4/tier3_numba_ptx_spike.md`
- `future/v4/tier3_optix_module_link_spike.md`
- `future/v4/README.md`
- `future/v4/tier2_operator_catalog.md`

## Protocol Boundary

Accepted future spike shape:

- `scalar per-hit reduce only`
- Numba CUDA device function only
- fixed scalar inputs to fixed scalar output state
- no Python objects, host memory, dynamic dispatch, or reflection
- at most one scalar or one fixed tuple of at most four scalar outputs

Rejected shapes:

- shared mutation
- global memory mutation outside fixed RTDL-owned output state
- user-visible atomics
- dynamic allocation
- variable-length output
- append/list/emit-row behavior
- recursion
- spawned action logic
- direct OptiX API calls from user callback
- raw OptiX callbacks as the public API
- app-identity kernels

## Falsifiable Gates

A later Tier-3 callback implementation spike must pass all of these before any
support discussion:

- compile reliability `>= 95%` across at least 20 attempts and 4 accepted scalar
  callback variants
- OptiX wrapper/direct-callable link/run reliability `>= 95%`
- correctness parity `100%`
- median callback route overhead `<= 1.50x` versus a matching hand-written
  Tier-2 fused route at each required size
- hard kill if any tested size exceeds `2.00x`

## Planner Results To Check

Scalar callback request must return:

- status: `tier3_spike_only_not_v4_0_release_surface`
- tier: `tier3_numba_ptx_spike`
- protocol status: `tier3_protocol_goal4622_spike_only_not_support`
- protocol doc: `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- no API surface
- `tier3_spike_authorized: true`
- all support/release/raw-callback flags false

Action-shaped callback request must return:

- status: `rejected_action_shaped_callback_deferred`
- protocol status: `rejected_by_goal4622_action_shape_boundary`
- protocol doc: `future/v4/tier3_callback_spike_protocol_2026-06-24.md`
- no API surface
- no spike/support/release/raw-callback authorization

## Verification

Local Windows:

```text
py -m unittest tests.v4_operator_catalog_test tests.v4_fixed_radius_docs_and_example_test tests.v4_tier3_numba_ptx_probe_test tests.v4_tier3_optix_module_link_probe_test tests.v4_tier3_callback_spike_protocol_test tests.v4_catalog_regression_gate_test tests.v4_frontdoor_test
Ran 35 tests in 16.663s
OK
```

Local catalog dry-run:

```text
py scripts/v4_catalog_regression_gate.py --mode dry-run --copies 16 --ray-count 16 --include-candidates --json-out future/v4/evidence/v4_goal4622_catalog_dry_run_callback_protocol_2026-06-24.json --md-out future/v4/evidence/v4_goal4622_catalog_dry_run_callback_protocol_2026-06-24.md
status: passed
release_authorized: false
examples: 10
```

POD Linux:

```text
ssh root@194.68.245.170 -p 22089 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so RTDL_OPTIX_LIB=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so python3 -m unittest tests.v4_operator_catalog_test tests.v4_tier3_numba_ptx_probe_test tests.v4_tier3_optix_module_link_probe_test tests.v4_tier3_callback_spike_protocol_test tests.v4_catalog_regression_gate_test tests.v4_frontdoor_test
Ran 27 tests in 7.343s
OK
```

POD catalog dry-run evidence:

- `future/v4/evidence/v4_goal4622_catalog_pod_dry_run_callback_protocol_2026-06-24.json`
- `future/v4/evidence/v4_goal4622_catalog_pod_dry_run_callback_protocol_2026-06-24.md`

POD dry-run status:

```text
status: passed
release_authorized: false
examples: 10
operator_callback_planning_scalar_callback: tier3_spike_only_not_v4_0_release_surface
operator_callback_planning_complex_callback: rejected_action_shaped_callback_deferred
```

## Questions For Review

1. Does this protocol answer how V4 handles complex user callback logic without
   falsely claiming arbitrary OptiX callback support?
2. Are the accepted and rejected callback shapes precise enough to prevent
   app-specific/native-kernel drift?
3. Are the compile reliability, wrapper/link reliability, correctness, and
   overhead gates falsifiable and strict enough?
4. Does the planner correctly expose scalar callbacks as spike-only and reject
   action-shaped callbacks?
5. Do the docs avoid support, release, raw-callback, true-zero-copy, broad
   speedup, C ABI/embedding, and app-specific kernel claims?
6. Is it acceptable to mark `goal4622` complete as protocol-only while Tier-3
   callback implementation remains future work?

## Non-Authorization

This review must not authorize:

- V4 release
- V4 release candidate
- Tier-3 callback support
- raw OptiX callback support
- true-zero-copy public claims
- broad V4 speedup claims
- whole-application speedup claims
- CuPy performance claims
- C ABI / embedding / non-Python-host work
- app-specific native kernels
