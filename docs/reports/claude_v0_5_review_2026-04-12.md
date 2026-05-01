# v0.5 Code Review and Test Report

Date: 2026-04-12
Working directory: `/Users/rl2025/claude-work/rtdl_review_2026-04-12`
Base commit (last reviewed): `2d51d38 Fix accelerated fixed-radius boundary parity`
Tip commit (this review): `917bcdc Add RTNN bounded dataset manifests for v0.5`
New commits reviewed: 34

---

## Summary

The new work spans two independent areas:

| Area | Commits | What changed |
|------|---------|--------------|
| **v0.5 compute surface** | 10 commits | 3D point type, `bounded_knn_rows` predicate and oracle path |
| **RTNN research scaffolding** | 10 commits | Dataset registry, baseline registry, reproduction matrix, manifest writer, cuNSearch skeleton |
| **v0.4 release closure** | 14 commits | README rewrite, tutorial audit, doc cleanup, version bump |

**Verdict: v0.5 compute surface is correct. One pre-existing test failure requires a one-line fix. Research scaffolding is well-structured with no runnable logic yet.**

---

## New Source Files

### Compute surface additions

| File | What it adds |
|------|--------------|
| `src/rtdsl/types.py` | `Point3DLayout`, `Points3D` geometry type |
| `src/rtdsl/reference.py` | `Point3D` dataclass, `bounded_knn_rows_cpu()`, `_point_distance_sq()` helper |
| `src/rtdsl/api.py` | `bounded_knn_rows(radius, k_max)` predicate factory |
| `src/rtdsl/runtime.py` | `bounded_knn_rows` dispatch, `_coerce_point` 3D path, `Point3D` oracle rejection |
| `src/rtdsl/oracle_runtime.py` | `_run_bounded_knn_rows_oracle()` |
| `src/rtdsl/lowering.py` | `_lower_bounded_knn_rows()` execution plan |
| `src/native/oracle/rtdl_oracle_abi.h` | `rtdl_oracle_run_bounded_knn_rows` declaration |
| `src/native/oracle/rtdl_oracle_api.cpp` | `rtdl_oracle_run_bounded_knn_rows` C implementation |
| `src/rtdsl/embree_runtime.py` | `Point3D` rejection with clear message |
| `src/rtdsl/optix_runtime.py` | `Point3D` rejection with clear message |
| `src/rtdsl/vulkan_runtime.py` | `Point3D` rejection with clear message |

### Research scaffolding additions (all new files)

| File | What it adds |
|------|--------------|
| `src/rtdsl/rtnn_reproduction.py` | `RtnnDatasetFamily`, `RtnnExperimentTarget`, `RtnnLocalProfile` — RTNN paper dataset registry |
| `src/rtdsl/rtnn_baselines.py` | `RtnnBaselineLibrary`, `RtnnBaselineDecision` — comparison library registry |
| `src/rtdsl/rtnn_matrix.py` | `RtnnMatrixEntry`, `rtnn_reproduction_matrix()` — cross-product matrix builder |
| `src/rtdsl/rtnn_manifests.py` | `RtnnBoundedDatasetManifest`, `write_rtnn_bounded_dataset_manifest()` — manifest writer |
| `src/rtdsl/rtnn_cunsearch.py` | `CuNSearchAdapterConfig`, `CuNSearchInvocationPlan`, adapter skeleton |

---

## Review: Compute Surface (`bounded_knn_rows` + 3D Points)

### `Point3D` type

**Correct.** `Point3DLayout` has fields `(x, y, z, id)` — same field order as `Point2DLayout` with `z` inserted. `Points3D` correctly specifies `required_fields=("x", "y", "z", "id")`. The `Point3D` frozen dataclass is clean.

### `_point_distance_sq` helper

**Correct.** Uses `getattr(left, "z", 0.0)` for the z component, which means 2D Points silently get z=0.0. This correctly allows mixed 2D/3D calls but is a silent coercion — not a problem for the current internal use, but callers should not rely on it for mixed inputs.

### `bounded_knn_rows` API factory

**Correct.** Validates `radius >= 0` and `k_max > 0`. Stores options as `{"radius": float, "k_max": int}`. Predicate name is `"bounded_knn_rows"` — distinct from `"fixed_radius_neighbors"` and `"knn_rows"`.

### `bounded_knn_rows_cpu` reference implementation

**Correct.** The algorithm is: radius filter → sort by (distance, neighbor_id) → assign 1-based `neighbor_rank` → truncate to `k_max` → sort output by `query_id`. This matches the contract spec in `docs/goal_262_v0_5_bounded_radius_knn_contract_design.md`.

**Note:** Output rows are sorted by `query_id` only at the end (`rows.sort(key=lambda row: row["query_id"])`). Within each query group, the secondary sort by distance is correct because the per-query `candidates.sort` runs before the final join. This is consistent with `fixed_radius_neighbors_cpu`.

### Oracle path (`rtdl_oracle_run_bounded_knn_rows`)

**Correct.** The C implementation reproduces the same algorithm: radius filter, sort by (distance, neighbor_id) with epsilon tolerance, k_max truncation, 1-based rank assignment. Neighbor rank is assigned after sort. ABI struct `RtdlKnnNeighborRow {query_id, neighbor_id, distance, neighbor_rank}` is 4+4+8+4 = 20 bytes — consistent with `_run_bounded_knn_rows_oracle` in Python which reads all four fields.

**Note:** The oracle works only on 2D points (uses `_RtdlPoint` with x/y). A `Point3D` input to `run_cpu` is caught early in `_validate_oracle_supported_inputs` with a clear message.

### Backend rejection messages

**Correct.** All three accelerated backends (Embree, OptiX, Vulkan) raise `ValueError` with an explicit "not native-online yet" message when given `Point3D` inputs. This is the honest boundary — the 3D surface exists only at the reference level.

### `lowering.py`

**Correct.** `_lower_bounded_knn_rows` produces `workload_kind="bounded_knn_rows"` and `predicate="bounded_knn_rows"` in the execution plan. The lowering requires `geometry.name == "points"` for both build and probe — it will raise for non-point inputs.

---

## Review: RTNN Research Scaffolding

### `rtnn_reproduction.py`

Three dataset families: `kitti_velodyne_point_sets`, `stanford_3d_scan_point_sets`, `nbody_or_millennium_snapshots` — all 3D, all `current_status="source-identified"`. Five experiment targets covering three artifacts (`dataset_packaging`, `paper_matrix`, `comparison_matrix`). Three local profiles (one per family, all `<=10 minutes`).

Filter functions work correctly: `artifact=`, `reproduction_tier=`, `handle=` filters all use tuple comprehension.

**No runnable logic — all data is metadata.**

### `rtnn_baselines.py`

Six baseline libraries: cuNSearch, FRNN, PCLOctree, FastRNN, SciPy cKDTree, PostGIS. Five baseline decisions. `rtnn_baseline_libraries()` and `rtnn_baseline_decisions()` support `handle=`/`current_status=` and `library_handle=`/`verdict=` filters.

**Correct. No runnable logic.**

### `rtnn_matrix.py`

`rtnn_reproduction_matrix()` cross-joins experiment targets × baseline libraries, filtered by workload shape compatibility and artifact type. Non-paper baselines (PostGIS, SciPy) are excluded from `dataset_packaging` and `paper_matrix` artifacts. `_matrix_status_for` correctly assigns status by reproduction tier.

**Correct. All filtering logic verified by tests.**

### `rtnn_manifests.py`

`write_rtnn_bounded_dataset_manifest()` writes a JSON file with three sections: `dataset` (from `rtnn_dataset_families`), `bounded_manifest` (from `rtnn_bounded_dataset_manifests`), `local_profile` (from `rtnn_local_profiles` via the manifest's `bounded_profile_id`). The `ValueError` path for unknown handles is clean.

**Correct. Roundtrip write-and-read verified.**

### `rtnn_cunsearch.py`

Adapter skeleton only. `resolve_cunsearch_binary` checks filesystem existence — no execution. `plan_cunsearch_fixed_radius_neighbors` raises `RuntimeError` when binary is not configured. `write_cunsearch_fixed_radius_request` writes a `json_request_v1` format request file (also raises when binary not configured).

**Correct as a skeleton. No execution path exists yet.**

---

## Pre-Existing Failure

| Test | File | Status | Root cause |
|------|------|--------|------------|
| `test_live_front_surface_docs_use_new_public_video_url` | `tests/goal187_v0_3_audit_test.py:24` | FAIL (pre-existing) | Checks for Shorts URL `youtube.com/shorts/VnzVWAPln3k` which was replaced by 4K URL `youtu.be/d3yJB7AmCLM` in commit `d2d036b` |

**Fix required:** Update `SHORTS_URL` constant in `goal187_v0_3_audit_test.py` to `"https://youtu.be/d3yJB7AmCLM"` and update the assertion to check all three docs use the 4K URL.

---

## Findings

**F-1 (low): `_point_distance_sq` silent 2D/3D coercion**
`getattr(left, "z", 0.0)` silently treats 2D points as z=0.0 when mixed with 3D. Not a bug for current use (the only callers are the `_cpu` functions which handle homogeneous inputs), but the behavior is implicit. A comment in the function noting this convention would help future readers.

**F-2 (low): `rtnn_local_profiles` artifact filter**
`rtnn_local_profiles(artifact=...)` checks `artifact in profile.artifact.split("|")` but the current profile records have `artifact="dataset_packaging"` (singular). Splitting on `|` still works correctly, but is defensive code for a separator that doesn't appear in the data yet. No correctness issue.

**F-3 (low): stale test (goal187)**
`tests/goal187_v0_3_audit_test.py:24` checks for the old YouTube Shorts URL after the README was upgraded to the 4K link. One-line fix: update `SHORTS_URL` to the 4K URL.

**F-4 (info): cuNSearch binary path resolves symlinks**
`resolve_cunsearch_binary` calls `resolved.resolve()` which expands symlinks. `config.binary_path` will differ from `sys.executable` if `sys.executable` is a symlink (as on Homebrew Python). This is correct behavior but worth knowing when writing adapter tests.

---

## Test Results

### Pre-existing tests
| Suite | Tests | Pass | Fail | Skip |
|-------|-------|------|------|------|
| All `tests/*_test.py` (before new tests) | 570 | 511 | 1 (F-3 above) | 58 |

### New tests (this review)
| File | Tests | Pass | Fail |
|------|-------|------|------|
| `tests/claude_v0_5_full_review_test.py` | 111 | 111 | 0 |

### Combined suite
| Total | Pass | Fail | Skip |
|-------|------|------|------|
| 681 | 622 | 1 (pre-existing F-3) | 58 |

---

## New Test File

**`tests/claude_v0_5_full_review_test.py`** — 111 tests across 15 test classes:

| Class | Tests | What it covers |
|-------|-------|---------------|
| `Point3DTypeTest` | 7 | Layout fields, required fields, frozen dataclass, equality, export identity |
| `PointDistanceSqTest` | 7 | Zero distance, unit vectors, Pythagorean triple, 3D diagonal, 2D/3D mixed, symmetry |
| `BoundedKnnRowsApiTest` | 8 | Validation (negative radius, zero k_max), options storage, type coercions, export |
| `BoundedKnnRowsCpuTest` | 12 | Radius filter, k_max truncation, rank ordering, tie-breaking, query_id sort, edge cases |
| `BoundedKnnRunCpuPythonReferenceTest` | 4 | 2D and 3D kernel paths, `neighbor_rank` emission, return type |
| `BoundedKnnVsFrnShapeTest` | 3 | `neighbor_rank` presence distinction, radius filter parity, predicate name distinction |
| `BoundedKnnOracleTest` | 2 | `run_cpu` matches reference, `Point3D` rejection message |
| `RtnnReproductionTest` | 12 | Family count/uniqueness, 3D requirement, filters, `bounded_knn_rows` in targets |
| `RtnnBaselinesTest` | 8 | Library count, cuNSearch priority, online baselines, PCL deferral, filters |
| `RtnnReproductionMatrixTest` | 8 | Non-empty, field presence, non-paper exclusion, comparison inclusion, blocked status, workload matching |
| `RtnnManifestsTest` | 8 | Count, handle/family alignment, 10-min budget, filter, unknown handle error, JSON roundtrip, parent-dir creation |
| `RtnnCuNSearchAdapterTest` | 9 | Binary resolution, config status, plan/write raises when unconfigured, JSON request shape |
| `StaleGoal187Test` | 2 | Documents the stale test and the corrected URL |
| `NewPublicExportsTest` | 17 | All new public symbols present in `rtdsl.__init__` |
| `Point3DOracleRejectionTest` | 2 | `run_cpu` raises "2D" for `fixed_radius_neighbors` and `knn_rows` with 3D points |

---

## Recommendations

1. **Fix F-3 now**: update `goal187_v0_3_audit_test.py` line 12 (`SHORTS_URL`) to the 4K URL to restore a clean test suite.
2. **Add a comment to `_point_distance_sq`** (F-1): one line noting the `getattr` fallback convention.
3. **The v0.5 compute surface is ready for the next acceleration step**: `cpu_python_reference` + `run_cpu` (oracle) both work for `bounded_knn_rows`. The next natural goal would be Embree/OptiX/Vulkan support for 3D points.
4. **RTNN scaffolding is well-structured**: all registries are pure data with correct filtering. The first concrete next step is the cuNSearch build guide, then the request-execution path in `rtnn_cunsearch.py`.
