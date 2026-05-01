# Goal1164 Two-AI Consensus - RTX Pod Batch

Date: 2026-04-30

## Verdict

ACCEPT with explicit boundaries.

Codex and Gemini agree that the Goal1164 RTX A5000 pod batch is valid runtime evidence for the current prepared/native OptiX app paths, and that the report is technically honest.

## Evidence Reviewed

- `docs/reports/goal1164_rtx_pod_batch_2026-04-30/goal1164_rtx_pod_batch_report_2026-04-30.md`
- `docs/reports/goal1164_rtx_pod_batch_2026-04-30/smoke/summary_with_outlier_rerun.json`
- `docs/reports/goal1164_rtx_pod_batch_2026-04-30/timed_medium/summary.json`
- `docs/reports/goal1164_rtx_pod_batch_2026-04-30/recovery/summary.json`
- `docs/reports/goal1164_rtx_pod_batch_2026-04-30/jaccard_sweep/`
- Gemini review: `docs/reports/goal1164_gemini_rtx_pod_batch_review_2026-04-30.md`
- Runtime patch: `src/native/optix/rtdl_optix_core.cpp`

## Consensus Points

- Compact RTX smoke ran successfully for all listed app/gate entries after the outlier command was rerun with the app-supported CLI surface.
- ANN candidate search and robot collision are functional on RTX OptiX, but current whole-app scaling is a bottleneck: ANN timed out at 65,536 copies and robot timed out at 262,144 poses, while smaller recovery sizes passed but were slow.
- Polygon Jaccard is not ready for broad large-scale public speedup wording. Chunk size 256 missed candidates, while chunk size 8192 overflowed LSI output capacity. Safe chunk sizes 512, 1024, 2048, and 4096 passed for the tested 8,192-copy fixture.
- The CUDA primary-context patch is reasonable for CUDA 13 headers with driver 550 and should remain.
- The nvcc fallback path is necessary for this pod because the validated execution path used `RTDL_OPTIX_PTX_COMPILER=nvcc` and OptiX headers v8.0.0.

## Boundary Notes

- This goal validates runtime execution and identifies performance bottlenecks. It does not authorize public speedup wording by itself.
- The pod run did not validate NVRTC as the final OptiX PTX path. NVRTC needed Linux architecture predefines to compile headers, but the successful app runs used the nvcc PTX compiler path.
- OptiX 8.0 headers were required on the driver 550 pod; OptiX 8.1 and 9.1 headers produced unsupported ABI errors.

## Required Follow-Up

- Add or retain documentation that cloud/pod OptiX runs may need SDK/header pinning to driver-compatible OptiX headers.
- Treat ANN and robot as performance-work items before any large-scale whole-app speedup claim.
- Fix or document polygon Jaccard chunk-boundary semantics before presenting arbitrary chunking as safe.
