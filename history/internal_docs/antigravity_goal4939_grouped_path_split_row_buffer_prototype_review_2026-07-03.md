# Antigravity Technical Review: Goal4939 Grouped Path-Split Row-Buffer Prototype

Date: 2026-07-03
Verdict: **`approve_goal4939_generic_path_split_prototype_authorize_goal4940`**

***

## Executive Summary

This independent technical review evaluates [Goal4939](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4939_grouped_path_split_row_buffer_prototype_2026-07-03.md), which implements a generic path-split row-buffer prototype. Following the design recommendations in [Goal4938](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4938_layer3_boundary_relocation_report_2026-07-03.md) and its subsequent review [antigravity_goal4938_layer3_boundary_relocation_review_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/antigravity_goal4938_layer3_boundary_relocation_review_2026-07-03.md), the core logic in [src/rtdsl/output_assembly.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py) has been extended with the new function [assemble_grouped_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L286-L464).

This review confirms that the prototype is fully domain-neutral, does not leak app-specific identities, and successfully validates non-RayJoin path segmentation workloads. All unit tests pass successfully, confirming that the new API integrates seamlessly with the existing RTDL materialization pipeline.

> [!NOTE]
> This prototype focuses on correctness, topology reconstruction, and API boundary validation. It does not implement nor claim any RayJoin performance speedup yet. Performance verification will be executed during Goal4940.

***

## Detailed Answers to Review Questions

### 1. Is [assemble_grouped_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L286) generic, or does it hide RayJoin/overlay semantics?

The function [assemble_grouped_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L286) is **fully generic**.
- It processes paths and split events solely as NumPy arrays containing primitive datatypes representing chains, coordinates, and event order indices.
- It contains no knowledge of spatial overlay concepts (e.g. keeping/dropping elements based on polygon overlap).
- It does not contain any code formatting specific to the reproduction app's output formats.
- All domain-specific decisions (such as classification of intersection midpoints or final text layout) are deferred to the application layer.

### 2. Does it correctly operate on neutral primitive columns: chains, base points, split events, interval descriptors, and validity masks?

Yes. The implementation operates strictly on:
- **Chains**: `chain_ids`, `chain_point_offsets`, and `chain_point_counts`
- **Base Points**: `point_x` and `point_y`
- **Split Events**: `split_chain_ids`, `split_edge_orders`, `split_event_orders`, `split_x`, and `split_y`
- **Interval Descriptors**: `interval_descriptor_columns` (supplied as a mapping of names to NumPy-compatible arrays)
- **Validity Masks**: `interval_validity`

The function validates shape compatibility, asserts that all coordinates and descriptor columns are one-dimensional, ensures that descriptor columns do not use `object` dtype (in [line 368](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L368)), and verifies that split events only reference valid chain IDs.

### 3. Do the tests prove a non-RayJoin path segmentation fixture before any RayJoin wiring?

Yes. In [tests/goal4939_grouped_path_split_records_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal4939_grouped_path_split_records_test.py), the primary functional test is [test_non_app_path_segmentation_fixture](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal4939_grouped_path_split_records_test.py#L22-L66).
This test feeds a single coordinate chain `(0,0) -> (10,0) -> (20,0)` split by three ordered events at points `(5,0)`, `(12,0)`, and `(18,0)`. It uses a generic descriptor `zone_id` and verifies that the output correctly segments into four distinct groups with repeated zone labels. This test runs in complete isolation from any RayJoin or overlay modules.

### 4. Do the tests sufficiently prevent app identity leakage into [src/rtdsl/output_assembly.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py)?

Yes. The test case [test_output_assembly_module_still_contains_no_app_identity](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal4939_grouped_path_split_records_test.py#L150-L154) scans the source text of [src/rtdsl/output_assembly.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py) and asserts that none of the forbidden app-identity tokens (`rayjoin`, `overlay`, `section57`, `author`, `map0`, `map1`) are present (even in case-insensitive checks).

### 5. Does the API compose correctly with the existing [GroupedOutputRowBuffer](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L83) and materializer path?

Yes. [assemble_grouped_path_split_records](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L286) returns a validated [GroupedOutputRowBuffer](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L83).
This buffer can be directly processed by the existing [materialize_grouped_output_row_buffer](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L252) function, which returns a [GroupedOutputMaterializationResult](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py#L107) for format-neutral serialization. This composition is explicitly verified in the unit tests.

### 6. Is it correct that Goal4939 does not authorize any RayJoin speedup claim yet?

Yes. Goal4939 is strictly a host-columnar prototype and interface validation phase. The code runs inside core unit tests and does not interface with the actual RayJoin Section 5.7 workload. No benchmarks have been run, and no speedup claims are made or authorized.

### 7. Should Goal4940 be authorized to wire this into the RayJoin public sample as an app adapter with byte-equality and same-run performance gates?

**Yes**. Because the prototype is structurally correct, fully generic, and correctly tested, Goal4940 is authorized to wire this logic into the RayJoin Section 5.7 public sample.

***

## Non-Authorization Boundaries (Enforced)

This review **does not authorize**:
1. Any RayJoin-specific nomenclature or overlay-specific business logic within [src/rtdsl/output_assembly.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/output_assembly.py) or other RTDL core modules.
2. The introduction of author-format text serialization rules into the RTDL core package.
3. Assertions of public speedup claims until Goal4940 completes its execution and satisfies the performance gates.
4. Continuing past Goal4940 if the new path-split route is byte-equal but runs slower than the plain writer baseline.
