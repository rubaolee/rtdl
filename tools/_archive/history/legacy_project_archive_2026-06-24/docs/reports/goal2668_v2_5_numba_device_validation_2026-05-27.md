# Goal2668: v2.5 Numba Device-Resident Group Validation

Status: local source/test backed, CUDA execution pending.

Date: 2026-05-27

## Purpose

Gemini's Goal2667 review accepted the v2.5 partner preview but noted that the
Numba fallback validated `group_ids` by copying the full array to host. That is
acceptable for a preview, but it is the wrong direction for large grouped row
streams.

This goal removes that full host-copy validation path and replaces it with a
device-resident error-flag kernel.

## Implemented Change

Updated:

- `src/rtdsl/numba_partner_continuation.py`
- `tests/goal2666_v2_5_numba_segmented_preview_test.py`
- `scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py`

New exported constant:

- `NUMBA_GROUP_ID_VALIDATION_MODE = "device_resident_error_flag"`

The Numba descriptor now records:

```text
group_id_validation_mode = device_resident_error_flag
```

## Semantics

For `validate_group_ids=True`, Numba now launches a CUDA validation kernel that:

1. scans `group_ids` on device;
2. writes `1` to a one-element device error flag if any group id is outside
   `[0, group_count)`;
3. copies only that one-element flag back to host;
4. raises `ValueError("group_ids must be in [0, group_count)")` on failure.

This preserves the Goal2662 reference contract while avoiding a full
`group_ids.copy_to_host()` validation pass.

## Boundary

This is still preview-only:

- no public speedup claim;
- no benchmark promotion;
- no RT traversal replacement;
- no app-specific semantics;
- no claim that Numba is preferred over Triton.

The change only removes an avoidable host-copy validation bottleneck from the
Numba fallback path.

## Validation

Local tests verify descriptor metadata, lazy imports, source-level validation
shape, and docs. CUDA execution still requires a pod:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2666_v2_5_numba_segmented_preview_test \
  tests.goal2665_v2_5_triton_grouped_runner_test
```

## Pod Gate

On the next CUDA pod, run the Goal2665 runner with `--include-numba` to verify
that the device validation kernel compiles and that the grouped count/sum paths
match Torch baselines.
