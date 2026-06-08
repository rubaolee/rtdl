# Goal4056 Numba Label/Flag Signature Continuation

Status: implemented and pod-smoked on an RTX 4000 Ada pod.

Goal4056 adds a generic Numba CUDA partner continuation:

- `NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION`
- `describe_numba_label_count_and_flag_count_i64()`
- `run_numba_label_count_and_flag_count_i64(labels, flags, label_count=...)`

The primitive counts signed `int64` labels into a device `label_counts`
column, counts negative labels separately, and counts nonzero `uint32` flags.
It is intentionally generic: labels and flags are graph/continuation columns,
not RT-DBSCAN-native engine semantics.

## RT-DBSCAN Effect

The RT-DBSCAN Numba column-signature route now uses the generic
label/flag-count continuation for all Numba grouped-stream label mixes instead
of only using `segmented_count_i64` when every point is core.

Expected metadata for new runs:

- `column_signature_strategy:
  numba_label_count_and_flag_count_label_columns`;
- `column_signature_uses_numba_label_count_and_flag_count: true`;
- `column_signature_materializes_point_ids: false`;
- `column_signature_materializes_core_flags: false`.

This removes the old mixed-label fallback that copied point ids, component
labels, and core flags to the host just to build a component-size signature.

## Boundary

This goal does not add a DBSCAN native ABI, does not add app-specific native
logic, does not replace RT traversal, does not authorize true-zero-copy claims,
does not authorize public speedup claims, and does not authorize release action.

The primitive is a partner continuation only. RT-core work remains in the
existing app-agnostic OptiX fixed-radius grouped-union path.

## Pod Evidence

The pod probe at commit `c36f7575` ran the CUDA-capable unit slice and a
threshold sweep over:

```text
optix_rt_core_grouped_stream_numba_column_signature_3d
dataset=road3d, point_count=4096, repeat=3, warmup=1, no_validation
```

The CUDA unit slice reported 14 tests OK with 1 skip. The threshold sweep
observed mixed-label rows at thresholds 64 and 128
(`all_core_flags_true: false`) while preserving:

- `column_signature_strategy:
  numba_label_count_and_flag_count_label_columns`;
- `column_signature_materializes_point_ids: false`;
- `column_signature_materializes_core_flags: false`.

The bounded artifact is
`docs/reports/goal4056_numba_label_flag_signature_pod_probe.json`.
