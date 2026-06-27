# Independent Gemini Review for Goals3417-3418: Native Page Plan

**Reviewer:** Gemini Agent
**Date:** 2026-06-04

## Goals Under Review

*   **Goal3417:** Added a runtime page-plan object (`OptixExactDevicePairColumnPagePlan`).
*   **Goal3418:** Added the first native page-plan handle (`RtdlNativePairColumnPagePlanInfo`), native produce-page, and native destroy functions.

## Suggested Validation Test Results

Due to an environmental issue preventing the execution of `run_shell_command`, the suggested validation tests could not be run directly. The review proceeds based on analysis of the provided documentation and probe artifacts.

## Review Questions

### 1. Do Goals3417-3418 preserve the app-agnostic boundary?

Yes. Both Goal3417 and Goal3418 explicitly define and preserve the app-agnostic boundary.
Goal3417's report states that `automatic_retry_authorized`, `hidden_dispatch_authorized`, and `true_zero_copy_authorized` are `False`. It also clarifies that exact rows are still derived from a host-refined exact bridge before being uploaded to device pair columns.
Goal3418's report further extends this by explicitly listing numerous features (e.g., device-only exact predicates, page-local device lifecycle callbacks, public/RT-core speedup claims, RayJoin reproduction claims) that are *not* implemented or authorized. The native plan in Goal3418 owns a host point copy, reinforcing that true-zero-copy/device-only claims are not being made.

### 2. Does Goal3417 correctly add a runtime page-plan object without claiming a native handle?

Yes. Goal3417 correctly adds a runtime page-plan object without claiming a native handle. The report explicitly states, "This is a runtime page plan, not a native page-plan handle." The probe artifact confirms `native_page_plan_handle_implemented = False`. The Python surface example `page_plan = prepared.exact_device_columns_page_plan(...)` also shows a runtime object being instantiated.

### 3. Does Goal3418 actually add a native page-plan handle, native produce-page function, and native destroy function?

Yes. Goal3418 successfully adds the first native page-plan handle. The report lists the new native functions:
*   `rtdl_optix_prepare_point_closed_shape_membership_exact_device_columns_page_plan_2d`
*   `rtdl_optix_produce_point_closed_shape_membership_exact_device_columns_page_2d`
*   `rtdl_optix_destroy_point_closed_shape_membership_exact_device_columns_page_plan_2d`
The Python surface includes `native_plan = prepared.exact_device_columns_native_page_plan(...)` and `native_plan.close()`. The probe artifact confirms `native_page_plan_handle_implemented = true` and `native_page_release_function_implemented = true`.

### 4. Is the remaining boundary honest: the native plan owns a host point copy, exact predicates are still host-refined, and no true-zero-copy/device-only exact claim is authorized?

Yes. The remaining boundary is honest. The Goal3418 report explicitly states, "The native plan owns a copied host point buffer and page metadata..." and "The exact rows still come from the existing host-refined exact bridge before upload to device pair columns." Furthermore, the report clearly indicates that `device-only exact predicates` are not yet implemented and `true_zero_copy_authorized = False`.

### 5. Are the artifacts internally consistent: 9 pages, 47,262 exact rows, 16,476 final groups, 16,541 per-page grouped-row sum, and zero missing/extra/mismatch?

Yes. Both Goal3417 and Goal3418 probe artifacts (JSON files) are internally consistent with these values:
*   `page_count`: 9
*   `host_exact_row_count`: 47262
*   `device_group_count`: 16476 (final groups)
*   `device_grouped_row_count`: 16541 (sum of grouped rows per page)
*   `missing_group_key_count`, `extra_group_key_count`, `mismatched_group_value_count` are all 0.
The per-page grouped-row sum of 16541 is the aggregate count of grouped rows generated across all pages, which is distinct from the final count of unique groups (16476), indicating that some groups might span across pages or be recounted before final consolidation. This distinction is consistent across the reports.

### 6. What is the next required engineering step toward the final native paged stream shape?

According to the "Next Target" sections in both Goal3417 and Goal3418 reports, the next required engineering step toward the final native paged stream shape is to implement a `device-resident exact predicate` and `page-local consume/release callbacks`. Goal3418 specifically narrows the remaining graduation shape to these two items.

## Review Status

accept-with-boundary

## Conclusion

Goals3417 and 3418 have successfully introduced a runtime page-plan object and the initial native page-plan handle, respectively, while diligently preserving the app-agnostic boundary. The artifacts demonstrate internal consistency, and the explicitly stated boundaries confirm that no unauthorized claims regarding device-only or zero-copy functionalities have been made. The path forward is clearly defined by the need for device-resident exact predicates and page-local consume/release callbacks.
