# Gemini Review: Goal1962 Unique-Pair Group Counts

- **Goal:** 1962 (Shared Partner Unique-Pair Group Counts)
- **Verdict:** `accept`
- **Reviewer:** Gemini/Antigravity
- **Date:** 2026-05-14

## Overview

This review audits the implementation of the `partner_group_count_unique_pairs_by_key` primitive in RTDL v2.0. This primitive resolves a specific piece of optimization debt where segment/polygon hit-count de-duplication was performed using a private runtime hook rather than a shared, app-agnostic reduction primitive.

## Verification of Requirements

### 1. Generic Primitive Implementation
Commit `67951efd` successfully added `partner_group_count_unique_pairs_by_key` to `src/rtdsl/partner_adapters.py`. The implementation is correctly branched for both **PyTorch** and **CuPy** backends:
- **PyTorch:** Uses `torch.unique` and `torch.bincount` on encoded pairs.
- **CuPy:** Uses `cupy.unique` and `cupy.bincount`.
- **Zero-Copy:** The primitive operates entirely on native tensors without host-side materialization.

### 2. Architectural Boundaries
The implementation strictly preserves app-agnostic native-engine boundaries. The native engine continues to emit generic `(ray_id, primitive_id)` witness pairs. The interpretation of these pairs as "segment/polygon" hits is handled entirely within the Python partner layer using generic reduction algebra. No domain-specific symbols or logic have leaked into the native OptiX/Embree kernels.

### 3. Adapter Migration
The segment and shape hit-count adapters have been successfully refactored to use the new shared primitive via the `_count_unique_pairs_for_runtime` helper.
- `segment_polygon_hitcount_optix_partner_device_count_columns` now routes through the shared primitive.
- The `native_engine_row_contract` remains `generic_ray_primitive_witness_pairs`, maintaining consistency across the v2.0 primitive layer.

### 4. Compatibility and Fallbacks
The old private runtime hook (`count_unique_pairs_by_ids`) has been retained strictly as a fallback for fake/legacy runtimes used in existing local tests, ensuring no regression in the test suite while promoting the new standard for Torch/CuPy.

### 5. Documentation of Debt
The report `docs/reports/goal1962_partner_unique_pair_group_counts_2026-05-14.md` accurately documents the remaining v2.0 continuation debt, specifically noting that richer continuation algebra (Graph, Polygon Overlay, Hausdorff, KNN, etc.) still requires migration to similar generic partner primitives.

## Verdict

**`accept`**

The implementation is sound, architectural boundaries are respected, and the transition to shared reduction algebra for unique-pair counts is complete for the Torch/CuPy backends.

## Artifacts Verified
- [partner_adapters.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/partner_adapters.py)
- [__init__.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/__init__.py)
- [goal1962_partner_unique_pair_group_counts_test.py](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/goal1962_partner_unique_pair_group_counts_test.py)
- [goal1962_partner_unique_pair_group_counts_2026-05-14.md](file:///c:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/reports/goal1962_partner_unique_pair_group_counts_2026-05-14.md)
