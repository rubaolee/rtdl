# Goal4040 Partition Device Ambiguous Union Preview

Date: 2026-06-08

## Purpose

Goal4040 moves one more fixed-radius partition-convergence continuation step
off the host. Goal4032/4034 moved near-partition pair enumeration onto CuPy.
Goal4035/4038 then showed that full component labels can reuse a partition
summary, but ambiguous partition pairs still used host-side exact point checks.

Goal4040 adds a generic device continuation for that ambiguous step:

- the partition-summary typed stream now includes `partition_point_ordinals`;
- the CuPy summary preview populates that column from the sorted point order;
- the component-label preview accepts
  `ambiguous_union_execution="cupy_partition_points"`;
- ambiguous partition pairs are classified on the device using partition
  offsets, point ordinals, and point coordinate columns;
- safe-full and connected ambiguous partition pairs are unioned by a generic
  CuPy union kernel.

This is not DBSCAN-specific. The engine-facing shape is still a generic
fixed-radius partition summary plus component-label continuation.

## Boundary

This is an executable preview and schema hardening step, not a promoted default
route. It does not add a native ABI, does not choose partners automatically,
does not add app-specific native-engine logic, does not authorize release
wording, does not authorize public speedup wording, does not authorize broad
RT-core wording, does not authorize whole-app wording, and does not authorize
true-zero-copy wording.

## Expected Validation

The focused validation is:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal4040_partition_device_ambiguous_union_test \
  tests.goal4016_partition_convergence_typed_stream_contract_test \
  tests.goal4017_partition_summary_reference_builder_test \
  tests.goal4019_partition_summary_same_contract_validator_test \
  tests.goal4027_partition_summary_cupy_preview_test \
  tests.goal4029_partition_summary_numba_preview_test \
  tests.goal4035_partition_component_labels_cupy_preview_test
```

On systems without CuPy, the runtime CuPy tests skip; the pod run must exercise
them.
