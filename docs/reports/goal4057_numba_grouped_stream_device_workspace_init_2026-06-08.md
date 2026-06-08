# Goal4057 Numba Grouped-Stream Device Workspace Init

Status: local implementation, pod timing pending.

Goal4057 removes per-run host-to-device workspace reset copies from the
generic OptiX+Numba fixed-radius grouped-stream continuation.

The prepared handle now uses a generic Numba CUDA init kernel to write:

- `parent[i] = i`;
- `border_candidate[i] = point_count` only when predicate-false border
  candidates may be written by the native grouped-union pass.

This replaces the previous `copy_to_device(parent_initial_host)` and
`copy_to_device(border_initial_host)` resets in
`PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D.run`.

## Contract Boundary

This is a generic workspace-initialization improvement. It does not add DBSCAN-native ABI,
does not change the OptiX grouped-union primitive, does not add app-specific
engine logic, does not choose a partner automatically, and does not authorize speedup,
release, true-zero-copy, or broad RT-core claims.

Expected metadata for new Numba grouped-stream runs:

- `numba_workspace_init_policy: device_parent_iota_optional_border_fill`;
- `numba_workspace_host_reset_copy_used: false`.
