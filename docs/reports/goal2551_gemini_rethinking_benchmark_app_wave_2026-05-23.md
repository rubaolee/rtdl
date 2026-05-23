# RTDL Technical Review: Benchmark-App Wave (2026-05-23)

Based on the review of `docs/reports/goal2551_codex_rethinking_benchmark_app_wave_2026-05-23.md` and inspection of the `src/` tree, here is the architectural assessment and prioritized next-work list.

---

### 1. Engine/Runtime Boundary Leakage
The native engine and core RTDSL layers currently suffer from significant app-specific and benchmark-specific "vocabulary leakage." While the benchmark wave successfully exposed pressure points, it left behind naming and structural debt that compromises engine purity.

*   **Native OptiX Leakage:** `src/native/optix/rtdl_optix_workloads.cpp` is the primary offender. It contains `DbScanLaunchParams`, `OptixDbDatasetImpl`, and thread-local timers like `g_optix_last_db_traversal_s`. The report confirms the existence of `db_scan_kernel.cu` and `DbScanPipeline`. These are app-specific implementations of what should be a generic **Columnar Predicate Scan**.
*   **RTDSL Adapter Leakage:** `src/rtdsl/partner_adapters.py` has been polluted with `robot_collision_pose_flags_optix_prepared_partner_device_columns`. This logic belongs in `examples/v2_0/research_benchmarks/robot_collision` or a dedicated `rtdsl.app_adapters` namespace.
*   **Wording Debt:** `src/rtdsl/columnar_partner.py` explicitly uses the term `"numeric RayDB-style columns only"` (L97) in its execution requirements. This ties the core columnar contract to a specific research benchmark (RayDB) rather than a generic primitive.
*   **Math Leakage:** `src/rtdsl/aggregate_tree_reference.py` contains hard-coded `sum_weighted_inverse_square_contributions_2d`. While Goal2549 correctly kept this out of native OptiX, its presence in the core reference module as a top-level function suggests the aggregate-frontier primitive is currently over-specialized for Barnes-Hut.

### 2. Feature Duplication and Fragmentation
Common patterns have emerged across RT-DBSCAN, Robot Collision, RayDB, and Barnes-Hut, but they have been implemented through independent, partially duplicated paths.

*   **Grouped Reductions:** There is a "Grouped Reduction" proliferation. `GROUP_COUNT` and `GROUP_SUM` appear in different guises across `optix_runtime.py`, `embree_runtime.py`, and `partner_adapters.py` (using Torch/CuPy). There is no unified `GroupedReduction` primitive that can target different backends.
*   **Device Column Descriptors:** `PartnerResidentColumnarRecordSet` in `src/rtdsl/columnar_partner.py` and various `dict[str, object]` patterns in adapters show that the project lacks a single, reusable **Unified Columnar Device ABI**. Every app is reinventing its handoff metadata.
*   **Prepared-State Lifecycle:** Each benchmark manages its own "prepared" objects (scenes, datasets, aggregate trees) with inconsistent lifetime management and metadata contracts.

### 3. Architectural Verdict
**Verdict: SUCCESSFUL PROTOTYPE; UNSTABLE ENGINE.**
The benchmark wave successfully validated the RTDL primitives (Hit-stream, Grouped Continuation, Columnar) for complex workloads. However, the current implementation is "benchmark-informed" rather than "engine-generic." It is suitable for an internal review of the research results, but **architecturally unfit for a public release** in its current state.

### 4. Git Snapshot Appropriateness
The label `internal-benchmark-apps-2026-05-23` is **HIGHLY APPROPRIATE**.
*   **Why Internal:** It preserves the exact state of the Goal2400-Goal2550 benchmark wave, including the Barnes-Hut Goal2549 rejection and Goal2550 closeout.
*   **Why NOT Public:** The "RayDB," "DBSCAN," and "Robot" vocabulary inside `librtdl_optix` would be seen as a sign of an immature, non-extensible engine. Public release wording must wait until the "Engine-Purity Gate" is passed.

---

### Prioritized Next-Work List

#### [HIGH PRIORITY] Goal A: Native Engine Purity Pass
*   **Action:** Rename `DbScan*` and `db_scan*` in `src/native/optix` to `ColumnarPredicateScan` and `columnar_scan`.
*   **Evidence Requirement:** Implement a `scripts/engine_purity_gate.py` that fails the build if `dbscan`, `raydb`, `robot`, or `barnes` appear in `src/native/`.

#### [HIGH PRIORITY] Goal B: Unified Columnar Device ABI
*   **Action:** Consolidate `PartnerResidentColumnarRecordSet` into a stable internal ABI.
*   **Implementation:** One C++ struct for intake, one Python validation layer, and a consistent descriptor for dtype/pointer/shape/ownership.

#### [MEDIUM PRIORITY] Goal C: Shared Grouped-Reduction Substrate
*   **Action:** Create a generic `GroupedReduction` primitive in RTDSL.
*   **Impact:** Lower RT-DBSCAN, RayDB-style aggregates, and robot pose-flags onto this single substrate. This allows a single performance optimization pass to benefit all three benchmark apps.

#### [MEDIUM PRIORITY] Goal D: Aggregate-Frontier Primitive (Math-Agnostic)
*   **Action:** Refactor `src/rtdsl/aggregate_tree_reference.py` to separate **Frontier Traversal** (geometric) from **Inverse-Square Reduction** (app math).
*   **Constraint:** Native OptiX must only produce the frontier or traversal diagnostics; app math remains in Python/Partner layers until a generic operator plug-in is designed.

#### [LOW PRIORITY] Goal E: App-Adapter Namespace
*   **Action:** Move benchmark-specific convenience wrappers from `src/rtdsl/partner_adapters.py` into a new `src/rtdsl/app_adapters/` directory or directly into the `examples/` modules.
