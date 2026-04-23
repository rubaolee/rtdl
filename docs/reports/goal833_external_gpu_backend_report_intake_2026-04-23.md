# Goal833 External GPU Backend Report Intake

Date: 2026-04-23

## Purpose

Goal833 records two external Gemini reports that were present as untracked
files in `/Users/rl2025/rtdl_python_only/docs/reports`. External inputs must be
preserved and interpreted, not left loose in the worktree.

## External Reports Ingested

- `/Users/rl2025/rtdl_python_only/docs/reports/goal727_gemini_optix_rtx_engine_polish_review_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/gemini_vulkan_hiprt_status_report_2026-04-23.md`

## Report 1: Goal727 Gemini OptiX/RTX Engine Polish Review

Reviewer: Gemini 3.1 Pro

Verdict: `ACCEPT`

Key points:

- Outlier and DBSCAN prepared fixed-radius scalar summary paths are described
  as genuine OptiX custom-AABB traversal paths, not row-materialization paths.
- Robot collision prepared pose flags / hit counts are described as genuine
  ray/triangle any-hit traversal with native reduction.
- Database analytics uses an OptiX DB bitset/probe path, but remains bounded
  by prepared DB sub-path semantics.
- Gemini explicitly preserves the boundary that Hausdorff, graph, and other
  compute/fallback paths are not magically promoted.

Codex intake interpretation:

- This report supports the current active candidate list in the NVIDIA WIP
  report and Goal832 baseline contract.
- It does not authorize public speedup claims by itself.
- It is consistent with the current status where robot, outlier, and DBSCAN
  prepared scalar sub-paths are `rt_core_ready`, while broader apps remain
  bounded.

## Report 2: Gemini Vulkan/HIPRT Status Report

Reviewer: Gemini, based on the RTX 4090 cloud node status.

Verdict: Vulkan and HIPRT were unavailable on that node.

Key points:

- Vulkan build failed because `shaderc/shaderc.h` was missing.
- Vulkan runtime also failed due incompatible/misconfigured Vulkan ICD.
- HIPRT build failed because the HIPRT SDK header was missing at the expected
  vendor path.
- Vulkan and HIPRT tests skipped safely instead of crashing.

Codex intake interpretation:

- The RTX 4090 cloud evidence should be treated as OptiX-only for GPU
  backend performance and correctness.
- No Vulkan/HIPRT comparison should be inferred from that cloud session.
- This supports the local-first policy: fix/install dependencies locally or in
  a prepared cloud image before spending another paid GPU session on
  cross-backend comparisons.

## Consensus Status

This intake has 2-AI support:

- Gemini authored the two external reports.
- Codex reviewed and recorded the reports in this intake.

No new Claude verdict is claimed here.

## Resulting Action Items

1. Keep the OptiX active claim candidates limited to the prepared scalar
   sub-paths already documented.
2. Treat the RTX 4090 Vulkan/HIPRT status as unavailable, not as poor
   performance.
3. Do not run another paid cloud cross-backend batch until Vulkan `shaderc`,
   Vulkan ICD health, and HIPRT SDK paths are preflighted.
4. Keep all public documentation from implying that Vulkan or HIPRT were
   validated in that RTX 4090 session.

## Verdict

ACCEPT as external input intake. No cloud action was taken.
