# Call For Review: Goal4988 LSI Device Columns Direct Numba Handoff

Please review:

```text
history/internal_docs/goal4988_lsi_device_columns_direct_numba_handoff_result_2026-07-04.md
Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py
tests/goal4988_lsi_device_columns_direct_numba_handoff_test.py
```

## Requested Verdict Label

```text
approve_goal4988_lsi_pair_device_columns_direct_to_numba_projection
```

## Review Questions

1. Does the change correctly reuse the existing generic device-column row-buffer
   and CUDA-array-interface handoff assets instead of inventing a RayJoin-specific
   core shortcut?
2. Does the new path remove the exact/bounded LSI pair-id
   `device -> NumPy -> device` loop before Numba CUDA reprojection when
   `--device-columnar` is enabled?
3. Is native device-column lifetime handled safely by keeping the output owner
   alive until the projection kernel finishes and closing it in `finally`?
4. Does the old NumPy copy route remain available for non-device-columnar
   fallback?
5. Does the summary honestly distinguish direct pair-id handoff from the
   remaining downstream host copies, and are the device-resident flags derived
   from row-buffer metadata rather than hard-coded route selection?
6. Do the tests sufficiently prevent regression back to the previous pair-id
   host-copy route?
7. Does the report correctly avoid claiming full device-resident overlay,
   true zero-copy, author-performance parity, or a public speedup before POD
   measurement?
8. Should the next gate be a POD correctness/performance smoke on the existing
   top4 representative route, with validation based on row-buffer metadata plus
   structural output alignment rather than route flags alone?

## Non-Authorization Boundary

This review does not authorize:

```text
full device-resident Section 5.7 claim;
author-performance parity claim;
public v2.14.3 release;
RTDL core RayJoin-specific primitive;
Layer 4 fusion work.
```
