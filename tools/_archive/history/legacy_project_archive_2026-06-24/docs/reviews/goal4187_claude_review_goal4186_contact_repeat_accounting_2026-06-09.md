# Goal4187 Claude Review: Goal4186 Contact Native Collect Repeat Accounting

**Date:** 2026-06-09  
**Reviewer:** Claude (claude-sonnet-4-6)  
**Verdict:** `accept`  
**Review type:** Measurement-hardening review, not a release authorization review.

---

## Scope

This review covers the files listed in the Goal4186 handoff:

- `examples/v2_0/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py`
- `tests/goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test.py`
- `docs/reports/goal4185_short_row_stress_calibration_rtx4000ada_2026-06-09.md`
- `tests/goal4185_short_row_stress_calibration_test.py`
- `docs/reports/goal4186_contact_native_collect_repeat_accounting_rtx4000ada_2026-06-09.md`
- `docs/reports/goal4186_contact_native_collect_repeat_accounting_rtx4000ada/contact_manifold_optix_grid64_repeat10000.stdout.json`
- `tests/goal4186_contact_native_collect_repeat_accounting_test.py`

---

## Q1 — Does Goal4186 correctly fix the `native_collect_k` repeat-accounting gap found by Goal4185?

**Yes. The fix is complete and correctly wired.**

Goal4185 identified: *"Not claim-grade yet: the front door does not expose repeat-aware aggregate timing or repeat metadata for this mode."* The specific problem was that `native_collect_k` accepted `--repeat-count` but only reported a single short `native_collect_elapsed_sec` value, making the aggregate run time invisible to downstream consumers.

Goal4186 addresses this in `native_collect_k_payload` (app lines 782–868):

- A loop over `repeat_count` calls accumulates wall times in `native_runs_sec: list[float]` (lines 804–817).
- After all runs, the aggregate fields are computed and emitted (lines 822–860):
  - `native_collect_elapsed_sec` = `statistics.median(native_runs_sec)` — the median of all runs.
  - `native_collect_runs_sec` = the full per-run tuple.
  - `native_collect_total_sec` = `sum(native_runs_sec)`.
  - `native_collect_min_sec` / `native_collect_max_sec`.
  - `native_collect_repeat_count` (mirrors `repeat_count`).
  - `native_collect_timing_scope` = `"median_preserves_legacy_field_total_records_repeat_aggregate"`.
- A cross-run correctness guard (lines 818–819) rejects runs where `candidate_id_rows` changes between iterations; the app fails closed rather than silently accepting non-determinism.

The RTX 4000 Ada artifact shows `native_collect_total_sec: 2.063397765159607` with `repeat_count: 10000`, which directly crosses the one-second stress-evidence threshold. The gap identified in Goal4185 is closed.

---

## Q2 — Does the old `native_collect_elapsed_sec` field remain compatibility-safe as a median-style value?

**Yes, with one minor semantic nuance that is correctly documented.**

When `repeat_count=1` (the backward-compatible case), `statistics.median([x]) == x`, so `native_collect_elapsed_sec` equals the single run time — identical to the previous behavior.

When `repeat_count>1`, `native_collect_elapsed_sec` becomes the median of multiple runs rather than a single wall-clock measurement. This is a redefinition, but it is:

1. Explicitly scoped by `native_collect_timing_scope: "median_preserves_legacy_field_total_records_repeat_aggregate"`.
2. Verified by the test in `goal2621` (line 64): `self.assertEqual(payload["native_collect_elapsed_sec"], app.statistics.median(payload["native_collect_runs_sec"]))`.
3. Verified again in `goal4186` test (line 30): `self.assertEqual(payload["native_collect_elapsed_sec"], statistics.median(runs))`.

Consumers who need aggregate evidence should read `native_collect_total_sec` (the true sum) and `native_collect_runs_sec`. Consumers who only read the legacy `native_collect_elapsed_sec` continue to receive a stable per-run representative value. The `native_collect_timing_scope` tag provides unambiguous documentation of the contract. **No compatibility hazard.**

---

## Q3 — Does the RTX 4000 Ada artifact prove second-level aggregate timing without changing app semantics?

**Yes. The artifact is internally consistent and crosses the stress threshold.**

Key fields from `contact_manifold_optix_grid64_repeat10000.stdout.json`:

| Field | Value |
|---|---|
| `repeat_count` | 10000 |
| `native_collect_repeat_count` | 10000 |
| `len(native_collect_runs_sec)` | 10000 |
| `native_collect_total_sec` | 2.063397765159607 |
| `native_collect_elapsed_sec` | 0.00020331889390945435 |
| `native_collect_min_sec` | 0.000197678804397583 |
| `native_collect_max_sec` | 0.0009395405650138855 |
| `valid_count` | 64 |
| `matches_cpu_reference` | `true` |
| `overflowed` | `false` |
| `native_generic_symbol` | `rtdl_optix_collect_k_bounded_i64` |

App semantics are unchanged across repeats:
- `claim_boundary` is the same text present before this goal: *"Native mode validates only the generic app-name-free COLLECT_K_BOUNDED i64 collector over Python oracle rows."*
- `engine_boundary.native_collision_logic_allowed: false` is unchanged.
- `candidate_id_rows` contains 64 rows matching the grid_64 oracle — no regression.

The artifact also carries `v2_4_phase_timing.validation.status: "accept"` and `promoted_performance_path: false`, consistent with a measurement-hardening run rather than a promoted performance path.

---

## Q4 — Does the implementation keep the native engine app-agnostic?

**Yes. No contact or collision vocabulary enters the native symbol layer.**

App code (line 803):
```python
symbol_name = f"rtdl_{normalized_backend}_collect_k_bounded_i64"
```

The symbol name is a generic `collect_k_bounded_i64` pattern, not `collect_contact_*` or `collect_collision_*`. The call uses the generic `rt.collect_native_i64_rows_with_backend_symbol` API (lines 808–816).

The `v2_4_prepared_session` descriptor in the artifact confirms:
- `"native_symbols": ["rtdl_optix_collect_k_bounded_i64"]`
- `"app_specific_native_vocab_allowed": false`
- `"native_engine_boundary": "app_agnostic_native_engine"`
- `"app_owned_interpretation": "Rows may represent contact witnesses in this benchmark, but RTDL sees only bounded int64 rows and valid_count."`

The test in `goal4186` enforces this at the artifact level:
```python
self.assertNotIn("rtdl_optix_contact", json.dumps(payload).lower())
self.assertNotIn("rtdl_optix_collision", json.dumps(payload).lower())
```

The `goal2621` test independently verifies the source code does not contain collision-specific native symbols (test `test_app_source_does_not_call_collision_specific_native_symbols`). The boundary is maintained at both source and artifact levels.

---

## Q5 — Does the report avoid overclaims?

**Yes. The report is appropriately scoped.**

From `goal4186_contact_native_collect_repeat_accounting_rtx4000ada_2026-06-09.md`:

> *"This is not a new public speedup claim. It is measurement hardening for one of the short-row benchmark rows."*

> *"The native engine remains app-agnostic"*

No release authorization, no broad acceleration, no zero-copy claim, no public speedup ratio language. The `goal4186` test validates the absence of `"release authorized"` and `"broad speedup"` strings (case-insensitive) from the report text.

---

## Minor Observations (non-blocking)

1. **`v2_4_phase_timing` uses the per-run median, not the aggregate total.** The `v2_4_phase_timing.phases_sec.materialization` field in the artifact carries `0.000203...` — the per-run median — rather than the aggregate `native_collect_total_sec`. This is correct given `promoted_performance_path: false`, but a future claim-grade row would need the phase-timing entry to reflect the aggregate or be explicitly labeled as a per-run value. No action needed at this stage.

2. **`repeat_count` appears twice in the payload** (`repeat_count` and `native_collect_repeat_count` both equal 10000). The redundancy is harmless; the `native_collect_repeat_count` key is the measurement-scoped label, and keeping `repeat_count` as a generic top-level parameter allows the app dispatch layer to remain clean.

---

## Verdict

**`accept`**

Goal4186 is a clean, targeted measurement-hardening change. It correctly closes the repeat-accounting gap identified by Goal4185, preserves the legacy field under a documented median contract, provides >1 s aggregate evidence on RTX 4000 Ada, maintains the generic native engine boundary at every level (source, artifact, test), and makes no overclaims. The test suite covers all correctness, boundary, and overclaim invariants.
