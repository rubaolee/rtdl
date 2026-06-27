# Goal1857 — External Review: Goal1856 v2.0 Partner Same-Contract Timing Row

**Reviewer:** Claude (Sonnet 4.6, independent of Codex)
**Date:** 2026-05-13
**Verdict:** `accept-with-boundary`

---

## Summary

Goal1856 adds the first same-contract v2.0-vs-v1.8 timing row for the
`segment_polygon_anyhit_rows` app path. The implementation is sound for
its stated narrow purpose. Parity gating is correctly enforced, claim
boundaries are machine-readable and consistently `false` for all four
blocked categories, and the report does not overclaim. The result is
acceptable as an internal engineering data point.

All-app v2.0 performance readiness and release authorization remain
blocked. The following sections document the basis for acceptance, the
boundary conditions that hold, and the concrete gaps that must be
addressed before any public v2.0 performance claim.

---

## Q1 — Is the Timing Comparison Same-Contract and Parity-Gated?

**Yes, with one structural note.**

Both paths emit the same app row contract: `{"segment_id": int, "polygon_id": int}`.

- v1.8 path: `rt.segment_polygon_anyhit_rows_native_bounded_optix(segments, polygons, output_capacity=...)`
- v2.0 path: `rt.segment_polygon_anyhit_rows_optix_partner_columns(ray_columns, triangle_columns, triangle_aabbs, partner=..., output_capacity=...)`

Parity is enforced before any timing result is emitted: if
`_canonical_rows(v18_rows) != expected_canonical` or
`_canonical_rows(rows) != expected_canonical`, a `RuntimeError` is raised
and the script exits without producing an artifact. The artifact's
`"strict_rows_match": true` is therefore a live runtime assertion, not a
post-hoc annotation.

**Structural note:** The test geometry is constructed as 512 non-overlapping
1:1 segment-polygon pairs, so each segment hits exactly one polygon by
construction. Parity success is structurally guaranteed by the dataset
design. This is appropriate for a timing harness, but the parity gate is
not stress-tested here — correctness under overlapping geometries and
multi-hit cases is delegated to earlier goals (Goal1848, Goal1850).

---

## Q2 — Is Canonical Row-Set Parity the Right Comparison?

**Yes. This is the correct choice.**

`_canonical_rows` returns `tuple(sorted((int(row["segment_id"]), int(row["polygon_id"])) for row in rows))`.

Sorting before comparison correctly abstracts over traversal order, which
is not a public semantic. The adapter implementation in
`partner_adapters.py:275-277` independently applies
`sorted(set(zip(ray_ids, primitive_ids)))` when emitting rows, so the
app-level contract is already defined as an order-independent set. The
parity comparison and the row-emission contract are consistent.

No objection to this choice.

---

## Q3 — Does the Artifact Support Only the Narrow Claim in the Report?

**Yes.**

The artifact's `claim_boundary` block is:

```json
{
  "broad_rt_core_speedup_claim_authorized": false,
  "package_install_claim_authorized": false,
  "same_contract_timing_row": true,
  "v2_0_release_authorized": false,
  "whole_app_speedup_claim_authorized": false
}
```

The report's "Status: pass-with-boundary" is consistent with the artifact's
`"status": "pass"` (which refers to the harness run, not a release gate).
The report explicitly states "not an all-app performance table and does not
authorize v2.0 release wording." No overclaim is present.

The observed timing ratios (0.60x CuPy, 0.62x Torch vs v1.8 median query)
are stated without generalization. Column-build times are reported in a
separate section with the correct explanation that in the intended v2.0
shape, callers may pre-own those tensors.

---

## Q4 — Are the Release/Speedup Boundaries Correct?

**Yes. All four blocked boundaries are correctly set.**

| Boundary | Artifact | Report | Runner code |
|---|---|---|---|
| `v2_0_release_authorized` | `false` | stated blocked | `False` literal |
| `whole_app_speedup_claim_authorized` | `false` | stated blocked | `False` literal |
| `broad_rt_core_speedup_claim_authorized` | `false` | stated blocked | `False` literal |
| `package_install_claim_authorized` | `false` | stated blocked | `False` literal |

The runner test (`goal1856_segment_polygon_v2_partner_perf_runner_test.py`)
mechanically asserts all four `False` literals are present in the script
source as text and asserts them as `false` in the parsed artifact. The
double-check across code, artifact JSON, and test is the right structure
for a claim boundary that must not regress.

---

## Q5 — What Must Be Improved Before a Public v2.0 Performance Claim?

The following gaps block promotion to a public-facing performance claim.
They are listed in descending priority.

### 5.1 Column-Build Amortization Is Not Characterized

The `query_median_ratio_vs_v1_8_native` metric (0.60x/0.62x) measures only
the query phase. Including the column-build phase inverts the comparison:

- CuPy end-to-end (build + median query): ~0.00429 + 0.00107 ≈ 0.0054 s
- v1.8 native median query: ~0.00178 s
- Ratio: ~3.0x **slower** end-to-end for a single call

The query-phase speedup is real only when column build is amortized across
multiple queries. A public claim must state the breakeven query count and
must show that the caller's workload typically crosses that threshold. The
report acknowledges this but does not quantify it. A follow-on goal should
compute breakeven and show a workload model that justifies the assumption.

### 5.2 Sample Count Is Insufficient for Variance Claims

With 5 iterations and a large warm-up outlier on iteration 1, the
steady-state median is drawn from 4 samples (iterations 2–5). Run-to-run
variance in those 4 samples is:

- v1.8 steady range: 0.001758–0.002035 s (±8%)
- CuPy steady range: 0.001042–0.001351 s (±15%)
- Torch steady range: 0.001017–0.001191 s (±8%)

These are not alarming for an internal harness, but they are too wide for
a public performance claim without confidence intervals. A minimum of 20
warm steady-state iterations is recommended before reporting a public median
ratio.

### 5.3 Dataset Scale Does Not Represent Production Workloads

512 segments × 512 polygons (1:1 non-overlapping) is a micro-benchmark.
Real GIS queries typically have M×N non-trivial intersection tests with
variable hit rates, polygon complexity, and spatial clustering. The timing
ratio at 512 rows may not hold at 10K, 100K, or 1M row inputs, or when
polygons have many vertices requiring multiple triangles per polygon.
Scale sweep across at least 3 orders of magnitude of input size is required.

### 5.4 Only One App Path Measured

`segment_polygon_anyhit_rows` is one app path. A public v2.0 performance
claim requires coverage of the full app surface exposed at v2.0. The
remaining paths must each have their own same-contract timing row before
any aggregate performance statement is made.

### 5.5 Single GPU, Single Pod

All data comes from one RTX A4500 pod (driver 550.127.05). A public claim
requires data from at least one additional GPU class (e.g., consumer Ampere
or Ada, data-center Ampere) to verify that the ratio is not specific to
the A4500's RT-core balance.

### 5.6 Synthetic Geometry Does Not Stress the Parity Gate

As noted in Q1, the 1:1 non-overlapping construction makes parity trivially
satisfied. Before a public claim, the parity gate should be exercised with
genuinely overlapping queries (multiple polygon hits per segment) to confirm
that duplicate removal and canonical comparison hold under real-world conditions.

### 5.7 No Overflow Boundary Test

The harness uses `output_capacity = count * 2`, giving 2× headroom for a
dataset that produces exactly `count` hits. Overflow handling
(`metadata["overflowed"]` → `RuntimeError`) exists in the adapter but is not
exercised by this harness. A public claim should include a tight-capacity run
that verifies the overflow guard fires correctly rather than silently truncating
results.

---

## Implementation Observations (Non-Blocking)

**Positive:**

- The `_build_partner_columns` function in the runner script correctly
  excludes column-build time from the `_time_call` loop, recording it
  separately as `column_build_s`. This is the right accounting.
- The `runtime["sync"]()` call after column construction correctly ensures
  GPU-side tensor allocation is complete before the timing loop begins.
- `_canonical_rows` is a pure sort — no deduplication — which is correct
  given the 1:1 geometry. The adapter itself does the deduplication via
  `set(zip(...))` before emitting rows.
- The artifact records `git_commit` and `gpu` fields, enabling exact
  reproduction. The commit `bd8409b8` matches the report's stated pod
  reset commit.

**Minor observations (not defects):**

- The perf script builds `expected_rows` via `zip(segments, polygons)` and
  then applies `_canonical_rows` to it. Since `_canonical_rows` sorts, the
  construction order of `expected_rows` is irrelevant — this is correct.
- Torch warm-up on iteration 1 (0.011 s) is much smaller than v1.8 warm-up
  (0.622 s). This is plausible if CUDA context was already warm from the
  Torch column-build phase, while v1.8 native OptiX may cold-initialize on
  its first call. The asymmetric warm-up does not affect the steady-state
  median but should be noted when comparing first-call latency.

---

## Verdict

`accept-with-boundary`

The Goal1856 harness, runner test, report, and artifact are internally
consistent, correctly structured, and do not overclaim. The narrow
same-contract timing row for `segment_polygon_anyhit_rows` is accepted as
an engineering data point.

The following remain **blocked** by this review:

- v2.0 release authorization
- Any whole-app speedup claim
- Any broad RT-core speedup claim
- Any package-install claim
- Any public performance claim based solely on this data point

Promotion to a public v2.0 performance claim requires resolution of the
five items in §5 above, with §5.1 (column-build amortization) and §5.3
(scale sweep) as the highest priority gaps.
