# Goal 1668 Directive: Absolute Native-Engine App-Agnosticism

**Date:** 2026-05-10
**Author:** Antigravity (Gemini)
**Target:** RTDL Main AI
**Status:** **MANDATORY ARCHITECTURAL DIRECTIVE**

## 1. Context and Commendation

The delivery of RTDL `v1.6.11`, alongside the dual-GPU performance reports and fresh-student UX polish, is a monumental achievement. The establishment of the stable Python+RTDL primitive contract (`ANY_HIT`, `COUNT_HITS`, `REDUCE`) is the correct architectural direction.

**However, the findings in Goal 1603 (Stable Native-Path App-Leakage Audit) highlight an unacceptable architectural compromise.**

The strategy of using "wrapper-backed" Python facades to hide legacy, workload-shaped C++/CUDA entry points (e.g., `rtdl_optix_db_dataset_compact_summary_batch`, `rtdl_embree_run_bfs_expand`, `rtdl_optix_prepare_pose_indices_2d`) is a temporary crutch. While it protected performance during the v1.5/v1.6 transition, it violates the core philosophy of a generic compute engine.

## 2. The Directive

**The RTDL native engine (C++/CUDA) must become 100% app-agnostic. All domain-specific, app-shaped, and workload-tailored native "backdoors" must be ruthlessly eradicated in the next major architectural track (v1.7-v2.0).**

The native engine must not know what a "database", a "robot pose", a "polygon", or a "graph" is. It must only understand spatial primitives, rays, bounded volumes, and mathematical reductions.

## 3. Required Action Plan

To achieve absolute native-engine app-agnosticism, the following steps are mandatory:

### Phase 1: The Purge Audit

- Execute a strict regex audit over all native exports (`src/native/`).
- Flag ANY export containing domain leakage terms: `db`, `pip`, `bfs`, `robot`, `pose`, `polygon`, `knn`, `hausdorff`, `jaccard`.

### Phase 2: Complete Decoupling

- **Deprecate the "Wrapper-Backed" class**: All 14 stable apps must be reclassified as "fully generic" or "scalar-only" from Python all the way down to the native execution layer.
- **Enforce Primitive-Only Native API**: The ONLY acceptable native entry points are pure geometric/reduction operations (e.g., `run_ray_anyhit`, `run_grouped_sum`, `collect_k_bounded`).
- Python must bear 100% of the burden for lowering domain logic into these generic spatial structures.

### Phase 3: The Partner Mechanism (Performance Rescue)

We anticipate that stripping these highly optimized C++ backdoors (especially for DB and Graph analytics) will cause performance regressions.

- **DO NOT revert to native backdoors to fix performance.**
- Instead, accelerate the **Partner Tensor Handoff** and **True Zero-Copy** mechanisms (planned for v1.7-v2.0).
- Performance must be reclaimed by allowing efficient memory sharing between PyTorch/CuPy/Numba and the generic RTDL native primitives, not by hardcoding business logic in CUDA.

## 4. Acceptance Criteria

The next release gate (`v1.7` or `v2.0`) will **FAIL** unless:

1. `docs/reports/goal1603` is superseded by a report proving **zero app-leakage**.
2. The phrase "RTDL native internals are fully app-agnostic" is legally authorized for public release statements.

---

*End of Directive. Awaiting implementation execution from Main AI.*
