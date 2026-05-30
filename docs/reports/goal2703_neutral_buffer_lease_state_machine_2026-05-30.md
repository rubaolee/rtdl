# Goal2703 Neutral Buffer Lease State Machine

Date: 2026-05-30
Status: local implementation; validation in progress
Depends on: Goal2692

## Purpose

Goal2703 strengthens the v2.5 ownership/lifetime story before native OptiX
CUDA-resident hit-column work begins. Goal2692 defined ownership states and
allowed transitions. Goal2703 turns that into an executable lease object that
future native buffers can be forced through.

This is still not a CUDA allocator or native free path. It is a fail-closed
Python contract layer for ownership, borrow, completion, release, and failure
cleanup.

## What Changed

Added `RtdlNeutralBufferLease` and `create_neutral_buffer_lease(...)` in
`src/rtdsl/neutral_buffer_seam.py`.

Lease operations:

| Operation | Transition |
| --- | --- |
| `begin_partner_borrow()` | owner-retained state -> `partner_borrowed` via `handoff_begin`. |
| `complete_partner_borrow()` | `partner_borrowed` -> original owner state via `continuation_complete`. |
| `release()` | owner-retained state -> `released` via `release`. |
| `failure_cleanup()` | `partner_borrowed` / pending-native state -> `released` via `failure_cleanup`. |

Native producer leases can start in
`native_owned_pending_state_machine`; their metadata sets
`native_state_machine_required=True`. This preserves the boundary that actual
native allocation/release/failure cleanup still must be implemented before real
CUDA buffers are attached.

The lease symbols are imported at `rtdsl` module scope for experimental use but
are not added to `rtdsl.__all__`.

## Validation

Added `tests/goal2703_neutral_buffer_lease_state_machine_test.py`.

Initial Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2702_raydb_explicit_partner_planner_integration_test
Ran 18 tests in 0.310s
OK
```

Windows focused v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 88 tests in 8.067s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\neutral_buffer_seam.py src\rtdsl\__init__.py \
  tests\goal2703_neutral_buffer_lease_state_machine_test.py
OK
```

Local Linux validation on `192.168.1.20`, checkout
`/home/lestat/work/rtdl_goal2692_linux_check`, commit
`27d88cc8dc0c15bb486ba569d08caa32c4e21825`:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2703_neutral_buffer_lease_state_machine_test \
  tests.goal2702_raydb_explicit_partner_planner_integration_test \
  tests.goal2700_explicit_hit_stream_gather_partner_test \
  tests.goal2698_hit_stream_partner_continuation_plan_test \
  tests.goal2696_v2_5_partner_support_matrix_test \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 88 tests in 2.610s
OK (skipped=5)

python3 -m py_compile src/rtdsl/neutral_buffer_seam.py src/rtdsl/__init__.py \
  tests/goal2703_neutral_buffer_lease_state_machine_test.py
OK
```

The test covers:

- producer-retained borrow/complete/release lifecycle;
- native-pending leases returning to the native-pending owner state;
- invalid release while borrowed;
- invalid borrow after failure cleanup;
- leases cannot start borrowed or released;
- lease symbols remain experimental and absent from `rtdsl.__all__`.

## Boundary

Goal2703 does not:

- allocate CUDA memory;
- free native buffers;
- synchronize CUDA streams;
- prove true zero-copy;
- prove performance;
- authorize release claims.

## Next Work

1. Run the expanded focused suite on Windows and local Linux.
2. When implementing native OptiX CUDA output, make native-produced hit columns
   create and return a lease rather than a loose owner string.
3. Add pod tests for real overflow/failure cleanup once native buffers exist.
