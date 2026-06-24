# Gemini Independent Review: Goal 1690 Apple RT BFS Remainder Migration

**Date:** 2026-05-11
**Reviewer:** Gemini / Antigravity (Independent External AI)

## 1. Context and Independence
This document serves as an independent external review of Goal 1690 ("Apple RT BFS-To-Frontier-Discover Native Migration"). This audit was performed independently by Gemini, satisfying the project's distinct 2-AI consensus requirement.

## 2. Apple RT BFS Leakage Elimination
The migration correctly targeted the remaining two deferred Apple RT native symbols from the broader BFS migration (Goal 1688).
- **Eliminated:** `rtdl_apple_rt_run_bfs_discover_compute` and `rtdl_bfs_discover` have been successfully renamed to `rtdl_apple_rt_run_frontier_discover_compute` and `rtdl_frontier_discover`.
- **Metal Kernel Integrity:** The embedded Metal kernel string and its dynamic lookup function (`newFunctionWithName`) have been consistently updated. The `bfs` term has been entirely scrubbed from the native ABI exports. 
- **Total `bfs` Native Leakage:** Verified to be exactly **0**. The entire `bfs` family is now successfully decoupled from native engine semantics.

## 3. Python Compatibility Verification
Python BFS backward compatibility remains fully intact. 
- The Python layer safely retains the `bfs_discover_apple_rt` public helper and the `"bfs_discover"` string predicate inside the Apple RT Python dispatcher.
- The `ctypes` native binding string correctly routes API calls to the new generic `rtdl_apple_rt_run_frontier_discover_compute` entry point.
- Local execution of the unit test suite (`tests.goal1690_apple_rt_bfs_to_frontier_discover_migration_test` and `tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test`) passed perfectly. This proves that no application-layer Python logic or public BFS semantics were disrupted.

## 4. Updated Counts Confirmation
The leakage counts reported in Goal 1690 accurately reflect the current source repository state:
- **Strict regex unique symbols:** 82 (down from 84)
- **Strict regex occurrences:** 159 (down from 164)
- **Remaining app-shaped callable/export symbols:** 73 (down from 75)
- **`bfs` family unique symbols:** 0

The 73 remaining app-shaped families blocking the release are appropriately confirmed as: `db` (30), `polygon` (29), and `knn` (14).

## 5. Verdict and Release Status
**Verdict:** `accept-with-boundary`. 

The source-level migration of the Apple RT Metal exports correctly finishes the work of Goal 1688. 

**Release Readiness:** `needs-more-evidence`. 
As correctly stated in the Goal 1690 report, the claim that "RTDL native internals are fully app-agnostic" remains strictly **blocked**. The project cannot authorize v1.8/v2.0 app-agnostic claims until the 73 remaining legacy symbols (`db`, `polygon`, `knn`) are eliminated or quarantined, and pod hardware validation is completed.
