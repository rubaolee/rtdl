# Call For Review - Goal5042 Existing Asset Inventory And API Mapping

Reviewer: Claude or external reviewer

Please review:

- `history/internal_docs/goal5042_existing_asset_inventory_and_api_mapping_2026-07-05.md`
- prior approved plan:
  - `history/internal_docs/goal5041_v2_14_4_device_columnar_api_design_and_implementation_plan_2026-07-05.md`
  - `history/internal_docs/claude_review_goal5041_v2_14_4_device_columnar_api_plan_2026-07-05.md`
- relevant implementation assets:
  - `src/rtdsl/device_column_row_buffer.py`
  - `src/rtdsl/columnar_partner.py`
  - `src/rtdsl/hit_stream_handoff.py`
  - `src/rtdsl/neutral_buffer_seam.py`
  - `src/rtdsl/v2_6_neutral_partner_handoff.py`
  - `src/rtdsl/numba_partner_continuation.py`
  - `src/rtdsl/current_prepared_session_residency_profiles.py`
  - `src/rtdsl/optix_runtime.py`
  - `src/rtdsl/embree_runtime.py`
  - `src/native/optix/*`
  - `src/native/embree/*`

Requested verdict label:

```text
approve_goal5042_asset_inventory_and_api_mapping
```

Alternative verdict labels:

```text
revise_goal5042_mapping_before_goal5043
fail_goal5042_due_to_missing_rayjoin_symbol_debt
fail_goal5042_due_to_overpromoting_device_group_by
```

## Review Questions

1. Does the report correctly conclude that v2.14.4 should consolidate existing v2.x assets rather than create a new fifth columnar surface?

2. Is `RtdlDeviceColumnRowBuffer` correctly classified as the main substrate to wrap into public `DeviceColumnBuffer`?

3. Does the mapping correctly preserve the existing four-state stream-ordering vocabulary:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

4. Does the report correctly classify `device_order_by` as public-ready for v2.14.4, with narrow dtype/key support and fail-closed behavior?

5. Does the report correctly keep `device_group_by` internal/experimental unless Goal5046 proves a true device-resident reduce path on POD?

6. Is the `columnar_partner.py` blocker evidence quoted and interpreted correctly, especially the host `row_values` blocker?

7. Is the RayJoin naming-debt table broad enough across Python, OptiX native, Embree native, env-var bridges, and app-owned RayJoin code?

8. Are the remediate/defer decisions reasonable:

```text
wrap_with_public_alias_defer_native_rename
keep_internal_with_debt
move_to_app_boundary_already
keep_internal_or_legacy_with_debt
```

9. Is it acceptable that Goal5042 does not rename native ABI symbols yet, provided Goal5050 scans and documents remaining debt?

10. Does the report avoid using RayJoin app code as API evidence except as consumer/regression evidence?

11. Is the proposed next step, Goal5043 public `DeviceColumnBuffer` contract, the right continuation?

12. Should Goal5042 close with:

```text
completed_asset_inventory_for_v2_14_4_api
```

or must it be revised first?
