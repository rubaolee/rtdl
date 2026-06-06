# Goal3573 Review: Goal3572 Grouped i64 Full-Reduction Small-Group Fast Path

Date: 2026-06-06
Reviewer: Claude (independent)
Verdict: **accept**

---

## Scope

This review covers Goal3572's extension of the v2.9 grouped-i64 small-group fast
path from `sum`/`sum_count` to `count`, `min`, `max`, and structurally `stats`.
Evidence is the RTX A5000 artifact at
`docs/reports/goal3572_grouped_i64_full_reduction_fastpath_preserve_long_a5000/summary.json`.
The implementation file is `src/native/optix/rtdl_optix_workloads.cpp`.

---

## Q1 — App-agnosticism of the native implementation

**Finding: clean.**

The kernel `device_column_grouped_i64_small_group_reduction_kernel` and the
selector block (`use_small_group_sum_count_fast_path` / `use_small_group_reduction_fast_path`,
lines 1503–1528) contain no RayDB, database, or application-layer vocabulary.
All symbol names use the generic primitive vocabulary
(`kDeviceColumnGroupedOpCount`, `kDeviceColumnGroupedOpMin`,
`kDeviceColumnGroupedOpMax`, `kDeviceColumnGroupedOpStats`, etc.).

The structural test in
`tests/goal3572_grouped_i64_small_group_full_reduction_fastpath_test.py` asserts
`assertNotIn("raydb", selector.lower())` and `assertNotIn("database", selector.lower())`,
and these assertions pass against the actual source text confirmed by direct grep.

---

## Q2 — Split-kernel design justification

**Finding: justified.**

The host selector at lines 1503–1528 routes `sum`/`sum_count` to the original
`device_column_grouped_i64_small_group_kernel` (v2.9 hot path, unchanged) and
routes `count`/`min`/`max`/`stats` to the new
`device_column_grouped_i64_small_group_reduction_kernel`. The two paths are
mutually exclusive; no `sum`/`sum_count` row is ever dispatched to the new kernel.

The engineering motivation — earlier generalized-kernel attempts improved
`count`/`min`/`max` but regressed `sum_count` — is supported by the A5000
artifact: `avg_as_sum_count` measures `1.0076x` (parity-positive) and `sum`
measures `0.9878x` (within noise), confirming the original kernel path is
preserved without measurable damage.

The implementation of the new kernel is internally consistent:
- Global buffers for `min`/`max` operations are initialized before kernel
  dispatch via `init_values_fn` (lines 1442–1456): `d_sums` is initialized to
  `INT64_MAX` for MIN and `INT64_MIN` for MAX.
- Shared memory allocation is operation-specific (1 array for `count`, 2 for
  `min`/`max`, 4 for `stats`), avoiding unnecessary shared-memory pressure.
- The flush stage uses `device_atomic_min_i64`/`device_atomic_max_i64` into
  `params.group_sums` for `min`/`max`, and the compaction kernel reads from that
  same buffer via the `else` branch (lines 1622–1645), which is consistent.
- For `stats`, separate `d_mins`/`d_maxs` buffers are allocated and passed in
  `params.group_mins`/`params.group_maxs`; the kernel correctly distinguishes
  the STATS flush path (lines 1075–1081) from MIN/MAX paths.

One minor internal note: the reduction kernel contains dead branches for
`RTDL_GROUPED_OP_SUM` and `RTDL_GROUPED_OP_SUM_COUNT` (in `needs_sum` and the
flush stage) that can never be reached because the selector gates those
operations to the other kernel. This is harmless and does not affect correctness.

---

## Q3 — A5000 artifact cleanliness

**Finding: clean enough for internal engineering evidence.**

Artifact fields verified:

| Field | Expected | Observed |
| --- | --- | --- |
| `baseline_commit` | `f5090057` | `f50900576489c552ddc0cf7594a718c8bec98866` |
| `candidate_commit` | `bfcb943c` | `bfcb943ce9366f448fd8fc67f02240c14f1568ba` |
| `candidate_has_uncommitted_native_change` | `false` | `false` |
| `copies` | 120000 | 120000 |
| `warmup` | 3 | 3 |
| `repeat` | 5000 | 5000 |
| `trials` | 5 | 5 |
| `all_modes_ok` | `true` | `true` |

All 50 rows (5 modes × 5 trials × 2 lanes) show `matches_cpu_reference: true`
and `status: "ok"`. No trial failed.

**On the `sum` row (0.9878x):** The baseline and candidate trial distributions
for `sum` substantially overlap (baseline range ≈ 452–499 µs; candidate range ≈
456–513 µs; medians 491 vs 497 µs). The ~1.2% difference is well within
pod-level noise, and the original `sum` kernel code path is unchanged. This is
correctly characterized as parity preservation, not a regression.

**On the isolated high `query_max_sec` outliers** in several baseline count/min
trials (e.g., trial 3 count baseline: `query_max_sec ≈ 597 ms` vs
`query_min_sec ≈ 574 µs`): these extreme outliers are single-iteration spikes
in the 5000-repeat batch, consistent with JIT compilation or OS scheduling
interference early in the run. The warmup=3 guard and median-based metric
correctly exclude them from the summary figures. Comparable spikes appear in
both lanes, so they do not bias the comparison.

The artifact is clean for internal primitive evidence purposes.

---

## Q4 — Overclaiming check

**Finding: no overclaiming.**

The report (`docs/reports/goal3572_grouped_i64_full_reduction_fastpath_2026-06-06.md`)
explicitly:

- States this is not a release packet and does not authorize public speedup
  claims.
- Notes that the `sum` row is "preserved near parity" with "no new sum speedup
  claim."
- Flags `stats` coverage as "structural/native-selector coverage only; it is
  not a measured stats performance claim."
- Lists all seven forbidden claim categories in the Boundary section.

The `claim_boundary` object in the JSON sets `internal_results_only: true` and
all other flags to `false`, and this is embedded at both the top-level and in
each per-row entry.

The A5000 test (`tests/goal3572_grouped_i64_full_reduction_fastpath_a5000_test.py`)
asserts that all forbidden claim strings appear in the report and that the JSON
boundary flags are correctly set.

No release, public, whole-app, RT-core, zero-copy, paper, or package-install
claims are present anywhere in the artifact set.

---

## Q5 — Required fixes before internal close

**Finding: none.**

All correctness checks pass. The implementation is app-agnostic. The split-kernel
design is properly motivated and consistently implemented. The A5000 artifact is
clean and correctly scoped. The claim boundary is fully respected at every layer
(report, JSON, test, probe script).

---

## Summary

Goal3572 adds shared-memory small-group fast-path coverage for `count`, `min`,
and `max` (and structurally `stats`) without disturbing the existing `sum`/`sum_count`
hot path. The A5000 evidence shows consistent speedups of 1.25–1.32x on the new
operations and parity on the preserved operations, with all correctness checks
passing. The implementation is generic, the artifact is clean, and the scope is
correctly bounded.

**Verdict: accept.**

This acceptance is scoped to internal primitive-performance evidence only. It
does not authorize release, public speedup claims, whole-app acceleration claims,
broad RT-core speedup claims, zero-copy claims, paper reproduction claims, or
package-install claims.
