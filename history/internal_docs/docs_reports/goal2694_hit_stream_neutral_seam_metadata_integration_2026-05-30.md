# Goal2694 Hit-Stream Neutral Seam Metadata Integration

Date: 2026-05-30
Status: local implementation; validation in progress
Depends on: Goal2692 neutral buffer seam contract

## Purpose

Goal2692 created the v2.5 neutral buffer seam. Goal2694 threads that contract
through the current hit-stream and typed-payload metadata, so the existing
Ray/primitive hit-stream path exposes a partner-neutral producer/consumer/copy
record without changing execution semantics.

This is the next safe step before native OptiX CUDA-resident hit-column output:
the existing host bridge, synthetic CUDA-shaped columns, and payload columns now
describe their handoff through the same neutral seam vocabulary.

## What Changed

`src/rtdsl/hit_stream_handoff.py` now imports the Goal2692 seam and adds:

| Location | New metadata |
| --- | --- |
| `RtdlHitStreamColumnHandoff.to_metadata()` | `neutral_buffer_seam_contract_version` and two `neutral_buffer_seams` for `ray_ids` and `primitive_ids`. |
| `RtdlTypedPrimitivePayloadColumns.to_metadata()` | `neutral_buffer_seam_contract_version` and two `neutral_buffer_seams` for `primitive_group_ids` and `primitive_values`. |
| `gather_typed_payload_columns_for_hit_stream(...)` | `neutral_buffer_handoff_summary` recording hit-stream and payload transfer statuses, any host staging, and any zero-copy authorization. |

The integration uses `neutral_buffer_descriptor_from_rtdl_buffer(...)`; it does
not create a new data path.

## Behavior

| Case | Neutral seam status |
| --- | --- |
| Host-row bridge | `host_stage`; `host_materialized_before_handoff=True`; zero-copy false. |
| CPU/reference columns | `host_reference`; zero-copy false. |
| CUDA-shaped native columns without hardware proof | `borrowed_device_pointer_unmeasured`; zero-copy false; native promotion false. |
| Future measured same-pointer/no-host-stage CUDA path | Representable by Goal2692, but not produced by this goal. |

For `source_mode="native_device_columns"`, the seam uses
`lifetime_state="native_owned_pending_state_machine"` and
`native_producer=True`. That is intentionally conservative: it marks the exact
place where the real native allocator/release/failure-cleanup state machine must
land, without pretending it already exists.

## Test

Added `tests/goal2694_hit_stream_neutral_seam_metadata_test.py`.

The test covers:

- host bridges record `host_stage` neutral seams and keep removed-bottleneck
  false;
- CUDA-shaped native hit-stream columns record borrowed/unmeasured device
  pointers, pending native ownership, no zero-copy, and no native promotion;
- typed payload columns can publish the same neutral seam vocabulary;
- gather metadata summarizes both hit-stream and payload transfer statuses.

Windows focused v2.5 contract validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 67 tests in 7.554s
OK (skipped=5)

py -3 -m py_compile src\rtdsl\hit_stream_handoff.py \
  tests\goal2694_hit_stream_neutral_seam_metadata_test.py
OK
```

Local Linux validation on `192.168.1.20`, checkout
`/home/lestat/work/rtdl_goal2692_linux_check`, commit
`de6ea9129de626d1fb71389cc9156497ef484c16`:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal2694_hit_stream_neutral_seam_metadata_test \
  tests.goal2692_neutral_buffer_seam_lifetime_contract_test \
  tests.goal2690_post_goal2689_contract_honesty_test \
  tests.goal2685_device_resident_hit_stream_handoff_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2684_generic_rt_hit_stream_handoff_test \
  tests.goal2662_v2_5_partner_continuation_contract_test \
  tests.goal2679_v2_5_triton_grouped_argmin_preview_test \
  tests.goal2681_v2_5_triton_partner_adapter_front_door_test
Ran 67 tests in 2.516s
OK (skipped=5)

python3 -m py_compile src/rtdsl/hit_stream_handoff.py \
  tests/goal2694_hit_stream_neutral_seam_metadata_test.py
OK
```

## Boundary

Goal2694 does not:

- replace the current hit-stream execution path;
- add native OptiX CUDA output buffers;
- measure same-pointer/no-host-stage evidence;
- authorize public zero-copy, speedup, or release claims;
- make Torch, CuPy, Triton, Numba, or raw CUDA mandatory.

## Next Work

1. Add a v2.5 support matrix that names supported `(partner x operation x
   backend)` cells and references the neutral seam.
2. Rework the Torch-specific gather branch into an explicit partner choice
   path, preserving CPU/reference and CuPy/raw-CUDA routes.
3. When a pod is available, implement and measure the first native OptiX
   bounded CUDA hit-column output path against the neutral seam.
