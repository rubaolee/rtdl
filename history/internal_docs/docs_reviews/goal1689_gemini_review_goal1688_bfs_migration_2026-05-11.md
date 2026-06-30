# Gemini Independent Review: Goal 1688 BFS Migration

**Date:** 2026-05-11
**Reviewer:** Gemini / Antigravity (Independent External AI)

## 1. Context and Independence
This document serves as an independent external review of the Goal 1688 migration ("BFS-To-Frontier-Edge-Traversal Native Migration"). This audit was performed independently by Gemini, fulfilling the requirement for distinct 2-AI consensus on the structural direction of the codebase.

## 2. Leakage Elimination Verification
The migration targeted the `bfs` native leakage family. 
- **Eliminated:** Eight (8) of the ten `bfs`-shaped native callables/exports across Embree, HIPRT, OptiX, Oracle, and Vulkan have been successfully renamed to `frontier_edge_traversal_packet` semantics. Internal kernel filename hints (like HIPRT's `.cu` reference) were also correctly scrubbed from the native core files.
- **Deferred / Quarantined:** Two (2) Apple RT discover variants (`rtdl_apple_rt_run_bfs_discover_compute` and `rtdl_bfs_discover`) remain. The migration report correctly identifies that because the Metal kernel source is embedded as a runtime string compiled through `MTLLibrary`, renaming them requires touching both the embedded source and the lookup site simultaneously. Deferring this to a dedicated narrow Apple RT slice is technically sound and responsibly avoids disrupting the broader five-backend rename.
- **Python Row Structures:** The retention of `RtdlBfsRow`, `RtdlBfsExpandRow`, and `_RtdlFrontierVertex` as CamelCase types is acceptable. They do not violate the `\brtdl_<lowercase>_` regex rules for exported ABI symbols and reside purely at the struct definition / ctypes binding layer.

## 3. Python Compatibility
Python backward compatibility is fully preserved.
- The Python layer continues to cleanly expose its existing BFS helpers (e.g., `rt.run_embree(rtdl_graph_bfs.bfs_expand_kernel, **case)`), enforcing the rule that domain semantics belong in Python, not native code.
- The ctypes binding strings across `embree_runtime.py`, `hiprt_runtime.py`, `optix_runtime.py`, `oracle_runtime.py`, and `vulkan_runtime.py` were correctly repointed to the new generic names.
- A local validation execution of the verification suite (`tests.goal1688_bfs_to_frontier_edge_traversal_native_migration_test` and `tests.goal1603_v1_6_stable_native_path_app_leakage_audit_test`) passed successfully, confirming no disruptions in runtime binding or execution logic.

## 4. Updated Counts
The reported counts accurately reflect the post-migration source state:
- **Remaining app-shaped callable/export symbols:** 75 (down from 83)
- **Remaining `bfs` family unique symbols:** 2 (Apple RT discover, properly tracked and deferred)
- **Remaining Blocking Families:** `db`, `polygon`, `knn`, and the 2 pending Apple RT `bfs` symbols.

## 5. Verdict and Release Claim
**Verdict:** `accept-with-boundary`. 

The source-level migration successfully achieves the goal of decoupling graph semantics from the primary backends' C++/CUDA/Vulkan entry points. The decision to defer the Apple RT string-embedded symbols is justified and well-documented.

**Release Readiness:** `needs-more-evidence`. 
As correctly stated in the Goal 1688 report, the claim that "RTDL native internals are fully app-agnostic" remains strictly **blocked**. The project cannot authorize v1.8/v2.0 app-agnostic claims until the 75 remaining legacy symbols are structurally eliminated or mechanically quarantined, and full pod validation confirms the runtime hardware execution.
