I have sufficient evidence. Let me now compile the full independent review.

---

# RTDL Benchmark-App Wave: Independent Architecture Review
**Scope:** RT-DBSCAN · Robot Collision · RayDB-style Columnar · Barnes-Hut — through Goal2550
**Reviewer basis:** direct source inspection of native C++, Python runtime, adapter layer, benchmark apps, and tests

---

## 1. App-Specific / Benchmark-Specific Concepts at the Engine Boundary

### Verdict: Partial — `Db` vocabulary is genuinely leaking into the native engine

The codex correctly identifies the problem but understates its depth.

#### 1a. `DbScanPipeline` / `g_dbscan` / `kDbScanKernelSrc` — Confirmed in two files

`rtdl_optix_core.cpp:5394` defines `kDbScanKernelSrc`, `5749` defines `DbScanPipeline`, and `5805` declares `static DbScanPipeline g_dbscan`.
`rtdl_optix_workloads.cpp:32` defines `struct DbScanLaunchParams`. Kernel entry points are `__raygen__db_scan_probe`, `__miss__db_scan_miss`, `__intersection__db_scan_isect`, `__anyhit__db_scan_anyhit` (lines 1714–1719).

This is **not cosmetic**. `DbScanPipeline` is a named singleton that owns the JIT-compiled OptiX pipeline. Its name is load-bearing in error messages and in the singleton init guard at `rtdl_optix_workloads.cpp:1712`.

#### 1b. `RtdlDb*` type family — Pervasive across the public ABI header

`rtdl_optix_prelude.h` (the public C ABI) contains:

| Symbol | Line(s) | Problem |
|---|---|---|
| `RtdlDbField` | 279 | "Db" in public stable struct name |
| `RtdlDbScalar` | 284 | Same |
| `RtdlDbClause` | 320 | "Clause" is DBMS vocabulary |
| `RtdlDbGroupedCountRow` | 331 | "Db" in grouped primitive result type |
| `RtdlDbGroupedSumRow` | 336 | Same |
| `RtdlDbGroupedSumCountRow` | 341 | Same |
| `RtdlDbGroupedStatsRow` | 347 | Same |
| `RtdlDbCompactSummaryRequest` | 359 | "CompactSummary" is query-optimizer vocabulary |
| `kRtdlDbKindInt64` etc. | 291–294 | "Db" in dtype constants |
| `kRtdlDbCompactSummary*` | 355–357 | Same |

`rtdl_optix_workloads.cpp` has 40+ internal functions named `db_scalar_*`, `db_clause_*`, `db_encode_*`, `db_compare_*`. All of these are implementing what is functionally a *columnar predicate evaluation* pass, not a database. The naming misleads: this is a scan/filter/aggregate primitive over a flat record batch, not a query engine.

#### 1c. `robot_collision_pose_flags_optix_prepared_partner_device_columns` — In `partner_adapters.py:5702`

This is not native engine leakage, but it is in the central shared adapter module. The function name encodes three app-specific terms: the benchmark name, the output concept (pose flags), and a specific execution path. This should live in the robot collision benchmark app or under an `rtdsl.app_adapters` namespace.

#### 1d. `"numeric RayDB-style columns only"` — `columnar_partner.py:97`

Confirmed at line 97. This is inside the documented blockers for a **non-experimental, shipped-in-HEAD module**. The comment anchors the scope of an API to a benchmark-app name instead of to a capability contract.

#### 1e. `WEIGHTED_INVERSE_SQUARE_CONTRIBUTION_ROWS_2D_CONTRACT` — `aggregate_tree_reference.py:11–22`

This is in a reference module, not the native engine. The codex flags it correctly as a force-law shape that should not become the only reduction model, but its placement is defensible as a reference contract name. It does not leak into C++ code or the runtime dispatch path.

---

## 2. Common Features Independently / Partially Duplicated

### Verdict: Three concrete duplication sites found; one missed by the codex

#### 2a. `_with_capacity` grouped reduction functions missing `overflowed_out` — **Structural ABI inconsistency**

Every bounded primitive in the prelude that involves ray output carries `uint32_t* overflowed_out`:
- `rtdl_optix_collect_k_bounded_i64` at line 715
- `rtdl_optix_run_segment_shape_anyhit_rows_native_bounded` at line 710
- `rtdl_optix_write_prepared_ray_anyhit_2d_device_all_witnesses` at line 637

But all six `_with_capacity` grouped reduction variants — lines 1132–1192 — omit `overflowed_out`. They accept `size_t group_capacity` and return `size_t* row_count_out` but provide no way for the caller to distinguish "capacity was sufficient" from "capacity was hit and groups were silently dropped." The codex does not call this out explicitly; it belongs in the capacity/overflow contract section as a concrete defect.

#### 2b. RT-DBSCAN union-find logic duplicated within the benchmark app itself

`examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py` has two nearly identical union-find builders:

- `_component_rows_from_pairs_and_flags()` (lines 298–362): takes predicate flags, runs union-find, assigns roots
- `_component_rows_from_parent_and_flags()` (lines 380–430): takes pre-computed parent array, runs union-find, assigns roots

Lines 309–341 and 390–408 are ~85% identical. The distinction is only the parent-array input source. This is the highest-risk intra-app duplication and will become a maintenance burden as component-row logic evolves.

#### 2c. Hausdorff distance has three near-identical partner conversion wrappers

`examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py`:
- `_run_partner_exact_directed()` lines 277–300
- `_run_partner_numpy_exact_directed()` lines 303–324
- `_run_partner_cupy_witness_exact_directed()` lines 327–348

Each follows the same pattern: `point_rows_to_partner_columns → run directed query → extract directed result`. ~85% of the body is identical across all three. Parameterizing the partner specialization would halve the code.

#### 2d. Device column allocation duplicated within RT-DBSCAN itself

`rtdl_rt_dbscan_benchmark_app.py` lines 1076–1078 and 1295–1298 contain identical calls to `allocate_fixed_radius_count_threshold_3d_partner_device_output_columns()` with no factoring. When the column layout changes, both sites will diverge.

#### 2e. Grouped reduction forms: six parallel paths, no shared substrate

The codex correctly identifies this. Across the four benchmarks, grouped reductions appear in at least five different code patterns:

| Location | Operation | Form |
|---|---|---|
| `rtdl_optix_workloads.cpp` | `RtdlDbGrouped*` | Host-side columnar predicate + OptiX accumulation |
| `rtdl_rt_dbscan_benchmark_app.py` | grouped union / component | CuPy + union-find |
| `rtdl_robot_collision_benchmark_app.py` | group-any flag | OptiX any-hit |
| `rtdl_barnes_hut_benchmark_app.py` | weighted vector-sum | partner columns + tree |
| `optix_runtime.py:145–160` | count/sum/min/max/sum_count/stats | FFI dispatch table |

There is no shared Python `GroupedReduction` primitive. Each benchmark rolls its own group-key logic, group-output compaction, and result extraction.

---

## 3. Better Architecture / Primitives for Next Work

### 3a. Rename the `Db` ABI before it is used externally

The `RtdlDb*` struct family is in the *public C header* (`rtdl_optix_prelude.h`) that any external partner binding would consume. If these names ship as-is, a future rename is a breaking ABI change. The rename cost is low now and high later.

Concrete rename map:

| Current | Proposed |
|---|---|
| `RtdlDbField` | `RtdlPayloadField` |
| `RtdlDbScalar` | `RtdlPayloadScalar` |
| `RtdlDbClause` | `RtdlPredicateClause` |
| `RtdlDbGroupedCountRow` | `RtdlGroupedCountRow` |
| `RtdlDbGroupedSumRow` | `RtdlGroupedSumRow` |
| `RtdlDbCompactSummaryRequest` | `RtdlPredicateSummaryRequest` |
| `DbScanPipeline` | `ColumnarScanPipeline` (internal, not public) |

### 3b. Add `overflowed_out` to all six `_with_capacity` grouped reduction variants

This is a safety defect, not a naming defect. Without it, the caller cannot safely implement retry/chunking for large group sets. The fix is mechanical: add `uint32_t* overflowed_out` as the penultimate parameter to each of the six functions at lines 1132–1192, matching the contract of every other bounded primitive.

### 3c. Introduce a unified `DeviceColumnDescriptor` Python class

Column descriptor logic is currently split across:
- `columnar_partner.py:170–239` (validation, dtype mapping, device check)
- `partner_adapters.py:5702` (app-specific allocation wrapper)
- `optix_runtime.py:145–160` (FFI symbol dispatch)

A single `DeviceColumnDescriptor` dataclass with: `dtype_token`, `device_ptr`, `element_count`, `stride_bytes`, `device_id`, `ownership` — validated once at construction — would replace three separate validation paths and give the device-column ABI a clear Python-side contract.

### 3d. Extract a `UnionFindBuilder` from RT-DBSCAN

The union-find logic in `_component_rows_from_pairs_and_flags` / `_component_rows_from_parent_and_flags` (lines 298–430) is the core component-labeling algorithm. It should be a standalone function with a clear signature: `union_find_from_proposals(pairs, flags, pre_parent=None) → parent_array`. The two callers become one-liners.

### 3e. Introduce a `PartnerDirectedQuery` factory for Hausdorff-style benchmarks

The three `_run_partner_*_directed()` functions in the Hausdorff app should be replaced by a template that accepts a `partner_mode` enum (`exact_generic`, `numpy_exact`, `cupy_witness`). The 85% common body runs once; only the column conversion and result extraction steps vary.

### 3f. The `grouped_union_query_block_size` knob is RT-DBSCAN-specific and undocumented at the engine level

This parameter appears only in the RT-DBSCAN benchmark app (lines 860–862, 1208–1272) and is not exposed in other grouped-reduction apps (RayDB, Barnes-Hut). If this is an engine primitive (block size for the grouped stream kernel), it should appear in the native API with documentation. If it is an RT-DBSCAN policy choice, the benchmark should document why other apps do not need it. Currently neither is done.

---

## 4. Internal Git Snapshot: `internal-benchmark-apps-2026-05-23`

### Verdict: Appropriate for internal use; phrasing is correct; not ready for public release

The codex language is well-calibrated. The snapshot label conveys:
- "internal" — not a public release
- "benchmark-apps" — scope matches the wave
- date suffix — disambiguates from future snapshots

**What supports it:**
- All four benchmark apps are runnable, bounded, and have correctness oracles
- Claim boundaries are explicitly marked `release_claim_authorized: False` in app metadata
- Goal2549 rejection guard and Goal2550 closeout are included
- Evidence reports (goal2467–2471, goal2551) are present but not staged as publishable performance claims

**What should be excluded from any public release:**
- The `RtdlDb*` / `DbScan*` vocabulary in the public ABI header — these are a renaming time-bomb
- The missing `overflowed_out` on six grouped reduction functions — this is a silent data-loss risk for callers
- `robot_collision_pose_flags_optix_prepared_partner_device_columns` in `partner_adapters.py` — app-specific name in a shared module
- The "numeric RayDB-style columns only" wording in `columnar_partner.py:97` — anchors a public API contract to a benchmark app

The snapshot is appropriate to send to external reviewers with the explicit caveat that naming is pre-stabilization. It should not be tagged as `v*` or carry release notes phrasing.

---

## Prioritized Next-Work List

| Priority | Goal | Evidence | Est. Risk |
|---|---|---|---|
| **P0** | Rename `RtdlDb*` / `DbScan*` to generic columnar/predicate names in `rtdl_optix_prelude.h`, `rtdl_optix_core.cpp`, and `rtdl_optix_workloads.cpp` before any external ABI usage | `rtdl_optix_prelude.h:279–370`, `rtdl_optix_core.cpp:5394–5805`, `rtdl_optix_workloads.cpp:32–1400+` | Low (mechanical rename) |
| **P0** | Add `uint32_t* overflowed_out` to all six `_with_capacity` grouped-reduction signatures | `rtdl_optix_prelude.h:1132–1192` | Low (ABI additive) |
| **P1** | Move `robot_collision_pose_flags_optix_prepared_partner_device_columns` from `partner_adapters.py:5702` to the robot collision benchmark or an `rtdsl.app_adapters` sub-module | `src/rtdsl/partner_adapters.py:5702` | Low |
| **P1** | Remove "RayDB-style" from `columnar_partner.py:97`; replace with "numeric columnar aggregate columns" | `src/rtdsl/columnar_partner.py:97` | Trivial |
| **P1** | Refactor RT-DBSCAN's duplicate union-find builders into a single `union_find_from_proposals()` function | `rtdl_rt_dbscan_benchmark_app.py:298–430` | Medium |
| **P2** | Introduce `DeviceColumnDescriptor` dataclass unifying `columnar_partner.py`, `partner_adapters.py`, and `optix_runtime.py` column descriptor logic | Multiple files | Medium |
| **P2** | Add a source-level CI check: grep `src/native/` for `dbscan`, `raydb`, `robot`, `collision`, `barnes`, `force`, `inverse_square`; fail if found outside an allowlist comment | New CI target | Low |
| **P2** | Collapse Hausdorff's three `_run_partner_*_directed()` functions into a parameterized template | `rtdl_hausdorff_distance_app.py:277–348` | Low |
| **P3** | Document or expose `grouped_union_query_block_size` at the engine level, or explicitly mark it as RT-DBSCAN policy | `rtdl_rt_dbscan_benchmark_app.py:860–862` | Low |
| **P3** | Design operator plug-in mechanism before allowing fused inverse-square math in native OptiX | `aggregate_tree_reference.py:11–22` | High (design cost) |
| **P3** | Unified evidence manifest (machine-readable, per Goal E in codex) | New artifact | Low |

---

## Summary Verdict

The native engine has two concrete, actionable defects: (1) the `RtdlDb*` / `DbScan*` naming family is DBMS vocabulary embedded in a public C ABI header and two implementation files, and (2) the six `_with_capacity` grouped-reduction variants lack `overflowed_out`, making silent data loss possible for callers who hit capacity. Both are pre-stabilization defects that are cheap to fix now and expensive to fix after external code depends on the ABI.

All other app-specific leakage (`robot_collision_pose_flags` in `partner_adapters.py`, "RayDB-style" in `columnar_partner.py`) is at the Python layer and one line or one function move each.

The four benchmark apps are well-bounded and correctly isolated. The internal snapshot label is appropriate as written. The P0 renames and overflow fix should precede any external sharing of the header.
