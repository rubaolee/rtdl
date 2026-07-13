# Claude Review - Goal5042 Asset Inventory And API Mapping

Date: 2026-07-05

Verdict:

```text
approve_goal5042_asset_inventory_and_api_mapping
```

## Summary

Claude verified the report's load-bearing claims against the source tree and approved Goal5042.  The only issue was a non-blocking traceability nit: the RayJoin scan-count table was described next to an `rg -o` unique-token command, while its values tracked the line-based scan.  The Goal5042 report has been amended to label the table as line-based counts.

## Verified Claims

- `columnar_partner.py` contains the quoted blocker text: current OptiX compatibility payloads store host scalar `row_values`, grouped count/sum reductions read host `row_values`, and native execution defaults to unauthorized.
- The four stream-ordering states exist in both `device_column_row_buffer.py` and `hit_stream_handoff.py`:

```text
not_proven
same_stream
producer_event_waited_by_consumer
host_synchronized_before_consumer
```

- `run_cuda_lexsort_i64_f64_i64_i64_device` exists, is generic/app-agnostic, and is fail-closed when the native symbol is unavailable.
- `RtdlDeviceColumnRowBuffer` is a justified substrate for public `DeviceColumnBuffer`.
- The RayJoin naming debt table covers Python, OptiX native, Embree native, env-var bridges, and app code.  `wrap_with_public_alias_defer_native_rename` is the correct conservative choice for existing ABI symbols.
- `device_group_by` should remain internal/experimental until a true device-resident reduce path passes POD verification.

## Non-Blocking Note

The scan-count table needed a labeling correction.  This does not affect the substantive conclusion that RayJoin-named implementation debt is large and real.

## Closeout

Goal5042 may close as:

```text
completed_asset_inventory_for_v2_14_4_api
```

Next authorized goal:

```text
Goal5043 - Public DeviceColumnBuffer Contract
```
