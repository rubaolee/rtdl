# Goal 440: v0.7 Embree Columnar Prepared DB Dataset Transfer

## Goal

Add the first native columnar prepared DB dataset transfer path, bounded to
Embree first.

## Required Outcome

- Add an Embree C ABI for creating a prepared DB dataset from column-major field
  arrays.
- Keep the existing row-struct compatibility ABI intact.
- Add a Python opt-in transfer mode:
  - `prepare_embree_db_dataset(..., transfer="columnar")`
- Prove row/columnar parity for:
  - `conjunctive_scan`
  - `grouped_count`
  - `grouped_sum`
- Measure prepare-time effect against the existing row-struct transfer path.
- Preserve the claim boundary:
  - this is an ingestion-path improvement, not a DBMS feature
  - OptiX and Vulkan columnar ingestion remain follow-up goals

## Review Requirement

This goal requires at least 2-AI consensus before closure.
