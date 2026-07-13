# Call For Review - Goal5043 Public DeviceColumnBuffer Contract

Reviewer: Claude or external reviewer

Please review:

- `history/internal_docs/goal5043_public_device_column_buffer_contract_2026-07-05.md`
- implementation:
  - `src/rtdsl/device_column_row_buffer.py`
  - `src/rtdsl/__init__.py`
  - `tests/goal5043_public_device_column_buffer_contract_test.py`
- prior gates:
  - `history/internal_docs/goal5041_v2_14_4_device_columnar_api_design_and_implementation_plan_2026-07-05.md`
  - `history/internal_docs/goal5042_existing_asset_inventory_and_api_mapping_2026-07-05.md`
  - `history/internal_docs/claude_review_goal5042_asset_inventory_and_api_mapping_2026-07-05.md`

Requested verdict label:

```text
approve_goal5043_public_device_column_buffer_contract
```

Alternative verdict labels:

```text
revise_goal5043_before_prepared_session_contract
fail_goal5043_due_to_self_declared_residency
fail_goal5043_due_to_overpromoting_internal_row_buffer
```

## Review Questions

1. Does `DeviceColumnBuffer` correctly wrap the existing `RtdlDeviceColumnRowBuffer` substrate rather than creating a competing fifth columnar surface?

2. Are the public exports appropriately limited to the new clean API names, while old adapter names remain importable but absent from `rt.__all__`?

3. Does the implementation preserve the existing four-state stream-ordering vocabulary:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

4. Does device-residency remain derived from actual column interfaces and `materializes_host_rows_for_bridge`, rather than app self-declaration?

5. Does the metadata make the public claim boundary clear:

```text
public_speedup_claim_authorized = false
whole_app_speedup_claim_authorized = false
true_zero_copy_claim_authorized = false
app_specific_schema_allowed = false
residency_self_declared = false
```

6. Is the context-manager/owner lifetime behavior acceptable, including owned-owner close exactly once and borrowed-owner non-closure?

7. Does the partner handoff path correctly reuse the existing v2.6 neutral handoff and fail closed for host-materialized buffers?

8. Do the tests sufficiently cover public exports, old internal-name boundary, four-state vocabulary, residency derivation, host-materialized rejection, lifetime close behavior, and invalid-state failures?

9. Is it acceptable that Goal5043 makes no GPU/POD performance claim and runs only local contract tests?

10. Should Goal5043 close as:

```text
completed_public_device_column_buffer_contract
```

and authorize Goal5044?
