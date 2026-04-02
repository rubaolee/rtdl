# Goal 43 Claude Audit: OptiX GPU Validation — Post-Fix Review

**Date:** 2026-04-02  
**Auditor:** Claude (claude-sonnet-4-6)  
**Reviewed commits:** `5b6f436`, `1f8b305`, `f15bcd4`  
**Remote host:** `192.168.1.20` (lx1, Ubuntu 24.04, x86_64)  
**GPU:** NVIDIA GeForce GTX 1070  
**OptiX runtime:** 9.0.0  
**PTX compiler path:** `nvcc` (`/usr/bin/nvcc`)

---

## Scope

This audit satisfies the deferred review requested in `goal_43_optix_gpu_validation.md`.
It covers three required items:

1. The final `overlay` parity fix in `src/native/rtdl_optix.cpp`
2. The shutdown-stability fix (teardown segfault prevention)
3. The validated remote rerun showing all 8 Goal 43 targets parity-clean on `192.168.1.20`

---

## Finding 1: Overlay Parity Fix

**Verdict: APPROVE**

**Root cause of original bug:** The CPU PIP supplement was iterating over ALL vertices
of each left/right polygon and testing containment. The CPU oracle
(`overlay_compose_cpu`) checks only the first vertex of each polygon. This caused
the OptiX path to set `requires_pip = 1` on cases where the oracle set `0`.

Pre-fix mismatch on `authored_overlay_minimal`:
- CPU: `{'requires_lsi': 1, 'requires_pip': 0}`
- OptiX: `{'requires_lsi': 1, 'requires_pip': 1}`

**The fix** (commit `1f8b305`): replaced all-vertex loops with first-vertex-only
checks on both left and right sides:

```cpp
// CPU PIP supplement: match the current RTDL oracle semantics exactly.
// overlay_compose_cpu checks only the first vertex of each polygon.
if (left_polys[li].vertex_count > 0) {
    float lxv = (float)left_verts_xy[left_polys[li].vertex_offset * 2];
    float lyv = (float)left_verts_xy[left_polys[li].vertex_offset * 2 + 1];
    ...
}
if (!found && right_polys[ri].vertex_count > 0) {
    float rxv = (float)right_verts_xy[right_polys[ri].vertex_offset * 2];
    ...
}
```

This exactly mirrors oracle semantics. The code comment is accurate. The fix is
correct and fully consistent with the RTDL oracle contract.

---

## Finding 2: Teardown Stability Fix

**Verdict: APPROVE**

**Root cause of original bug:** Pipeline structs held `std::unique_ptr<PipelineHolder>`
as static globals. On process exit, static destructors ran after the Python
interpreter and CUDA/OptiX runtime had begun teardown, hitting invalid driver
state and segfaulting.

**The fix** (commit `1f8b305`): all five pipeline structs changed to raw pointers,
pipeline objects intentionally leaked via `.release()`:

```cpp
struct LsiPipeline {
    PipelineHolder* pipe = nullptr;  // was: std::unique_ptr<PipelineHolder>
    std::once_flag   init;
};
// ... same for Pip, Overlay, RayHitCount, SegPoly

g_lsi.pipe = build_pipeline(...).release();  // destructor intentionally never runs
```

The leak is bounded (at most 5 `PipelineHolder` objects, one per workload type),
does not grow at runtime, and is fully reclaimed by the OS on exit. This is the
standard and correct approach for preventing crash-on-exit with GPU runtimes
embedded in a Python process. The fix is sound.

---

## Finding 3: Post-Fix Remote Rerun on `192.168.1.20`

**Verdict: APPROVE**

Both fixes were confirmed present in `~/work/rtdl_python_only/src/native/rtdl_optix.cpp`
on the remote host (applied directly; git not yet pulled to that point). The
validation harness was re-executed and results written to
`~/work/rtdl_python_only/build/goal43_optix_validation.json`.

### Parity table — all 8 targets

| # | Workload | Dataset | CPU rows | OptiX rows | Parity |
|---|----------|---------|----------|------------|--------|
| 1 | `lsi` | `authored_lsi_minimal` | 2 | 2 | **true** |
| 2 | `pip` | `authored_pip_minimal` | 2 | 2 | **true** |
| 3 | `overlay` | `authored_overlay_minimal` | 1 | 1 | **true** ✓ fixed |
| 4 | `ray_tri_hitcount` | `authored_ray_tri_minimal` | 2 | 2 | **true** |
| 5 | `segment_polygon_hitcount` | `authored_segment_polygon_minimal` | 2 | 2 | **true** |
| 6 | `point_nearest_segment` | `authored_point_nearest_segment_minimal` | 2 | 2 | **true** |
| 7 | `lsi` | `derived/br_county_subset_segments_tiled_x8` | 0 | 0 | **true** |
| 8 | `pip` | `derived/br_county_subset_polygons_tiled_x8` | 384 | 384 | **true** |

**8 / 8 parity-clean.** `overlay` moved from failing to clean after the fix.

### Wall times (indicative)

| Workload | CPU (s) | OptiX (s) |
|----------|---------|-----------|
| lsi authored | 0.0016 | 0.463 |
| pip authored | 0.0002 | 0.304 |
| overlay authored | 0.0001 | 0.297 |
| ray_tri_hitcount | 0.0001 | 0.295 |
| segment_polygon_hitcount | 0.0001 | 0.306 |
| point_nearest_segment | 0.0001 | 0.228 |
| lsi derived x8 | 0.0002 | 0.001 |
| pip derived x8 | 0.0007 | 0.001 |

OptiX first-call overhead dominates for the tiny authored cases (JIT + pipeline
init). This is expected and does not indicate a correctness or performance problem
at this stage.

---

## Current boundary (confirmed)

- Host: `192.168.1.20` (lx1), GTX 1070, driver `580.126.09`
- OptiX runtime: `9.0`, SDK headers pinned to `v9.0.0`
- PTX compiler: `RTDL_OPTIX_PTX_COMPILER=nvcc`, `RTDL_NVCC=/usr/bin/nvcc`
- Default NVRTC path: **not yet the trusted path on this host** (unchanged)
- Teardown: no crash observed after validation run

---

## Overall verdict: **APPROVE**

All three required audit items are satisfied:

- overlay parity fix is correct and matches oracle semantics
- teardown stability fix is sound and bounded
- post-fix rerun on `192.168.1.20` shows 8/8 parity-clean

The corrected Goal 43 state is **acceptable for continued OptiX development**.
The backend may proceed from validation into broader GPU testing. The NVRTC
default path remains an open item for a future goal, but it does not block
forward progress on the `nvcc` fallback path.
