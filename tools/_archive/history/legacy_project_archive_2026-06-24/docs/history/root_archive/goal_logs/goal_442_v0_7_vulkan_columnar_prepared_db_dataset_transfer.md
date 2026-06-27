# Goal 442: v0.7 Vulkan Columnar Prepared DB Dataset Transfer

## Goal

Add the native columnar prepared DB dataset transfer path to Vulkan, following
the accepted Goal 440 Embree and Goal 441 OptiX patterns.

## Required Outcome

- Add a Vulkan C ABI for creating a prepared DB dataset from column-major field
  arrays.
- Keep the existing row-struct compatibility ABI intact.
- Add a Python opt-in transfer mode:
  - `prepare_vulkan_db_dataset(..., transfer="columnar")`
- Prove row/columnar parity for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Measure prepare-time effect against the existing row-struct transfer path on
  Linux.
- Preserve the claim boundary:
  - this is an ingestion-path improvement, not a DBMS feature
  - this goal only closes Vulkan columnar transfer

## Review Requirement

This goal requires at least 2-AI consensus before closure.
