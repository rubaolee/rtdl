---

# Phoenix V3 M42 Grouped-Reduction Grid Occupancy Root Cause — External Review

**Date:** 2026-06-23  
**Verdict:** `accept_m42_shape_positive_require_tiled_kernel`

---

## Verdict Rationale

The M42 evidence is genuine Step-2 evidence for a specific shape region. The root-cause diagnosis is correct, the instrumentation is technically sound, and the experiment is properly controlled. However, the current offsets kernel architecture makes the family useful only for high-group-count/low-rows-per-group shapes. Accepting M42 as a full family closure with only a shape envelope would leave the standard production shape pattern (moderate group_count, many rows/group) permanently disadvantaged with no GPU acceleration path. A single bounded tiled/row-parallel kernel implementation is required before the family can be declared Step-2 complete.

---

## Findings by Severity

### HIGH — Blocking for Full Family Closure

**H1 — Kernel is single-threaded per group; standard shapes are unserviceable.**  
`_numba_grouped_vector_sum_f64x2_offsets_kernel` (`numba_partner_continuation.py:1496–1513`) assigns one CUDA thread per group and runs a serial inner loop over that group's rows. Launch shape is `grid = ceil(group_count / block_size)`, block_size=256. At group_count=1024 (a completely normal production shape), this yields 4 CUDA blocks — essentially single-SM execution on any modern GPU. A production workload with 1000 groups and 1M rows would run worse than CPU. The M42 experiment avoids this by selecting a shape (65536 groups × 4 rows/group mean) that saturates block count while minimizing per-group work. This is a valid hypothesis test but not a general solution. A row-parallel block-cooperative kernel (each thread block reduces one group's rows cooperatively) is needed for the family to be generally useful. This work is scoped and local; it does not require POD.

### MEDIUM — Non-Blocking, Track Before Envelope Finalization

**M1 — M42 shape is at an unusual extreme of the envelope.**  
262144 rows / 65536 groups = 4.0 rows/group mean. This is near the degenerate end of grouped reduction (almost no aggregation per group). The 6.44× CPU-hot advantage at this shape is partly explained by the CPU path (`np.add.reduceat`) having to touch every row while the CUDA path dispatches 65536 independent threads with negligible serial work each. A second anchor point at group_count=4096 (64 blocks, ~64 rows/group) would establish that the benefit holds for non-degenerate shapes before the envelope is formalized. Not required before the tiled kernel is pursued, but required before any envelope-scoped claim.

**M2 — allclose tolerances not explicitly tied to accumulation-order proof.**  
`all_variant_vector_sum_signatures_hash_match` was not reported in the summary excerpt, only `allclose=true`. With rows_per_group_mean=4.0, floating-point accumulation differences between NumPy reduceat and the CUDA serial loop should be negligible, so allclose at atol=1e-6 is almost certainly correct. This is a documentation gap, not a correctness concern.

### LOW — Cosmetic / Minor

**L1 — Harness script name (m41) does not match evidence milestone (m42).**  
`scripts/v3_phoenix_grouped_reduction_m41_local_harness.py` was reused for M42. The output directory is correctly labeled `m42_lx1_shape_262144x65536`. This creates a script-version/evidence-version mismatch. The harness itself is correct; the name is an artifact of reuse without rename. Future reviewers checking the harness script name against the evidence directory will need to resolve this discrepancy.

**L2 — `v2_5_numba_rows_per_group_mean` is computed in the adapter, not read from the kernel.**  
`partner_adapters.py:2514–2518` divides `numba_result.get("row_count", 0)` by `numba_result.get("group_count", 1)`. The kernel result does carry both values (via `extra_metadata` in `run_numba_prepared_grouped_vector_sum_f64x2_by_offsets`), so this is correct. The division-by-zero guard is present. Not a defect.

---

## Seven Review Questions

**Q1. Is the root-cause diagnosis correct: the current offsets kernel parallelizes over `group_count`, so the M41 1024-group shape launched only 4 blocks?**

Yes. Source-confirmed. `_numba_grouped_vector_sum_f64x2_offsets_kernel` (line 1499): `group = cuda.grid(1)`. The launch at line 475: `grid = ((group_count + block_size - 1) // block_size,)`. With group_count=1024, block_size=256: grid=(4,). The inner serial loop (lines 1503–1509) runs entirely within one thread per group. The diagnosis is correct.

**Q2. Is the correction to earlier speculative shapes correct: increasing `row_count` at fixed `group_count=1024` would not improve occupancy, and reducing `group_count` to 64 would worsen it?**

Yes, both corrections are correct. (a) Increasing row_count at fixed group_count=1024 would leave grid=(4,) unchanged — it only makes the serial loop longer per thread, not more parallel. (b) Reducing group_count to 64 gives grid=ceil(64/256)=1 block — strictly worse. The implied corrective action (increase group_count) is the only path to better occupancy with this kernel design.

**Q3. Does the M42 free-local shape experiment (`262144` rows, `65536` groups) validly test the launch-shape hypothesis?**

Yes, within the shape tested. Controls are sound: all three variants (CPU control, legacy one-shot, productized runner) used the same data generated once per process; `generic_grouped_reduction_contract=true`; `app_specific_route_logic_allowed=false`; warmup=2; repeat=5; failed_check_count=0; allclose=true. The experiment cleanly demonstrates that increasing group_count from 1024 to 65536 shifts program_count from 4 to 256, and the runner outperforms CPU hot by 6.44× at this shape. The hypothesis is validated for this specific shape class.

**Q4. Does the M42 result close grouped reduction as a shape-positive second Step-2 family, or should it be treated only as a prompt to build a tiled/row-parallel generic kernel?**

It should be treated as a prompt to build a tiled kernel, not as family closure. The result is genuinely shape-positive — the productized runtime trunk works for high-group-count inputs — but the shape constraint is binding in most production scenarios. Standard grouped reduction workloads (hundreds to a few thousand groups, many rows each) will remain CPU-slower with the current kernel. Accepting M42 as full family closure without a tiled kernel would require documenting a shape envelope that excludes typical usage, which undermines the value of the family.

**Q5. Are the new launch-shape metadata fields sufficient and placed in the right layer?**

Yes. The five fields are correctly layered:
- `program_count` and `threads_per_block` originate in `run_numba_prepared_grouped_vector_sum_f64x2_by_offsets` (kernel layer, lines 601–602 in the truncated portion), reported in the Numba result.
- `v2_5_numba_offset_program_count`, `v2_5_numba_threads_per_block`, `v2_5_numba_launch_parallelism_axis`, `v2_5_numba_rows_per_group_mean` are surfaced in `run_grouped_vector_sum_2d_partner_columns_session` (adapter layer, `partner_adapters.py:2511–2518`) and propagated up.
- `grouped_reduction_launch_shape` is assembled as an interpretable summary in `run_grouped_vector_sum_2d_prepared_session` (`prepared_execution.py:2566–2573`) — the correct layer for cross-field summaries.
- `launch_parallelism_axis` hardcoded to `"group_count"` is accurate for this kernel and appropriate (it is a fixed property of the offsets kernel design, not a runtime-variable).

No concerns about layer placement.

**Q6. Does any wording overclaim performance, release readiness, all-app readiness, paid-POD authorization, V4, embedding, or true zero-copy?**

No overclaiming found. Every authorization field in the summary, variant payloads, and claim_boundary block is false. The status string `m42_root_cause_identified_shape_positive_not_release` is accurate. The speedup figures (6.44× CPU-hot, 18.71× legacy-hot) are scoped as internal harness comparisons, not external speedup claims. The non-authorization block in the report explicitly enumerates all forbidden claims.

**Q7. What exact next step should be authorized: external-review-only closure, one local tiled-kernel implementation, one additional free local envelope run, or family switch?**

**Authorized next step: one local tiled/row-parallel kernel implementation.**  
Specifically: replace `_numba_grouped_vector_sum_f64x2_offsets_kernel` with a block-cooperative variant where each CUDA thread block is assigned one group and all threads within the block collaboratively reduce that group's rows using shared memory. This eliminates the grid-occupancy dependency on group_count and enables the family to serve low-group-count / high-rows-per-group shapes. The work is:
- local only (no paid POD)
- scoped to one new kernel and its harness integration
- reviewable with the existing M42 harness infrastructure at multiple shapes (e.g., 262144×1024, 262144×4096, 262144×65536)
- does not authorize release, all-app, or any claim listed in the non-authorization block below

An additional free-local envelope run alone (without the kernel fix) would only add shape samples; it would not resolve the underlying occupancy-vs-group-count coupling.

---

## Explicit Non-Authorization Block

This review does not authorize, and explicitly preserves the prohibition on:

- **No V3 release** — no release authorization of any kind
- **No all-app run** — no authorization to run any app benchmark suite with this evidence
- **No paid POD spend** — paid POD remains blocked pending a separate request after tiled kernel implementation and local evidence review
- **No public speedup wording** — the 6.44× and 18.71× figures are internal harness comparisons only; they are not authorized for any external, partner-facing, or marketing context
- **No broad V3-over-V2 claim** — no claim that V3 is faster than V2 in any general or broad sense
- **No V4 work** — this review does not authorize any V4, embedding, C ABI, or external device buffer interop work
- **No embedding** — not authorized
- **No C ABI** — not authorized
- **No true zero-copy claim** — `internal_device_residency_between_rtdl_phases=true` in the evidence refers to RTDL-owned intermediates between RTDL phases; it does not constitute true zero-copy and must not be described as such
