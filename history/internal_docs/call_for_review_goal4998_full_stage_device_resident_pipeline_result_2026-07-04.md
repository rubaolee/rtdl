# Call For Review - Goal4998 Full-Stage Device-Resident Pipeline Result

Reviewer: Claude / external reviewer

Please review:

- `history/internal_docs/goal4998_full_stage_device_resident_pipeline_result_2026-07-04.md`
- `history/internal_docs/goal4998_full_stage_device_resident_pipeline_artifacts_2026-07-04/baseline_compiled_group_top4_repeat5_serial.json`
- `history/internal_docs/goal4998_full_stage_device_resident_pipeline_artifacts_2026-07-04/device_resident_carrier_top4_repeat5_serial.json`
- `Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py`

## Context

The owner requested that we stop treating previous row-buffer / Numba handoff work as enough and actually connect the device-resident path into the real RayJoin 5.7 writer-free binary route.

Goal4998 implements an app-layer `--device-resident-carrier` route:

- no RTDL core/native change;
- no new RayJoin-specific RTDL primitive;
- device face-id midpoint scatter;
- prepared-session carrier dataset arrays;
- device carrier side count/fill/combine;
- device descriptor-pair count consumer.

## Review Questions

1. Does the implementation genuinely connect the device-column route into the real RayJoin carrier/consumer path, rather than merely demonstrating a toy handoff?
2. Does it preserve the architecture boundary: RTDL remains a generic system and RayJoin remains an app-layer paper reproduction?
3. Is the structural gate sufficient for this writer-free binary route (`lsi_row_count=428322`, `descriptor_pair_count=15014`, stable repeat rows)?
4. Is the performance claim correctly bounded to prepared/query-many writer-free hot performance?
5. Is the reported improvement modest but real: baseline median `0.36405662819743156s` versus device route median `0.338140819221735s`?
6. Does the report correctly reject fresh one-shot, paper byte-equality, author parity, and strict zero-copy claims?
7. Are the remaining non-device-resident boundaries described honestly, especially midpoint query-point preparation and host run-bound metadata?
8. Should Goal4998 close with:

`completed_goal4998_app_layer_device_resident_carrier_route__modest_prepared_hot_win__not_strict_zero_copy`
