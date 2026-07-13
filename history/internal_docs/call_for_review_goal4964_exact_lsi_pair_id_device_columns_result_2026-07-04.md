# Call For Review: Goal4964 Exact LSI Pair-Id Device Columns Result

Please review:

`history/internal_docs/goal4964_exact_lsi_pair_id_device_columns_result_2026-07-04.md`

## Requested Verdict

One of:

- `approve_goal4964_correctness_passed_performance_no_go`
- `approve_with_required_amendments`
- `block_until_goal4964_native_route_or_measurement_is_rechecked`

## Review Questions

1. Is the new native/API route generic exact segment-pair / planar-map LSI
   pair-id output rather than a RayJoin overlay shortcut?
2. Does the evidence show correctness/fingerprint parity with the host exact
   pair-id row route?
3. Does the evidence support the no-go performance conclusion?
4. Is it correct that host row materialization/copy is not the meaningful
   bottleneck, given the `~0.000526s` device-to-NumPy copy median?
5. Is it correct to avoid promoting `--exact-lsi-device-columns` as the
   v2.14.3 performance route?
6. Should Goal4965 pivot from "measure exact device columns as the new route" to
   "document no-go and define the next bottleneck direction"?
