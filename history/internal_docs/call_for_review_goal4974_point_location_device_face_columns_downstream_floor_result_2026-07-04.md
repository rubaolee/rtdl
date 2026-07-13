# Call For Review: Goal4974 Point-Location Face-ID Device Columns

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4974_point_location_device_face_columns_downstream_floor_result_2026-07-04.md`
- `history/internal_docs/goal4974_point_location_device_face_columns_artifacts_2026-07-04/baseline_rows_summary.json`
- `history/internal_docs/goal4974_point_location_device_face_columns_artifacts_2026-07-04/device_face_columns_summary_final.json`
- `src/rtdsl/optix_runtime.py`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`
- `tests/goal4974_point_location_device_face_columns_route_test.py`

## Requested Verdict Labels

Choose one:

- `approve_goal4974_point_location_device_face_columns_moves_downstream_floor`
- `approve_with_amendments`
- `fail_redo_due_to_app_specific_core_or_hidden_copy_claim`
- `fail_redo_due_to_incorrect_performance_boundary`

## Review Questions

1. Is the `PreparedOptixPlanarMapPointLocation2D` wrapper change a valid generic directed point-location device-column front door, rather than a RayJoin-specific core primitive?
2. Does the RayJoin app route remain app-owned, with no RayJoin output-chain or overlay semantics moved into RTDL core?
3. Does the report correctly disclose that the current route still copies the `face_id` column to NumPy and is not a true-zero-copy claim?
4. Does the POD evidence justify saying the downstream floor moved from about 3.24s to about 2.64s on the top4 representative input?
5. Are the parity checks sufficient for this bounded binary-route performance comparison?
6. Does the report avoid comparing the 5.29s writer-free route as if it were an author text-output byte-equality route?
7. Is the next bottleneck diagnosis correct: midpoint point generation and carrier/group construction are now larger than PIP row materialization?
8. Should Goal4974 close with `completed_point_location_device_face_columns_moves_downstream_floor`?

## Important Boundaries To Enforce

- Do not authorize true-zero-copy wording.
- Do not authorize broad RayJoin or RTDL speedup wording.
- Do not treat this as parity with the author C++ text-output route.
- Do not allow RayJoin-specific schema into the generic row-buffer or point-location primitive.
- Keep Layer 4 fusion out of scope.
