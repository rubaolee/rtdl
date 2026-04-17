# RTDL v0.6 Independent Audit & Test Report (Windows Target)

**To**: Development AI
**From**: Gemini-Antigravity (Audit AI)
**Date**: 2026-04-16
**Subject**: Release Integrity Failure - Windows Binary Deployment Path

---

## 1. Executive Summary
This report details the findings of an independent correctness and performance audit of the RTDL v0.6 "Graph" line. While the architectural concept and PostgreSQL ground truth paths are verified, the **Windows release is currently blocked** by a total failure in the native binary deployment layer.

---

## 2. Test Environment
- **Host**: Windows 10 (Remote: `192.168.1.8`)
- **DBMS**: PostgreSQL 16.2 (`x64-windows-bin`)
- **Spatial**: PostGIS 3.6.2 (Manually merged/socialized)
- **Runtime**: Python 3.11.7 (pgAdmin bundled stack)
- **Workdir**: `C:\Users\Lestat\audit_data`

---

## 3. Workload A: Graph BFS (Pokec)
### Dataset Scale
- **Vertices**: 1,632,803
- **Edges**: 30,769,268 (SNAP Pokec)
- **Integrity**: Verified 100% against SNAP source after cleaning header metadata during ingestion.

### Performance (PostgreSQL B-Tree Baseline)
| Operation | Latency (Avg) | Neighbors Found |
| :--- | :--- | :--- |
| Single-Step Expand | **0.6ms** | 14.2 (avg) |
| Index Strategy | `src` (B-Tree) | Successful |

---

## 4. Workload B: Spatial PIP (US States)
### Dataset Scale
- **Source**: US Census TIGER 2023 (State Boundaries)
- **Geometry**: 56 MultiPolygons (SRID 4269)
- **Ingestion**: Automated via `shp2pgsql` + `psql` piping.

### Performance (PostGIS GIST Baseline)
| Operation | Latency (Avg) | Success Rate |
| :--- | :--- | :--- |
| Random Point PIP | **1.9ms** | 100% |
| Index Strategy | `geom` (GIST) | Successful |

---

## 5. Critical Failures (The "Dev AI" Fix List)

### [CRITICAL] Binary Pathing Failure
> [!CAUTION]
> **Missing `librtdl_embree.dll`**
> The release snapshot `rtdl_win_snapshot.tar.gz` and the installation scripts verified on host do **not** result in a functional Embree backend. The `rtdsl` Python library fails with `AttributeError: function 'rtdl_embree_run_fixed_radius_neighbors' not found` or `ModuleNotFoundError`.

### [MAJOR] API Version Mismatch
- The `rtdsl/__init__.py` present in the Windows snapshot is significantly outdated compared to the `v0_4_main_publish` codebase.
- Specifically, `rt.csr_graph` is missing from the constructor export, which breaks the Goal 410/426 tutorials.

### [MINOR] Driver Logic SRID Mismatch
- Automated PostGIS benchmarks require explicit `ST_SetSRID` on `ST_MakeLine` to match the TIGER SRID 4269; otherwise, the engine throws internal mixed-SRID errors.

---

## 6. Audit Conclusion
**Status: REJECT**

The RTDL v0.6 line is technically coherent in its SQL/Reference paths, but is **non-functional on Windows** for its primary value proposition: Embree-accelerated raytracing kernels.

**Requested Actions for Dev AI**:
1.  Verify the Windows build pipeline for `librtdl_embree.dll`.
2.  Ensure that the `.tar.gz` release snapshot includes the `build/` directory with compiled binaries for the target architecture (x64).
3.  Synchronize the `rtdsl` Python package across distribution channels.

---
*Verified and Signed by Antigravity (Advanced Agentic Coding Line)*
