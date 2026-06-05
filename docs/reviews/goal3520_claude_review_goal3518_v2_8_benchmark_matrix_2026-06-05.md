# Goal3520: Claude Review — Goal3518 v2.8 Benchmark Matrix

Date: 2026-06-05
Reviewer: Claude (independent read-only review)
Verdict: **accept**

---

## Scope

Independent review of:
- `src/rtdsl/v2_8_benchmark_matrix.py`
- `src/rtdsl/__init__.py` (export surface)
- `tests/goal3518_v2_8_benchmark_matrix_test.py`
- `docs/reports/goal3518_v2_8_benchmark_matrix_refresh_2026-06-05.md`

Evidence artifacts cross-checked:
- `docs/reports/goal2968_current_packet_plus_raydb_gate_triage_2026-06-01.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json`
- `docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2801_hausdorff_xhd.json`
- `docs/reports/goal2965_raydb_current_gate_pod/goal2965_raydb_same_contract_gate_current.json`
- `docs/reports/goal3511_overlay_area_steady_state_relation_stream_pod_2026-06-05.json`

---

## Q1: App Coverage — All 10 Promoted Apps Present, Extra Rows Justified

`V2_8_PROMOTED_BENCHMARK_APPS` (from `v2_8_benchmark_runtime_gap.py`) contains exactly 10 apps:
`hausdorff_xhd`, `spatial_rayjoin`, `rt_dbscan`, `robot_collision`, `contact_manifold`,
`raydb_style`, `barnes_hut`, `librts_spatial_index`, `rtnn`, `triangle_counting`.

The matrix has 12 rows across those 10 apps. The two apps with extra rows:

- **`spatial_rayjoin`** (2 rows): `count_parity_prepared` vs `overlay_area_exact_prepared`. These are genuinely different contracts — count/parity is a sub-second scalar path; overlay-area requires a full prepare/warm/steady/validate workflow with separate timing. Justified.
- **`raydb_style`** (2 rows): `count_primitive_first` vs `sum_primitive_first`. The Goal2965 gate tests count and sum at separate row counts with measurably different steady-state times (0.459 ms vs 2.162 ms). Justified.

The `__post_init__` validator rejects any row whose `app` is not in `V2_8_PROMOTED_BENCHMARK_APPS`, and `validate_v2_8_benchmark_matrix()` enforces `apps == set(V2_8_PROMOTED_BENCHMARK_APPS)`. The test confirms `app_count == 10`. **Pass.**

---

## Q2: Classification Honesty and App-Agnosticism

All three lanes are used across the 12 rows.

| Classification | Rows | Assessment |
|---|---|---|
| `primitive_only` | hausdorff_xhd, contact_manifold, raydb_style×2, triangle_counting (5) | Single generic OptiX primitive or fused reduction; no partner required. Honest. |
| `partner_needed` | rt_dbscan, barnes_hut (2) | CuPy explicitly required for component labeling and vector sums, respectively. Honest. |
| `prepared_execution_needed` | spatial_rayjoin×2, robot_collision, librts_spatial_index, rtnn (5) | Full prepare/warm/steady cycle required. Honest. |

**`contact_manifold` as `primitive_only`**: The recommended path is a "prepared bounded witness collection primitive". The word "prepared" here refers to the primitive type, not a user-visible workflow phase with a separate cached artifact. The evidence from Goal2654 reports a total, not a phase split. This classification is defensible.

**`robot_collision` as `prepared_execution_needed`**: Classified with evidence "legacy_total_only_from_goal2654". The class is honest about the path type; the evidence gap is disclosed in the status fields. Acceptable.

No row encodes app-specific engine logic or hidden dispatch. All `recommended_path` strings reference generic RTDL constructs. **Pass.**

---

## Q3: Timing Cells — Numeric or Explicitly Explained

Every row was checked. Findings:

- All `steady_state_sec` values are numeric floats. All 12 pass the `steady_state_sec >= 0.0` invariant.
- Rows that lack a numeric `setup_sec` or `warmup_sec` carry an explicit string explanation in the corresponding `_status` field. Examples that were verified:
  - `hausdorff_xhd`: `setup_sec=None` / status: "not_separately_recorded_in_goal2801; one RTDL warmup captures first-run setup" — correct, the Goal2801 artifact has a single combined warmup.
  - `rt_dbscan`: both `setup_sec` and `warmup_sec` are None with explicit explanations referencing Goal2802's measurement scope.
  - `robot_collision` and `contact_manifold`: "legacy_total_only_from_goal2654" — honest about evidence tier.
  - `raydb_style` rows: "same-contract gate reports prepared primitive median; setup excluded by gate contract" — matches Goal2965 gate design.

No row carries a bare `n/a`, empty string, `TODO`, or `TBD`. The dataclass `__post_init__` and `validate_v2_8_benchmark_matrix()` enforce this programmatically. **Pass.**

---

## Q4: Overlay Row Phase Separation and Claim Boundary

The `spatial_rayjoin_overlay_area_exact_prepared` row was cross-checked against Goal3511 `timing_sec` fields:

| Phase | Matrix value | Goal3511 field | Match |
|---|---|---|---|
| `setup_sec` | 0.192737128585577 | `payload_cache_load: 0.192737128585577` | Exact ✓ |
| `warmup_sec` | 0.386260448955 | sum of `active_relation_device_columns_warmup_secs` [0.37163624819368124, 0.0074598342180252075, 0.007164366543292999] = 0.38626044895499944 | Match within floating-point precision (Δ ≈ 5×10⁻¹⁶) ✓ |
| `steady_state_sec` | 0.06988946907222271 | `active_relation_device_columns` (0.0038709240034222603) + `device_tile_task_planning_best_repeat` (0.05171292740851641) + `cupy_tile_task_executor_best_repeat` (0.014305617660284042) = 0.06988946907222271 | Exact ✓ |
| `validation_sec` | 0.26809314265847206 | `exact_oracle: 0.26809314265847206` | Exact ✓ |

The `setup_status` explicitly states "binary prepared-payload cache load; geometry/payload write is excluded from steady-state". The steady-state is the post-warmup best-repeat sum, not the total elapsed. Phases are not collapsed. **Pass.**

RayJoin claims:
- `claim_boundary_status`: "no RayJoin reproduction, no rtdl-beats-RayJoin, and no full overlay-geometry claim"
- Goal3511 artifact: `rayjoin_paper_reproduction_claim_authorized: false`, `rtdl_beats_rayjoin_claim_authorized: false`
- The correctness note quotes "1086 positive rows observed" and "matches Shapely/GEOS total within 1e-8" — consistent with Goal3511 (`exact_positive_row_count: 1086`, `total_area_abs_error: 9.23e-9 < 1e-8`).

No paper-reproduction claims present. **Pass.**

---

## Q5: Claim-Boundary Flags All False

All 7 flags (`release_authorized`, `public_speedup_claim_authorized`, `whole_app_speedup_claim_authorized`, `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, `paper_reproduction_claim_authorized`, `app_specific_engine_logic_allowed`) are hard-coded to `False` in the dataclass defaults.

The `__post_init__` raises `ValueError` on any row that sets a flag to `True`. `validate_v2_8_benchmark_matrix()` checks all 7 flags per row. The test `test_claim_boundaries_remain_false` iterates all 12 rows and all 7 flags. **Pass.**

---

## Q6: Number Verification Against Evidence Artifacts

Numbers that could be directly cross-checked:

| Row | Field | Matrix value | Artifact source | Match |
|---|---|---|---|---|
| hausdorff_xhd | `warmup_sec` | 0.8969316319562495 | Goal2801: `rtdl.warmup_elapsed_sec` | Exact ✓ |
| hausdorff_xhd | `steady_state_sec` | 0.007444375194609165 | Goal2801: `rtdl.median_elapsed_sec` | Exact ✓ |
| raydb_style count | `steady_state_sec` | 0.00045938510447740555 | Goal2965: `primitive_first_median_wall_sec` (count, 1M rows) | Exact ✓ |
| raydb_style sum | `steady_state_sec` | 0.002161583164706826 | Goal2965: `primitive_first_median_wall_sec` (sum, 1M rows) | Exact ✓ |
| overlay_area | `setup_sec` | 0.192737128585577 | Goal3511: `payload_cache_load` | Exact ✓ |
| overlay_area | `warmup_sec` | 0.386260448955 | Goal3511: sum of warmup secs | Within FP precision ✓ |
| overlay_area | `steady_state_sec` | 0.06988946907222271 | Goal3511: best-repeat sum | Exact ✓ |
| overlay_area | `validation_sec` | 0.26809314265847206 | Goal3511: `exact_oracle` | Exact ✓ |
| triangle_counting | `steady_state_sec` | 0.0004133919719606638 (≈ 0.413 ms) | Goal2968 triage: `max_query_median_ms: 0.413` | Consistent ✓ |
| librts | `steady_state_sec` | 0.001551950117573142 (≈ 1.552 ms) | Goal2968 triage: `max_query_median_ms: 1.552` | Consistent ✓ |

No incorrect transcription found. **Pass.**

---

## Observations (Non-Blocking)

1. **`robot_collision` and `contact_manifold` evidence tier**: Both rows rely on Goal2654 total timing (not fresh v2.8 phase splits). The steady_state_status on both rows says "accepted OptiX total from Goal2654, not a fresh v2.8 split". This is disclosed, not hidden, and the report's Next Pod Refresh section explicitly calls these out as items 1 and 2 in the gap list. Acceptable for an internal matrix; should not appear in any external-facing comparison.

2. **`barnes_hut` large steady-state (18.033 sec)**: The steady_state_status clarifies "largest-case OptiX total median at 8192 bodies; vector partner median is 0.000696728 sec". The vector partner (0.697 ms) is correctly broken out from the total. The notes explain the RT membership dominates at this scale. No inflation or collapsing concern.

3. **`spatial_rayjoin_count_parity` setup > steady-state**: `setup_sec` (0.0001745 sec) slightly exceeds `steady_state_sec` (0.0001611 sec). The status fields explain these are the "largest" values from different rows in Goal2799 — they are not necessarily from the same row. This is internally consistent with using conservative upper-bound values per phase.

---

## Verdict

**accept**

The matrix covers all 10 promoted v2.8 benchmark apps. Extra rows exist only for `spatial_rayjoin` (count/parity vs overlay-area) and `raydb_style` (count vs sum), both of which represent genuinely distinct contracts with different timing profiles. All classifications are honest and app-agnostic. Every timing cell is either numeric or carries an explicit description of why the phase is absent; there are no bare placeholders. The overlay row cleanly separates all four phases and all numbers were verified against Goal3511 exactly. All seven claim-boundary flags remain false, enforced by `__post_init__`, the validator, and the test suite. No incorrect transcription was found in any cross-checked number.
