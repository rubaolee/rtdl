Now I have everything needed for the review. Here is the complete critical review.

---

# Review: Phoenix V3 RayDB M28 Grouped-Reduction Evidence

**Reviewer:** Claude Sonnet 4.6  
**Date:** 2026-06-20  
**Scope:** Internal generic grouped-reduction evidence gate only — not V3 release authorization.

---

## verdict: approve-with-required-fixes

The evidence packet is factually honest. No material false claim, no unauthorized release assertion, and no app-specific native engine logic was introduced. The core data, claim flags, and timing boundary documentation are sufficient to accept this as internal generic grouped-reduction evidence. Three P1 issues must be fixed in the test file before the goal is formally closed. They are test coverage gaps, not factual integrity failures.

---

## P0 Findings

**None.**

The following were checked and cleared:

- `public_speedup_claim_authorized=false` appears at three independent levels: the top-level `claim_boundary`, the `comparison` object, and per-row `claim_boundary`. No level is contradicted by another.
- The forbidden reading ("RayDB-style V3 is 158x faster end to end") is explicitly named in the evidence report and negated — it is not a stray overclaim left in prose.
- The native symbols (`rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction`, `rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction`) are RTDL generics. `v2_5_selection_reason="continuation_matches_existing_fused_app_agnostic_rtdl_primitive"` is consistent. No SQL engine, planner, or transaction system artifact appears in any file.
- `release_authorized=false`, `whole_app_speedup_claim_authorized=false`, `paper_reproduction_claim_authorized=false`, `Phoenix M7-qualified release rows=0` are all correctly maintained.
- The overlarge attempt file exists, names the command, timestamp, and reason, and is referenced in the test.

---

## P1 Findings

### P1-1 — `prepared_ray_batch_sec` is not called out in the narrative, creating an ambiguous cold-prepare decomposition

**Location:** `phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md` Timing Boundary section; JSON row `optix/sum`.

**Issue:** The OptiX sum row has `prepared_ray_batch_sec: 2.547s`. The report names `workload_build_sec` (213.265s) and `cold_prepare_total_sec` (215.843s), but does not explicitly state that `cold_prepare_total` subsumes the ray-batch preparation cost. A reader checking the arithmetic (215.843 − 213.265 = 2.578 ≈ 2.547 + ~0.03s other) would have to reconstruct this. The hot-query `elapsed_median_sec` (13.3ms) correctly excludes all 215s, but the decomposition of those 215s is not spelled out. A future reader who knows that `prepared_ray_batch_reused=true` might still wonder whether the 2.547s ray-batch setup is amortized per-iteration or one-time. It is one-time (included in cold_prepare), but this is implicit.

**Required fix:** Add one sentence to the Timing Boundary section of the evidence report: "The `cold_prepare_total_sec` for OptiX sum (215.843s) includes both `workload_build_sec` (213.265s) and the one-time ray-batch preparation (2.547s); the hot-query `elapsed_median_sec` (13.3ms) excludes all of these." No code change needed.

---

### P1-2 — Test does not assert `rt_core_accelerated` differentiation between Embree and OptiX rows

**Location:** `tests/v3_phoenix_raydb_m28_evidence_test.py`, `test_same_contract_ratios_are_internal_hot_query_only`.

**Issue:** The comparison is between a CPU-path backend (`rt_core_accelerated=false`) and an RT-core-accelerated backend (`rt_core_accelerated=true`). This distinction is the foundation of why the ratio is meaningful. The test currently checks `v2_5_selected_path` and `partner_continuation_required` but does not assert the `rt_core_accelerated` values. A future regression that accidentally runs both backends through Embree (e.g., from a configuration error) would produce a plausible-looking but incorrect comparison and the test would not catch it.

**Required fix:** In `test_same_contract_ratios_are_internal_hot_query_only`, add:

```python
for mode in ("count", "sum"):
    self.assertFalse(rows[("embree", mode)]["rt_core_accelerated"])
    self.assertTrue(rows[("optix", mode)]["rt_core_accelerated"])
```

---

### P1-3 — Overlarge log file has only 1 line; test checks existence only, not content

**Location:** `docs/rebuild/v3/evidence/phoenix_v3_raydb_m28_grouped_reduction_20260620/m28_raydb_grouped_reduction_1048576.log`; `tests/v3_phoenix_raydb_m28_evidence_test.py`, `test_overlarge_attempt_is_preserved`.

**Issue:** The log file for the 1,048,576-row run has exactly 1 line. A run stopped after 20+ minutes should have captured at least the script invocation or initial environment output. The current test only calls `.exists()` on the log file, so it would pass even if the file were blank. For a run that is being preserved as an audit artifact, the log should demonstrate the run actually started and produced initial output. The status file (`overlarge_1048576_attempt_status.txt`) carries the essential information, but the log as an independent corroborating artifact is thin.

**Required fix (two parts):**

1. If the log content is recoverable, ensure it contains at minimum the command invocation or first environment snapshot line.
2. In `test_overlarge_attempt_is_preserved`, change the log file check from existence-only to a content check:

```python
log_text = (EVIDENCE / "m28_raydb_grouped_reduction_1048576.log").read_text(encoding="utf-8")
self.assertTrue(len(log_text.strip()) > 0, "overlarge log file must contain at least one line of output")
```

---

### P1-4 — Embree sum row uses only 5 repeats; statistical context is absent from the report

**Location:** JSON `rows[embree/sum].repeat = 5`; evidence report "Result" section.

**Issue:** The Embree sum row median (2.104s) is derived from 5 measurements (after 2 warmups). This is a practical necessity — 5 × 2.1s = 10.5s measured time, and 1 × 2.1s warmups make this already long. But with repeat=5, the median is the 3rd measurement, which is less statistically robust than the 100-rep count row. The report table does not note repeat counts, so a reader sees "Embree 2104.065 ms" without context that this is the median of 5. The report should note the asymmetry in repeat counts between count and sum rows.

**Required fix:** Add a footnote or parenthetical in the Result table noting the repeat overrides: "count: Embree 100 reps, OptiX 1,000 reps; sum: Embree 5 reps, OptiX 500 reps." This is already in the JSON `planned_rows`, but not surfaced in the human-readable report.

---

## P2 Suggestions

### P2-1 — "raydb" in contract names could be mistaken for RayDB engine invocation

The contracts are named `raydb_paper_triangle_scan_prepared_grouped_reduction_embree/optix`. The "raydb" prefix is a benchmark fixture domain label, not evidence that a RayDB SQL engine was invoked. A one-sentence clarification in the Scope section would prevent future confusion: "The `raydb_paper_triangle_scan_*` contract names reflect the benchmark fixture domain; no RayDB engine, query planner, or transaction system is invoked."

### P2-2 — Test does not check `comparison_scope` field value

The `comparison_scope: "internal_same_contract_prepared_query_refresh_not_public_speedup"` field is the machine-readable evidence of the scope boundary. The test currently only checks `public_speedup_claim_authorized=false`. An additional assertion on the scope string would be a stronger guard against future comparison-struct changes that might silently remove this field.

### P2-3 — Count row light-setup cost not asserted

The test asserts `workload_build_sec > 200.0` for sum rows (establishing they are heavy-setup). There is no corresponding assertion that count rows have light setup (`workload_build_sec < 5.0`). The count row builds at ~0.198s, but without an upper-bound test, a future run with unexpectedly heavy count-row setup would pass silently.

### P2-4 — `v3_release_wording_gate.py` REQUIRED_STRINGS does not include the M28 evidence report path

`v3_release_wording_gate.py` scans `DEFAULT_FILES` and the scanned set includes `docs/rebuild/v3/phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md`. The `REQUIRED_STRINGS` list does not include a string that would force the scanned M28 report to actually confirm any of its own key fields (e.g., `"Phoenix M7-qualified release rows=0"` is only checked in the aggregate join, not attributed to the M28 report specifically). This is low risk given the gate already fails on that string being absent from the joined text, but per-document anchoring would be more robust.

---

## Final Recommendation

**Accept as bounded internal generic grouped-reduction evidence** after addressing P1-1 through P1-4.

The evidence correctly isolates hot-query timing from the 213s+ workload build and cold-prepare costs, uses a verified app-agnostic primitive, passes CPU reference parity on all four rows, and prohibits every public claim. The 524,288-row scale is non-toy. The overlarge attempt is preserved with a command and timestamp record.

The P1 items are all test-and-documentation hardening, not corrections to the data itself. None of them indicate that the data was collected or reported dishonestly. They should be fixed before formal goal closure to ensure that the test suite independently enforces the boundaries that the narrative documents, and that future readers have the full timing decomposition in the report.

**This evidence does not authorize any public release claim, public speedup wording, or M7 row qualification. Phoenix M7-qualified release rows remain 0.**
