# Codex Review: Goal 436 v0.7 Vulkan Native Prepared DB Dataset

Date: 2026-04-16

## Verdict

ACCEPT, pending external AI review for the required 2-AI consensus.

## Review Findings

No release-blocking issues found.

The implementation satisfies the Goal 436 scope:

- A native Vulkan prepared DB dataset handle is present.
- The handle owns copied table data, primary RT axes, row AABBs, row metadata, and built Vulkan BLAS/TLAS handles.
- The prepared query functions reuse the TLAS for `conjunctive_scan`, `grouped_count`, and `grouped_sum`.
- The Python API exposes a reusable dataset object through `prepare_vulkan_db_dataset`.
- Correctness is checked against Python truth and direct Vulkan on Linux.
- The Linux performance gate includes PostgreSQL setup-once plus repeated-query timing.

## Boundary Check

The performance claim is bounded correctly. Goal 436 proves native Vulkan acceleration-structure reuse and a low repeated-query phase. It does not prove final large-table ingestion performance, because the initial table transfer still uses the compatibility ctypes row encoding path. That caveat is recorded in the Goal 436 report and should remain in release-facing language.

## Evidence Reviewed

- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_prelude.h`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_core.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/native/vulkan/rtdl_vulkan_api.cpp`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/src/rtdsl/__init__.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/tests/goal436_v0_7_vulkan_native_prepared_db_dataset_test.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal436_vulkan_native_prepared_db_dataset_linux_2026-04-16.json`
- `/Users/rl2025/worktrees/rtdl_v0_4_main_publish/docs/reports/goal436_v0_7_vulkan_native_prepared_db_dataset_2026-04-16.md`
