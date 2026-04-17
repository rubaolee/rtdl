# Goal 462: External Review of v0.7 DB Kernel App Demo

Date: 2026-04-16
Reviewer: Claude (external AI, second reviewer)
Verdict: ACCEPT

## Scope Reviewed

- `docs/goal_462_v0_7_db_kernel_app_demo.md`
- `examples/rtdl_v0_7_db_kernel_app_demo.py`
- `tests/goal462_v0_7_db_kernel_app_demo_test.py`
- `examples/README.md`
- `docs/reports/goal462_v0_7_db_kernel_app_demo_2026-04-16.md`
- `docs/reports/goal462_v0_7_db_kernel_app_demo_review_2026-04-16.md`

## Findings

**Acceptance criteria coverage — all satisfied:**

- Runnable kernel-form example present under `examples/` (`rtdl_v0_7_db_kernel_app_demo.py`). ✓
- Focused unit test covers CPU Python reference output (`tests/goal462_v0_7_db_kernel_app_demo_test.py`). ✓
- Implementation report documents local execution of both `--backend cpu_python_reference` and `--backend auto` (selected `embree` on the test host). ✓
- `examples/README.md` "Start Here" list includes `rtdl_v0_7_db_kernel_app_demo.py`. ✓
- 2-AI consensus requirement: first review (Codex) ACCEPT present; this review is the second. ✓

**Scope requirements — all present:**

- `rt.input(..., role="probe")` and `rt.input(..., role="build")` appear in all three kernels. ✓
- `rt.traverse(..., accel="bvh")` with `mode="db_scan"` and `mode="db_group"` variants. ✓
- `rt.refine(...)` with `conjunctive_scan`, `grouped_count`, and `grouped_sum` semantics. ✓
- `rt.emit(...)` used in all three kernels. ✓
- One-, two-, and three-predicate scan examples provided. ✓
- Grouped count and grouped sum examples provided. ✓
- `cpu_python_reference` backend provides portable execution. ✓
- `auto`, `cpu`, `embree`, `optix`, and `vulkan` backends available. ✓
- Honesty boundary string present: "not SQL, joins, transactions, or a DBMS." ✓

**Independent test value verification:**

Expected values in the unit test were independently verified against the `make_orders()` fixture:

- One-predicate (`discount=6`): rows 3, 4, 5, 7 — correct.
- Two-predicate (`ship_date 12–15` AND `quantity<20`): rows 3, 4, 5, 6, 7 — correct.
- Three-predicate (two-predicate AND `discount=6`): rows 3, 4, 5, 7 — correct (row 6 excluded by `discount=3`).
- Grouped count by region (two-predicate filter): east=2, south=1, west=2 — correct.
- Web revenue by region (`ship_date≥12` AND `channel=web`): east=180, west=240 (rows 4+5: 150+90) — correct.

No discrepancies found between the test assertions and manual evaluation of the source data.

**No blocking issues.** PostgreSQL is correctly absent from public backend flags. The demo does not overstate its capabilities. The kernel-form presentation is clear and distinct from the app-level demo (`rtdl_v0_7_db_app_demo.py`).

## Verdict

ACCEPT. All Goal 462 acceptance criteria are met. The kernel-form app demo correctly demonstrates the v0.7 bounded DB workload surface with clean kernel API usage, accurate test expectations, and an appropriate honesty boundary.
