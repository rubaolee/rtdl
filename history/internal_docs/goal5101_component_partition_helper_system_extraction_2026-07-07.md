# Goal5101 Component Partition Helper System Extraction

## Status

`completed_generic_component_partition_helper_extracted`

## Purpose

RT-DBSCAN needed canonical component-label comparison. That logic is not DBSCAN-specific: any connected-component or clustering-style result may need label-renaming-invariant partition comparison. Goal5101 extracts the reusable part into RTDL system code.

## New System Module

```text
src/rtdsl/component_partition.py
```

Public helpers:

```text
canonical_partition_labels(labels, noise_label=-1)
component_signature_from_partition(labels, core_count=None, core_flags=None, noise_label=-1)
partition_equivalent(left, right, noise_label=-1)
```

They are exported from:

```text
src/rtdsl/__init__.py
```

## App Integration

`run_authorofficial_component_signature_gate.py` now delegates canonical partition/signature work to `rtdsl` rather than carrying independent app-local implementations.

## Tests

```text
tests/goal5101_component_partition_helpers_test.py
```

The tests cover:

- label-renaming invariance,
- noise preservation,
- signature construction from `core_count`,
- signature construction from `core_flags`,
- fail-closed behavior when neither core count nor core flags are supplied.

## Boundary

The helper is generic and does not implement DBSCAN. It does not compute neighborhoods, density reachability, or cluster expansion. It only compares and summarizes component partitions.
