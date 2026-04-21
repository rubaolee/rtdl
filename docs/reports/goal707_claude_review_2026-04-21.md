# Goal 707: Claude Review — RT-Core Red Line And DB/Graph/Spatial Audit

Date: 2026-04-21
Reviewer: Claude Sonnet 4.6 (claude-sonnet-4-6) — independent re-review
Verdict: **BLOCK**

---

## Scope

Review of:

- `docs/reports/goal707_app_rt_core_redline_and_db_graph_spatial_audit_2026-04-21.md` (the audit report)
- `docs/app_engine_support_matrix.md` + `src/rtdsl/app_support_matrix.py` (the evidence)
- `docs/application_catalog.md` (the public catalog)
- `tests/goal707_app_rt_core_redline_audit_test.py` (the test suite)

---

## Verdict: BLOCK

The audit report's red line is technically correct and its DB/graph/spatial status assessments are honest. However, a concrete label inconsistency in the engine support matrix — both the Markdown doc and its Python source — must be fixed before these documents can serve as authoritative public evidence. The inconsistency creates a directly contradictory statement that any reader cross-referencing the two tables will notice.

---

## Finding 1 (BLOCK): `direct_cli_native` and `host_indexed_fallback` are mutually contradictory labels

**Severity: must fix before accept**

The status legend in `app_engine_support_matrix.md` defines `direct_cli_native` as:

> "the app CLI exposes this engine and **the app uses native backend support for its RTDL core**"

The OptiX performance class `host_indexed_fallback` is defined as:

> "OptiX-facing app path currently dispatches to host-indexed CPU-side logic"

Dispatching to host-indexed CPU-side logic is not native backend support. The two definitions are mutually exclusive. Yet four apps carry both labels simultaneously:

| App | Engine-matrix OptiX label | OptiX performance class |
| --- | --- | --- |
| `graph_analytics` | `direct_cli_native` | `host_indexed_fallback` |
| `road_hazard_screening` | `direct_cli_native` | `host_indexed_fallback` |
| `segment_polygon_hitcount` | `direct_cli_native` | `host_indexed_fallback` |
| `segment_polygon_anyhit_rows` | `direct_cli_native` | `host_indexed_fallback` |

The inconsistency is present in both `docs/app_engine_support_matrix.md` (the Markdown table) and `src/rtdsl/app_support_matrix.py` (the Python source at lines 131–135, 181–185, 192–196, 201–205).

The correct label for these four apps is `direct_cli_compatibility_fallback`, which is defined as "the app exposes this engine but the path is a documented compatibility path, not an acceleration claim." That is exactly what `host_indexed_fallback` means in the performance table.

**Required fix:**

In `src/rtdsl/app_support_matrix.py` change `optix=_NATIVE` to `optix=_COMPAT` for:

- `graph_analytics` (line ~134)
- `road_hazard_screening` (line ~184)
- `segment_polygon_hitcount` (line ~195)
- `segment_polygon_anyhit_rows` (line ~205)

Then update the four corresponding rows in `docs/app_engine_support_matrix.md` from `direct_cli_native` to `direct_cli_compatibility_fallback`.

**Note on DB app (`database_analytics`):** The DB app has `direct_cli_native` for OptiX and `python_interface_dominated` as its performance class. This is NOT a contradiction. The audit report correctly explains that real native OptiX BVH candidate discovery work exists; it is the Python packing, copy-back, and materialization overhead that dominates the app-level timing, not the absence of native work. The `direct_cli_native` label is defensible there.

---

## Finding 2 (PASS): Red line is technically correct

The five definitional statements in the red line are individually correct and mutually consistent:

1. **RTDL acceleration claim requires routing through an RTDL backend traversal, BVH, point query, ray query, or native spatial-query primitive.** Correct. This is the right minimum bar.

2. **NVIDIA RT-core claim requires that the measured OptiX path uses OptiX traversal (e.g., `optixTrace`) over an OptiX acceleration structure on RTX-class hardware.** Correct. This correctly excludes: (a) host-indexed paths that happen to be compiled against the OptiX library, (b) CUDA kernels launched through the OptiX backend library, and (c) Embree paths.

3. **CUDA kernels inside the OptiX backend library are GPU compute, not RT-core traversal.** Correct and important. The `cuda_through_optix` performance class in the matrix is consistent with this.

4. **Embree BVH and point-query execution is real RT-style CPU traversal, not GPU RT-core execution.** Correct. The distinction between Embree CPU BVH work and NVIDIA GPU RT-core work is real and the audit draws it cleanly.

5. **Python post-processing must not be described as native backend acceleration.** Correct.

The red line is clear enough for public docs as written. No changes needed here.

---

## Finding 3 (PASS): DB, graph, and spatial status assessments are honest

**DB:** The audit correctly identifies the DB app as a valid RTDL app with real OptiX BVH candidate discovery, and correctly holds back any RTX app-performance flagship claim due to Python/interface domination. The `python_interface_dominated` classification and `needs_interface_tuning` readiness status are internally consistent and honestly reflect the documented limitation.

**Graph:** The audit correctly states that the graph app's OptiX and Vulkan paths are host-indexed correctness paths and makes no GPU RT-core traversal claim. The `host_indexed_fallback` performance class and `needs_native_kernel_tuning` readiness status are consistent. The statement "Graph is not yet a valid OptiX RT-core performance app today" is accurate.

**Spatial — Embree-only apps (service coverage, event hotspot, facility KNN):** These are correctly described as Embree CPU spatial-query apps with no RT-core claim. The `not_optix_exposed` performance class and `exclude_from_rtx_app_benchmark` readiness status are consistent.

**Spatial — OptiX-exposed segment/polygon apps (road hazard, segment/polygon hitcount, anyhit rows):** The audit correctly identifies these as `host_indexed_fallback` paths and makes no RTX speedup claim. The readiness status `needs_native_kernel_tuning` is consistent. (These are the same four apps covered by Finding 1; the audit's verbal description is honest even though the engine-matrix label is wrong.)

**Spatial — CPU-reference only (polygon-pair overlap, polygon-set Jaccard):** Correctly classified as `exclude_from_rtx_app_benchmark`. No issues.

**Paper-derived apps:**

- Robot collision: Correctly identified as the cleanest OptiX traversal candidate. The `optix_traversal` performance class and `needs_phase_contract` readiness status (pending a clean phase-split RTX rerun) are honest.
- Outlier detection and DBSCAN: The optional summary modes that use real OptiX traversal are accurately described as bounded prototypes distinct from the default `cuda_through_optix` row paths. The `needs_phase_contract` and `needs_postprocess_split` readiness statuses are appropriate.
- Hausdorff, ANN, Barnes-Hut: Correctly classified as `cuda_through_optix` or app/Python-dominated. No RT-core claims are made.

---

## Finding 4 (PASS): Test suite is correct and sufficient for its scope

All three test methods in `tests/goal707_app_rt_core_redline_audit_test.py` check phrases that are present verbatim in the documents. The tests would pass today. The test scope is appropriate for a consensus-gate check: it verifies that the key definitional statements and status summaries are present in the public docs, and that the honesty-boundary language appears in both the engine matrix and the catalog. No test changes are needed.

---

## Finding 5 (PASS): Application catalog honesty boundary is correct

`docs/application_catalog.md` correctly states:

- RTDL owns the accelerated core only when the app routes through an RTDL backend traversal, BVH, point-query, ray-query, or native spatial-query primitive.
- `--backend optix` is not by itself an NVIDIA RT-core claim.
- Python orchestration is expected; Python-only post-processing must not be described as backend acceleration.
- The optional OptiX summary modes in outlier and DBSCAN apps are bounded fixed-radius prototypes.

No changes needed in the catalog.

---

## Required Fixes Before Accept

1. In `src/rtdsl/app_support_matrix.py`: change `optix=_NATIVE` to `optix=_COMPAT` for `graph_analytics`, `road_hazard_screening`, `segment_polygon_hitcount`, and `segment_polygon_anyhit_rows`.

2. In `docs/app_engine_support_matrix.md`: update the corresponding four rows in the Matrix table from `direct_cli_native` to `direct_cli_compatibility_fallback` for the OptiX column.

No changes are needed to the audit report, the application catalog, or the test suite.

---

## Summary

The red line is technically sound. The DB/graph/spatial status audit is honest. The only concrete error is a label mismatch: four apps are marked `direct_cli_native` (which claims native backend support) for OptiX while their measured paths are `host_indexed_fallback` (CPU-side host-indexed logic). Fix those four labels and the document set is ready to accept.
