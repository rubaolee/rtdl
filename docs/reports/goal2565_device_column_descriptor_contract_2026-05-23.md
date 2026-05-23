# Goal2565: Device Column Descriptor Contract

Date: 2026-05-23

## Scope

Goal2551 identified that device/partner-resident column metadata was split
across the columnar partner planner, partner adapters, and OptiX runtime ctypes
encoding. This slice introduces one Python-side descriptor contract for
partner-resident input columns.

## Change

- Added `DeviceColumnDescriptor` in `src/rtdsl/columnar_partner.py`.
- PartnerResidentColumnHandoff remains a compatibility alias to the new
  descriptor class, including the old `(name, logical_kind, handoff)`
  constructor shape.
- `PartnerResidentColumnarRecordSet.fields` now stores
  `DeviceColumnDescriptor` instances.
- Descriptor metadata records stable ABI fields: logical kind, dtype token,
  device pointer, element count, stride bytes, CUDA device identity, source
  protocol, transfer mode, and host-materialization boundary.
- OptiX ctypes encoding now consumes descriptor fields directly instead of
  re-deriving dtype/count/stride/device pointer from the raw handoff in each
  runtime path.

## Boundary

The descriptor still carries the original handoff object to preserve
ownership/lifetime and existing metadata. It does not authorize native
execution by itself, no public zero-copy or speedup claim is made, and output
buffer descriptors remain future work for the grouped-reduction substrate.

## Validation

Added `tests/goal2565_device_column_descriptor_contract_test.py`, covering:

- public export of `DeviceColumnDescriptor`;
- compatibility alias preservation;
- legacy constructor compatibility;
- descriptor field construction from existing partner-resident record sets;
- metadata shape;
- OptiX ctypes field encoding through descriptor fields;
- this report.

No pod was used. This is local Python ABI-boundary cleanup.
