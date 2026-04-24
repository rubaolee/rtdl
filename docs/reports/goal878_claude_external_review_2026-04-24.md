# Goal878 External Review — 2026-04-24

Reviewer: Claude (claude-sonnet-4-6), independent read of all listed files.

## Verdict: ACCEPT

No blockers found. All four review questions pass.

---

## Q1: Routing — does `--backend optix --output-mode rows --optix-mode native` call the bounded native pair-row emitter?

**Pass.**

`examples/rtdl_segment_polygon_anyhit_rows.py` `run_case()` branches cleanly:

```python
if backend == "optix" and optix_mode == "native":          # → _run_native_anyhit_rows_optix
else:                                                       # → _run_anyhit_rows (host-indexed)
```

`_run_anyhit_rows` additionally raises `ValueError` if `optix_mode == "native"` is ever passed to it directly, preventing accidental fallback. `_run_native_anyhit_rows_optix` calls `rt.segment_polygon_anyhit_rows_native_bounded_optix(...)` which dispatches to the `rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded` C symbol in the backend library. The host-indexed path (`run_optix`) is never reached when `optix_mode="native"` + `output_mode="rows"`.

The payload fields `summary_source`, `rt_core_accelerated`, and `native_output_capacity` are set correctly only on the native path.

---

## Q2: Overflow policy — honest and safe for public explicit native mode?

**Pass.**

`segment_polygon_anyhit_rows_native_bounded_optix` in `optix_runtime.py` (lines 2381–2435):

- Raises `ValueError("output_capacity must be positive")` for `<= 0` before any backend call.
- Allocates exactly `output_capacity` rows in a ctypes array; the C backend writes an `overflowed` flag.
- On overflow, raises `RuntimeError` with capacity and a lower-bound emitted count — no silent truncation.
- If the backend library lacks the symbol, raises `ValueError` with an explicit rebuild instruction.

The policy is honest: callers must size the buffer, and overflow is reported loudly. The payload `boundary` string and all docs repeat this contract.

---

## Q3: Do docs avoid claiming speedup before Goal873 strict RTX artifact review?

**Pass.**

Every touchpoint is consistent:

| Location | Claim-limiting language |
|---|---|
| `docs/features/segment_polygon_anyhit_rows/README.md` | "still behind the Goal873 strict RTX artifact gate for speedup promotion" |
| `docs/tutorials/segment_polygon_workloads.md` | "speedup promotion still requires the Goal873 strict RTX gate, row-digest parity, zero overflow, and independent review" |
| `docs/app_engine_support_matrix.md` (readiness row) | allowed_claim = "native bounded pair-row traversal path only; no pair-row speedup claim today" |
| `docs/application_catalog.md` | "speedup promotion still needs Goal873 RTX artifact review" |
| `examples/rtdl_segment_polygon_anyhit_rows.py` payload `boundary` | "speedup claims still require strict RTX artifact review" |

No doc in the set asserts a measured speedup or promotes native mode as the default performance path.

---

## Q4: Support/readiness/maturity matrix — conservative and internally consistent?

**Pass.**

| Matrix | `segment_polygon_anyhit_rows` value | Assessment |
|---|---|---|
| `app_engine_support` (optix) | `direct_cli_native` | Correct — native CLI is now publicly exposed |
| `optix_app_performance_class` | `host_indexed_fallback` | Conservative — default path still host-indexed |
| `optix_app_benchmark_readiness` | `needs_real_rtx_artifact` / next=Goal873 | Correct gate |
| `rt_core_app_maturity` (current) | `rt_core_partial_ready` | Correct — real traversal exists but no RTX artifact yet |

The combination of `direct_cli_native` (engine surface) + `host_indexed_fallback` (performance class) is intentional and documented: the exposed native mode does not promote the default-path performance claim. The goal707 test explicitly pins this distinction. All three sibling apps (`road_hazard_screening`, `segment_polygon_hitcount`) remain `direct_cli_compatibility_fallback` / `needs_rt_core_redesign`, which is consistent — they do not yet have an exposed bounded-native rows mode.

The matrices are fully consistent across `app_support_matrix.py`, `docs/app_engine_support_matrix.md`, and the pinning tests in goal705/goal707/goal820/goal878.

---

## Summary

Goal878 correctly wires the bounded native pair-row emitter through the public app CLI, documents the overflow-fail contract honestly, makes no premature speedup claims, and updates all three matrices conservatively. Tests (`33 OK` per the goal self-report) and code logic agree. No blockers.

---

# Goal878 Delta Review — 2026-04-24 (post-ACCEPT)

Reviewer: Claude (claude-sonnet-4-6), independent read of the three changed files plus live test run.

## Verdict: ACCEPT

No blockers. All three deltas are correct, internally consistent, and pass tests.

---

## D1: `scripts/goal515_public_command_truth_audit.py` — GOAL878_COMMANDS block

Six commands added (lines 53–60):

```
python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode host_indexed --copies 4
python examples/rtdl_segment_polygon_hitcount.py --backend optix --optix-mode native --copies 4
python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode segment_counts --optix-mode native --copies 4
python examples/rtdl_segment_polygon_anyhit_rows.py --backend optix --output-mode rows --optix-mode native --copies 4 --output-capacity 1000000
python examples/rtdl_polygon_pair_overlap_area_rows.py --backend optix --output-mode summary
python examples/rtdl_polygon_set_jaccard.py --backend optix
```

Coverage label: `goal878_optix_doc_gate_exact`. Wired in `build_coverage_maps()` via `setdefault` — existing goal410/goal513/goal821 exact hits are not overwritten.

Live audit result: `valid=True`, `goal878_optix_doc_gate_exact: 8` hits (8 > 6 because two commands appear in multiple public doc files — expected). No uncovered commands.

Classification: all six carry `--backend optix` so are correctly tagged `linux_gpu_backend_gated` — they require RTX hardware and will not be executed in portable CI.

**Pass.**

---

## D2: `tests/goal824_pre_cloud_rtx_readiness_gate_test.py` — deferred_count 3→6, baseline_contract_count 8→11

The gate script computes `baseline_contract_count = len(active) + len(deferred)`.

Live manifest: active=5, deferred=6 → baseline_contract_count=11. Three new deferred entries are `segment_polygon_anyhit_rows`, `polygon_pair_overlap_area_rows`, `polygon_set_jaccard` — the GOAL878 apps that are now RTX-manifest-tracked but not yet RTX-cloud-active.

Consistency checks:
- `missing_excluded == []`: all REQUIRED_EXCLUDED_APPS are still in `manifest["excluded_apps"]`. The deferred promotion adds entries to `deferred_entries` without removing them from the excluded set — gate logic handles both correctly.
- `missing_deferred == []`: REQUIRED_DEFERRED_APPS = {service_coverage_gaps, event_hotspot_screening, segment_polygon_hitcount} are all present in the 6 deferred entries.
- `active_errors == []` and `baseline_contract_errors == []`: all 11 entries pass the baseline review contract check.

Live test run: 32 tests OK (including `test_gate_records_active_deferred_and_excluded_counts` which pins the exact counts).

The count update is arithmetically correct and mechanically verified. No premature activation — all three GOAL878 apps are deferred, not active.

**Pass.**

---

## D3: `docs/reports/goal878_segment_polygon_native_pair_rows_app_surface_2026-04-24.md` — broader gate section

Adds "Broader matrix/manifest gate" subsection (60-test suite) and records `valid=True` for the public command audit. The 60-test count is consistent with the full manifest+matrix test suite documented on the branch. The `valid=True` is confirmed by live audit above.

The changed-files list in the report was also updated to include `scripts/goal515_public_command_truth_audit.py` and `tests/goal824_pre_cloud_rtx_readiness_gate_test.py` — accurate and complete.

**Pass.**

---

## Delta Summary

| Delta | File | Verdict |
|---|---|---|
| GOAL878_COMMANDS in goal515 audit | `scripts/goal515_public_command_truth_audit.py` | Pass |
| deferred_count 3→6, baseline_contract_count 8→11 | `tests/goal824_pre_cloud_rtx_readiness_gate_test.py` | Pass |
| Broader gate section in surface report | `docs/reports/goal878_segment_polygon_native_pair_rows_app_surface_2026-04-24.md` | Pass |

Live test run: **32 tests OK**. Public command audit: **valid=True**. Manifest: **5 active, 6 deferred, 12 excluded**. No blockers.
