# Goal 695/696 Dev-AI Handoff: OptiX Fixed-Radius Summary Path

Review the current `main` state after Goals 694-696 and continue only within the accepted boundaries.

## Required Context

Read these files first:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal694_optix_rt_core_redesign_plan_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal694_codex_review_of_gemini_rt_core_redesign_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal694_claude_review_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal695_optix_fixed_radius_summary_prototype_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal695_claude_review_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal695_gemini_flash_review_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal696_optix_fixed_radius_summary_linux_validation_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal696_optix_fixed_radius_summary_linux_validation_2026-04-21.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal696_claude_review_2026-04-21.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal696_gemini_flash_review_2026-04-21.md`

## Current Accepted State

Goal695 already implemented the first accepted OptiX redesign slice:

- Native C ABI: `rtdl_optix_run_fixed_radius_count_threshold`
- Python helper: `rtdsl.fixed_radius_count_threshold_2d_optix(...)`
- Outlier app mode:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_outlier_detection_app.py`
  - `--backend optix --optix-summary-mode rt_count_threshold`
- DBSCAN app mode:
  - `/Users/rl2025/rtdl_python_only/examples/rtdl_dbscan_clustering_app.py`
  - `--backend optix --optix-summary-mode rt_core_flags`

Goal696 validated this on Linux:

- Host: `lestat-lx1`
- Commit: `c569e71`
- Build: `make build-optix OPTIX_PREFIX=$HOME/vendor/optix-dev CUDA_PREFIX=/usr NVCC=/usr/bin/nvcc`
- OptiX: `9.0.0`
- Focused tests: `15` OK
- Outlier summary: oracle pass, zero neighbor-row materialization
- DBSCAN core flags: oracle pass, zero neighbor-row materialization

## Strict Boundary

Do not claim a broad OptiX RT-core speedup from Goal696. The Linux GPU was a GTX 1070, which has no RT cores. The evidence proves native OptiX build/correctness and bounded whole-call behavior, not RTX-class acceleration.

Do not change app performance classifications yet. Outlier detection and DBSCAN remain `cuda_through_optix` until RTX-class phase-split benchmarks justify a change.

Do not implement or claim the following as solved by the 2.5D mapping:

- Hausdorff distance
- KNN/ANN top-k ranking
- Barnes-Hut force accumulation

The accepted consensus says these are not ready. In particular, Barnes-Hut cannot rely on "missed nodes contributing mass" because RT hardware does not enumerate misses.

## Next Safe Work Items

If asked to continue this line, the next safe tasks are:

1. Add an RTX-class phase profiler for only the fixed-radius summary path.
2. Profile separate phases:
   - Python input construction
   - packing
   - BVH build
   - OptiX launch/traversal
   - copy-back
   - scalar/app postprocess
3. Compare:
   - existing OptiX row path
   - new OptiX summary path
   - CPU/oracle label path where appropriate
4. Keep correctness gates:
   - outlier label parity
   - DBSCAN core-flag parity
   - no full DBSCAN cluster-expansion claim in summary mode
5. Only after RTX-class data exists, decide whether app classifications should change.

## Do Not Do

- Do not silently fall back from OptiX summary mode to Python rows.
- Do not emit `tuple[dict, ...]` from the new native summary path when a scalar/flag output is sufficient.
- Do not use GTX 1070 data as RT-core evidence.
- Do not promote Hausdorff/KNN/Barnes-Hut to `optix_traversal` based on Goal694's speculative plan.
- Do not remove the existing row paths; they remain the full-neighborhood compatibility path.

## Expected Output

Write a short report under `/Users/rl2025/rtdl_python_only/docs/reports/` that states:

- what was tested or implemented;
- whether it stayed within the accepted fixed-radius scope;
- whether any app classification changed;
- whether the result is correctness-only, GTX whole-call timing, or RTX-class speed evidence.

