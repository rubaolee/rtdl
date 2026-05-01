## Goal1132 Verdict: **ACCEPT**

All three focal questions check out cleanly.

---

### 1. App-level phase timing — correct

**OptiX `directed_threshold_prepared`:**
- `_run_optix_directed_threshold()` (app.py:229–251) times prepare and query independently inside each directed call, storing them in the returned `run_phases` dict.
- `run_app()` (app.py:309–314) aggregates both directed calls into the top-level `run_phases`, adding `input_construction_sec`, `python_postprocess_sec`, and `validation_sec`.
- Result: five phases are present and sum to total work. Report claims match code exactly.

**Embree `directed_summary`:**
- One `query_start` timer wraps both `directed_hausdorff_2d_embree` calls (app.py:358–361), producing `native_directed_summary_sec`.
- `validation_sec` is separately timed. `input_construction_sec` is captured at entry.
- JSON evidence (1000 copies / 4000 pts per side) confirms all three fields are present.

---

### 2. Scalar threshold avoids row materialization — correct

`_run_optix_directed_threshold()` calls `prepared.count_threshold_reached(...)` (scalar int), never `prepared.run()` (row-returning). This is structurally enforced: `_FakePreparedThreshold.run()` raises `AssertionError` in both goal879 and goal1132 test fixtures, and both test suites pass. `row_count: None` in the returned payload labels the absence of rows. No materialization occurs.

---

### 3. Hausdorff public speedup correctly kept blocked — correct

The report is explicit and consistent with REFRESH_LOCAL: the analytic tiled oracle (`cpu_reference_total_sec: 6.9e-05 s` for 80k points) is not a same-semantics baseline. Forbidden wording is listed. The cloud claim contract status is `deferred_until_real_rtx_phase_run_and_review`. Nothing in the code or report claims a public RTX speedup.

---

### Minor observation (non-blocking)

The dry-run JSON's `cloud_claim_contract.required_phase_groups` (from the Goal887 profiler schema) lists `input_build_sec`, `point_pack_sec`, and `optix_close_sec` — none of which match the app's actual field names (`input_construction_sec`; no pack or close phases). This is a Goal887 schema artifact that predates Goal1132 and doesn't affect local correctness. It should be resolved before a cloud run uses this schema as a compliance checklist.

---

### Summary

Goal1132 correctly instruments both accelerated subpaths with phase timing, keeps the scalar count path free of row materialization, and preserves the public speedup block with consistent wording. **ACCEPT.**
