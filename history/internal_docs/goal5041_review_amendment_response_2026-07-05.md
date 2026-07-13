# Goal5041 Review Amendment Response

Date: 2026-07-05

Status: review conditions incorporated; implementation still not started

Reviewed source:

- `history/internal_docs/claude_review_goal5041_v2_14_4_device_columnar_api_plan_2026-07-05.md`

## Verdict Accepted

Claude verdict:

```text
approve_v2_14_4_device_columnar_prepared_pipeline_api_plan
```

The approval carried four conditions.  The design and call-for-review have been amended so those conditions are implementation gates.

## C1 - RayJoin Naming Debt

Accepted.

Change made:

- Goal5042 now requires an explicit remediate-or-defer table for every existing core/native `rayjoin_*`, `RayjoinCdb*`, or `rtdl_optix_*rayjoin*` symbol/class.
- Goal5050 now requires native symbol-name scanning, not only public Python/docs scanning.

Required classifications:

```text
rename_now
wrap_with_public_alias_defer_native_rename
keep_internal_with_debt
move_to_app
```

Minimum symbols that must appear in the table:

```text
rtdl_optix_prepare_rayjoin_cdb_point_location_2d
rtdl_optix_run_prepared_rayjoin_cdb_point_location_2d
rtdl_optix_prepared_rayjoin_cdb_point_location_2d_device_face_id_columns
PreparedRayjoinCdbPointLocation2D / PreparedOptixRayjoinCdbPointLocationPoints2D
rayjoin_lsi / RTDL_OPTIX_SEGMENT_PAIR_PREDICATE legacy alias
```

## C2 - `device_group_by` Public Exposure

Accepted.

Change made:

- `device_order_by` remains a public v2.14.4 target.
- `device_group_by` is no longer assumed public.
- Goal5046 now decides public-vs-internal based on POD proof of true device-resident grouped reduce.

Reason:

`src/rtdsl/columnar_partner.py` currently states that grouped count/sum reductions read host `row_values`.  A public `device_group_by` cannot claim device-resident semantics while that remains true.

Allowed exits:

```text
completed_public_device_group_by_segmented_reduce
completed_internal_only_device_group_by_until_device_resident_reduce
blocked_device_group_by_public_due_to_host_row_values
```

## C3 - Stream Ordering And Residency Metadata

Accepted.

Change made:

- Goal5043 now preserves the existing four-state stream-ordering vocabulary:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

- `DeviceColumnBuffer` residency must be derived from actual column interfaces and `materializes_host_rows_for_bridge`, never from app flags or summary self-declarations.

## C4 - RayJoin Regression Gate Includes Device Residency

Accepted.

Change made:

- Goal5049's performance gate remains:

```text
top4 prepared binary six-batch sum <= 0.36s median-of-N
```

- It now also requires:

```text
lsi_pair_input_device_resident == true
lsi_pair_host_to_device_copy_used == false
public DeviceColumnBuffer materializes_host_rows_for_bridge == false where the route claims device-resident handoff
```

A timing pass with hidden host copies must fail the gate.

## Current Decision

The plan remains approved for implementation after these amendments.  Goal5042 should start next, and implementation must stay inside the revised gates above.
