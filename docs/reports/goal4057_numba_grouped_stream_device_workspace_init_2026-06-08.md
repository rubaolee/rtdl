# Goal4057 Numba Grouped-Stream Device Workspace Init

Status: implemented and pod-smoked on an RTX 4000 Ada pod.

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

## Pod Evidence

At commit `a60509b8`, the pod CUDA slice reported 15 tests OK with 1 skip.
A threshold sweep over the same `road3d` 4096-point RT-DBSCAN Numba
column-signature probe used for Goal4056 confirmed:

- every row reported `numba_workspace_host_reset_copy_used: false`;
- mixed-label thresholds 64 and 128 still used
  `numba_label_count_and_flag_count_label_columns`;
- after a same-protocol baseline rerun requested by external review, elapsed
  time improved versus the Goal4056 same-pod baseline by about 1.07x to 1.09x
  on this small diagnostic probe.

The bounded artifact is
`docs/reports/goal4057_numba_grouped_stream_device_workspace_init_pod_probe.json`.
