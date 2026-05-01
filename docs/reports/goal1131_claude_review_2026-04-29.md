Now I have everything I need. Here is the verdict.

---

## Goal1131 Review — 2026-04-29

**VERDICT: ACCEPT**

---

### 1. Phase Timing Observability

Correct and consistent across both apps.

**Polygon-pair overlap** (`rtdl_polygon_pair_overlap_area_rows.py:296–340`):
- CPU paths: `input_construction_sec` + `query_and_materialize_sec` + `summary_postprocess_sec`
- Embree/OptiX paths: `input_construction_sec` + `rt_candidate_discovery_sec` + `native_exact_continuation_sec`
- The summary path for embree/optix uses `_exact_overlap_summary_for_candidates` inside the timed continuation block — discovery and exact work are separately attributable. ✓

**Polygon-set Jaccard** (`rtdl_polygon_set_jaccard.py:156–172`):
- Same two-phase split for native backends. Native paths also emit `summary_postprocess_sec` (a trivially fast `dict(rows[0])` copy, ~300 ns in the artifact). The contract doc says only CPU paths expose it, but the artifact confirms it's harmless and honest. Minor asymmetry, not a blocker.

**Phase profiler** (`scripts/goal877_polygon_overlap_optix_phase_profiler.py:260–317`):
- Summary mode uses chunked accumulation; `optix_candidate_discovery_sec` and `native_exact_continuation_sec` are accumulated per-chunk and reported correctly. The `run_phases` field is stripped by `_canonical` before parity comparison, so timing noise cannot cause false parity failures. ✓

---

### 2. Jaccard Summary Semantics

`output_mode="summary"` correctly omits `rows` from the payload while setting `summary = dict(rows[0])`, which is the complete aggregate Jaccard row (`intersection_area`, `left_area`, `right_area`, `union_area`, `jaccard_similarity`). `row_count` remains `len(rows)` (1), not 0. The contract test at `goal1131_polygon_app_phase_contract_test.py:23–30` directly asserts `summary_payload["summary"] == rows_payload["rows"][0]` and equal `row_count`. ✓

For the chunked profiler in summary mode, Jaccard is accumulated as `sum(intersection_area) / sum(union_area)` across spatially disjoint chunks, which is mathematically correct for non-overlapping tile sets. ✓

---

### 3. Parity Test Integrity

`goal713_polygon_overlap_embree_app_test.py` now strips `run_phases` from `_canonical` comparison (`goal713_polygon_overlap_embree_app_test.py:12–31`). This is necessary since timing fields would cause false negatives; the omission is safe because `goal1131_polygon_app_phase_contract_test.py` explicitly checks that the correct phase keys are present. The two tests are complementary — goal713 owns result correctness, goal1131 owns phase-key contract. ✓

`goal877` profiler tests still assert `parity_vs_cpu=True` for mocked optix runs and explicitly test the analytic_summary path with chunk diagnostics. The `candidate_count_matches_expected=False` assertion in `test_pair_overlap_summary_analytic_chunks_without_cpu_reference:65` correctly documents the expected divergence under mocked candidate discovery — this is a documented diagnostic behavior, not a masked failure. ✓

---

### 4. RTX Claim Boundaries

Both app payloads hardcode `rt_core_accelerated: False` unconditionally (`rtdl_polygon_pair_overlap_area_rows.py:359`, `rtdl_polygon_set_jaccard.py:204`). `rt_core_candidate_discovery_active` is `True` only when `backend == "optix"`. The local Embree artifacts confirm `rt_core_candidate_discovery_active: false` for embree runs.

One minor point: `_cpu_payload()` in the profiler (`goal877_polygon_overlap_optix_phase_profiler.py:113`) sets `rt_core_candidate_discovery_active: True` for the CPU reference summary path — factually wrong. However, this field is in `_canonical`'s exclusion list, so it never surfaces in parity comparison or in `optix_metadata` (which reads from `optix_payload`). Pre-existing issue, not introduced by Goal1131, not a blocker.

`boundary` strings in both apps and the profiler consistently deny monolithic GPU kernel claims and full-app RTX speedup. ✓

---

### Summary

No blockers. The phase split is observable, correctly timed, and honestly labeled. Jaccard summary output is semantically faithful. Parity tests cover the right invariants. No RTX overclaim is introduced or implied. Goal1131 is ready for Codex consensus.
