# Goal4035 Partition Component-Label CuPy Preview

Date: 2026-06-08

## Purpose

Goal4035 adds `build_v2_8_fixed_radius_partition_convergence_component_labels_cupy_preview_3d(...)`.

The preview consumes the generic fixed-radius partition-summary stream:

- `safe_skip` partition pairs do no work;
- `safe_full` partition pairs union partition components;
- `ambiguous` partition pairs use exact point checks before unioning components.

The default summary producer is the Goal4032 CuPy `device_bounded_offsets` mode. If no pair capacity is supplied, that mode allocates a conservative bounded-offset upper capacity rather than requiring a host pair-count warmup.

The preview also supports `partition_union_execution="cupy_safe_full"`, which runs safe-full partition unions in a CuPy RawKernel and downloads only the resulting partition-parent array plus ambiguous partition pairs for exact checking. The simpler `partition_union_execution="host"` mode remains available for debugging.

For correctness tests, `validate_summary_same_contract=True` keeps the Goal4019 validator in the path. Timing runs may set it to `False` to avoid timing the Python oracle; that timing mode is explicitly marked in metadata and must not be used as standalone correctness evidence.

## Boundary

This is still an executable preview, not a promoted release route. It does not add a native ABI, does not add app-specific engine logic, does not choose partners automatically, and does not authorize public speedup, broad RT-core, whole-app benchmark, release, or true-zero-copy wording.

The next performance step is timing this full component-label preview against the current grouped-stream route on pod-scale inputs.
