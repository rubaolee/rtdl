# Call For Review - Goal4857 Planar-Map Point-Location Public Front Door Cleanup

Please review:

- `history/internal_docs/goal4857_planar_map_point_location_public_front_door_cleanup_2026-07-01.md`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/datasets.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/engine_feature_matrix.py`
- `tests/goal4857_planar_map_point_location_public_front_door_test.py`
- `history/internal_docs/goal4855_rayjoin_section53_pip_public_front_door.py`
- `history/internal_docs/goal4856_rtdl_section53_pip_raw_diagnostic.py`
- public docs touched under `docs/`

## Requested Verdict

One of:

- `approve_goal4857_public_front_door_cleanup`
- `approve_with_required_amendments`
- `reject_goal4857_redo`

## Questions

1. Does `prepare_planar_map_point_location_2d_optix` establish a cleaner public
   front door for Section 5.3-style planar-map point-location/PIP than the
   previous `prepare_directed_segment_point_location_2d_optix` plus user-side
   environment-variable wrapper?
2. Is this cleanup generic at the API boundary, or does it hide a new RayJoin
   application-specific helper?
3. Is it acceptable that the lower native compatibility bridge still uses the
   historical `RTDL_RAYJOIN_CDB_*` environment variables internally, given that
   user/application code no longer sets them directly and the bridge is guarded
   and restored?
4. Do the new dataset aliases `chains_to_planar_map_segments` and
   `chains_to_planar_map_points` improve the public model without breaking
   legacy compatibility?
5. Do the Section 5.3 internal runners now use the new public front door and
   avoid direct `_point_location_env` / `RTDL_RAYJOIN_CDB_*` usage?
6. Are the docs bounded correctly, avoiding Section 5.7 overlay, all-eight,
   broad RayJoin, or broad performance claims?
7. Are the tests sufficient for this cleanup level?
8. Should Goal4857 close with
   `completed_planar_map_point_location_public_front_door_cleanup`?
