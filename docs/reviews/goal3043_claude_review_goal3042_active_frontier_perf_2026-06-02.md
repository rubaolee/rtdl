# Goal3043 — Claude Review: Goal3042 Active-Frontier Hausdorff Performance

**Reviewer:** Claude Sonnet 4.6 (independent, read-only)
**Date:** 2026-06-02
**Subject commit:** `c10301b7` / source commit `f0b42a18`
**Verdict:** `accept-with-boundary`

---

## Files Inspected

- `src/native/optix/rtdl_optix_core.cpp` (kernel source, lines 6148–6373)
- `src/native/optix/rtdl_optix_workloads.cpp` (host dispatch, lines 14024–14175)
- `src/native/optix/rtdl_optix_api.cpp` (C extern, lines 4983–4999)
- `src/native/optix/rtdl_optix_prelude.h` (declaration, lines 1520–1528)
- `src/rtdsl/optix_runtime.py` (ctypes binding and Python contract)
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
  (active frontier helper, lines 624–711; `_reduce_nearest_max_distance_row`, lines 327–355)
- `docs/reports/goal3042_point_group_active_frontier_witness_selection_2026-06-02.md`
- `docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json`
- `tests/goal3042_point_group_active_frontier_witness_selection_test.py`
- `src/rtdsl/v2_6_roadmap.py`

---

## Review Questions

### Q1 — App-agnostic native-engine boundary

**Finding: Clean. No violations observed.**

The exported C symbol is:

```
rtdl_optix_reduce_prepared_point_group_nearest_max_distance_active_frontier_2d
```

All six tokens in the name are generic: `point_group`, `nearest`, `max_distance`,
`active_frontier`, `2d`. The ABI carries: `prepared handle`, `query_points`,
`query_count`, `threshold_radius`, `threshold`, `witness_radius`, `row_out`,
`active_count_out`. No Hausdorff/X-HD/application semantics appear in the native
signature.

The kernel source (`rtdl_optix_core.cpp`) contains no Hausdorff, X-HD, or XHD
text. The test at `test_native_export_is_generic_and_filters_rows_on_device` checks
this programmatically and would fail on any case-insensitive match. The internal
workload function name is
`reduce_prepared_point_group_nearest_max_distance_active_frontier_2d_optix` — fully
generic.

The Hausdorff-specific orchestration lives entirely in Python
(`_directed_rt_grouped_active_frontier_nearest_witness`). That function calls the
generic `nearest_max_distance_active_frontier_row` method on
`PreparedOptixPointGroupNearestWitness2D` and post-processes the result in Python.
The native engine does not know it is serving a Hausdorff computation.

The boundary is clean.

---

### Q2 — Exactness and the witness-index fix

**Finding: Correct under the stated contract. The ID-based mapping is sound.**

**Kernel ID semantics.** The nearest anyhit shader (`__anyhit__point_group_nearest_anyhit`,
`rtdl_optix_core.cpp:6290`) stores `t.id` as the `neighbor_id` in the output record.
`t.id` is the original point ID embedded in the `GpuPoint` struct when the search
points are packed from `sorted_target_columns["ids"]`, which in turn is drawn
directly from the original `target_columns["ids"]` array (re-sorted but not re-IDed
by `_build_uniform_point_group_columns`, line 142: `columns["ids"][order]`). The
kernel therefore carries original point IDs across the sort.

**ID-to-index mapping in Python.** `_reduce_nearest_max_distance_row`
(function.py:327) looks up `neighbor_id` in `target_columns["ids"]` — the original
unsorted array — via `np.nonzero`. This correctly returns the original array position
of the target point, independent of whatever sort order the BVH used internally.
Both call sites in the active frontier helper (line 665 for the seed reduction, line
680 for the frontier reduction) correctly pass `target_columns`, not
`sorted_target_columns`.

**Inactive record handling.** Queries flagged as threshold-satisfied are written as
`{q.id, 0xFFFFFFFFu, -1.0f}` by the nearest raygen shader
(`rtdl_optix_core.cpp:6255`). The reduce kernel skips these records at
`neighbor_id == 0xFFFFFFFF && distance < 0.0` (lines 6349–6351). Records where
no witness was found within `witness_radius` but the query was active appear as
`{q.id, 0xFFFFFFFFu, FLT_MAX}`; these are converted to `INFINITY` by the reduce
kernel (line 6353) and subsequently trapped by the `math.isfinite` guard in
`_reduce_nearest_max_distance_row`. The sentinel path is correct and produces a
descriptive `RuntimeError` rather than a silent wrong answer.

**Active-count atomics.** The nearest raygen increments `params.active_query_count`
via `atomicAdd` only for queries that pass the active-flag gate. Two sequential
`optixLaunch` calls on stream 0 are serialized; the threshold flags are fully
written before the nearest pass reads them. This is correct.

**Pod evidence.** `runtime_smoke_matched_openmp_witness: true` and all 6 rows
reporting `all_methods_match_exact_reference: true` (distance tolerance check) plus
`all_methods_ok: true` are consistent with the analysis above.

One pre-existing inconsistency observed (not introduced by Goal3042): the older
`_directed_rt_grouped_reduced_nearest_witness` function (function.py:528) calls
`_reduce_nearest_max_distance_row(source_columns, sorted_target_columns, row)`
where Goal3042's active frontier correctly uses `target_columns`. This means the
older path returns `target_index` in sorted order rather than original order. It is
not caught by the distance-only `matches_exact_reference` check. This is a
pre-existing bug in a predecessor function; Goal3042 does not introduce it and the
active frontier path is correct.

---

### Q3 — Artifact timings and speedup ratio arithmetic

**Finding: All six rows independently verified. Arithmetic is correct.**

The speedup convention used is `cupy_sec / active_frontier_sec`. Independent
verification against the JSON values:

| Points | cupy_sec (JSON) | af_sec (JSON) | Computed speedup | Reported |
| ---: | ---: | ---: | ---: | ---: |
| 4096 | 0.004776467802 | 0.006584460847 | 0.7254x | 0.725x ✓ |
| 8192 | 0.008929982781 | 0.011395583861 | 0.7836x | 0.784x ✓ |
| 16384 | 0.032289380906 | 0.020904737059 | 1.5446x | 1.545x ✓ |
| 32768 | 0.079344463767 | 0.038273931947 | 2.0731x | 2.073x ✓ |
| 65536 | 0.300481389044 | 0.078558421927 | 3.8249x | 3.825x ✓ |
| 131072 | 1.101468300913 | 0.168522496941 | 6.5360x | 6.536x ✓ |

The JSON `active_speedup_vs_cupy` field agrees with each computed value to four
significant figures. The `active_vs_cupy_ratio` field correctly records the inverse
(elapsed ratio, not speedup). The `best_active_speedup_vs_cupy: 6.53603...` in the
top-level JSON is the 131072-row value, consistent with the per-row data.

The crossover point (AF slower at 4096/8192, faster at 16384+) is correctly
documented in the JSON `crossover_points` field and in the report table.

The reduce kernel uses a single 256-thread block with a stride loop. For N=131072
this means each thread processes 512 records before the shared-memory tree
reduction. This is functionally correct; the single-block pattern is adequate here
because the result is one record per traversal, not a large output, and the
performance evidence confirms it is not a bottleneck in practice.

---

### Q4 — Is "bounded internal positive A4000 evidence" a fair characterization?

**Finding: Yes, with the caveats the report already states.**

The report documents:

- A clear monotonic crossover: AF is slower at small sizes (GPU overhead dominates)
  and progressively faster at larger sizes (frontier pruning compounds).
- Correctness validation: all 6 sizes match the exact reference method and OpenMP.
- Explicit `false` on `v2_6_release_authorized`, `public_speedup_claim_authorized`,
  `rt_core_speedup_claim_authorized`, `true_zero_copy_claim_authorized`, and
  `whole_app_speedup_claim_authorized`.
- The "not true-zero-copy" note is accurate: query points are still packed on the
  host before upload; only the threshold-derived active mask stays device-resident.

The characterization is fair. The evidence is positive (6.5x at 131K on this
specific benchmark) and bounded (one GPU, one run per size, dense synthetic data,
specific seed parameters). It is appropriate to record it as internal v2.6 evidence
requiring external review before any public use.

---

### Q5 — Residual risks and next engineering steps before any public claim

**1. Single-run wall-clock timing.**
Each size is a single elapsed measurement. There are no multi-trial averages,
no confidence intervals, and no warm-up / cold-start isolation. At 4096 and 8192
points the margin between CuPy and AF is narrow enough that run-to-run noise could
shift the crossover. Multi-trial timing with median and inter-quartile range is
needed before any crossover claim is published.

**2. Single GPU, single architecture.**
All evidence is from an NVIDIA RTX A4000 (Ampere). The active frontier pattern
(two sequential OptiX launches plus one CUDA kernel reduction per call) has
different overhead profiles on Ada, Turing, and Hopper. No L4, A10, or consumer
GPU data exists. Second-GPU validation is required before a general "RT-core
Hausdorff acceleration" claim.

**3. Dense synthetic data only.**
`make_demo_points` produces uniform random 2-D point sets. The active frontier
efficiency depends on the fraction of source points pruned by the seed threshold.
Sparse, clustered, or adversarially structured point sets may yield lower pruning
rates or degenerate seed samples. The method has no documented behavior bounds for
non-uniform distributions.

**4. Seed sample reliability at large scale.**
The seed sample is fixed at 1024 points. At 131072-point sets this is a 0.78%
sample. For highly non-uniform distributions, the 1024-point seed may fail to
sample the true max-witness source point, establishing a threshold radius that
incorrectly prunes it. The correctness guard (if `active_count == 0`, fall back to
seed result; if not, take the max of seed and frontier) is correct only when the
seed result is still a valid lower bound on the Hausdorff distance. For adversarial
inputs this invariant may break silently unless validated. For the tested uniform
random seeds the correctness holds, but this should be tested explicitly on
near-degenerate or structured inputs before promotion.

**5. Pre-existing target-index inconsistency in `_directed_rt_grouped_reduced_nearest_witness`.**
As noted in Q2, this predecessor function passes `sorted_target_columns` to
`_reduce_nearest_max_distance_row`, which yields a sort-order target index rather
than the original-input target index. Since `matches_exact_reference` only checks
distance, this is not caught. Goal3042 does not introduce this bug and the active
frontier path is correct, but the inconsistency should be fixed before any function
that depends on the returned `target_index` from the seeded-pruned path is used in
a non-benchmark context.

**6. No guard against witness_radius being an invalid upper bound.**
If `witness_radius` is not a valid upper bound for all source points in the active
set, some active queries will have no witness within `witness_radius`. The kernel
writes `{q.id, 0xFFFFFFFF, FLT_MAX}` for these; the reduce kernel promotes them to
INFINITY; and the Python layer raises a `RuntimeError`. This is the correct
defensive behavior, but it means callers must ensure `witness_radius` is a true
upper bound. The current Hausdorff wiring computes this from `_point_set_upper_bound`
which is sound. Any future caller that passes a non-conservative radius would get a
runtime exception rather than a silent wrong answer, which is the right failure mode.

**Summary of next steps before any public claim:**
- Multi-trial timing (≥10 runs, median + IQR) for crossover confirmation
- Second GPU validation (at minimum one non-A4000 Ampere or one Ada)
- Non-uniform / structured point-set correctness tests for the seed heuristic
- Fix the pre-existing `sorted_target_columns` / `target_columns` inconsistency in
  `_directed_rt_grouped_reduced_nearest_witness`
- Consider increasing seed sample count adaptively for point sets above 64K

---

## Summary

Goal3042 delivers a correct, well-bounded generic primitive. The native boundary is
clean. The ID-based witness mapping is sound and the sorting does not corrupt
indices. The timing arithmetic is independently verified. The claim language
correctly refuses all public/release/true-zero-copy assertions and the v2.6 roadmap
enforces this at test time.

The accept-with-boundary verdict reflects that the work is ready to be indexed as
internal positive evidence, but the residual items in Q5 — particularly multi-trial
timing, second-GPU confirmation, and non-uniform data testing — must be addressed
before any external or public performance claim is made.

**Verdict: `accept-with-boundary`**
