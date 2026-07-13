# Call For Review: Goal4999 Device Midpoint Query-Point Handoff

Please review:

```text
history/internal_docs/goal4999_device_midpoint_query_points_handoff_result_2026-07-04.md
history/internal_docs/goal4999_device_midpoint_query_points_artifacts_2026-07-04/device_query_midpoint_top4_repeat5.json
```

## Requested Verdict Label

`approve_goal4999_device_midpoint_query_point_handoff`

## Review Questions

1. Did Goal4999 remove the midpoint scaled-query-point host pack boundary in the
   `--device-resident-carrier` route?

2. Is the new native API a generic directed point-location device-query input,
   rather than a RayJoin overlay/output-chain kernel hidden in RTDL core?

3. Does the public planar-map point-location wrapper correctly expose
   `prepare_device_query_points(...)` under the existing environment guard?

4. Is the device query-point lifetime safe, given that the prepared native point
   handle keeps a Python owner reference to the Numba device array?

5. Are the POD validation results sufficient for this narrow claim?
   Specifically:
   - native library rebuilt successfully with compatible OptiX 8.1 headers;
   - exported symbol exists;
   - 9 related tests pass on POD;
   - top4 route completes with `lsi_row_count=428322` and
     `descriptor_pair_count=15014`.

6. Is the performance interpretation honest: Goal4999 is mainly an
   architecture-boundary fix with a modest measured improvement
   (`0.3381s -> 0.3295s` median), not an author-parity or broad-performance
   headline?

7. Are the remaining floors correctly identified as ordering/carrier/consumer
   work rather than midpoint query-point packing?

8. Should Goal4999 close with:

```text
completed_device_midpoint_query_point_handoff__host_scaled_point_pack_removed
```
