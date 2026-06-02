# Independent Claude Review: Goals 3036–3040 — Numba Hausdorff Device-Column Argmax Chain

**Review date:** 2026-06-02
**Reviewer:** Claude (independent review, distinct from Codex and Gemini reviews)
**Verdict:** `accept`
**Scope:** Goals 3036, 3037, 3039, 3040
**Note:** This review does not constitute final release consensus and cannot authorize v2.6 release by itself.

---

## Files Inspected

- `src/rtdsl/numba_partner_continuation.py`
- `src/rtdsl/partner_adapters.py` (grep search; file exceeds read limit)
- `examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`
- `src/rtdsl/v2_6_roadmap.py`
- `docs/reports/goal3036_numba_global_argmax_block_reduce_hardening_2026-06-02.md`
- `docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.md`
- `docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.json`
- `docs/reports/goal3039_hausdorff_device_columns_numba_argmax_strategy_2026-06-02.md`
- `docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.md`
- `docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.json`
- `tests/goal3036_numba_global_argmax_block_reduce_hardening_test.py`
- `tests/goal3037_point_group_nearest_numba_argmax_a4000_pod_test.py`
- `tests/goal3039_hausdorff_device_columns_numba_argmax_strategy_test.py`
- `tests/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_test.py`

No tests were executed locally (no CUDA device available in this environment). Evidence is grounded in code inspection and the clean-source pod artifacts.

---

## Question 1: Does Goal3036 correctly replace global atomics with block-reduce?

**Finding: Yes.**

`run_numba_global_argmax_u32_f64` (`numba_partner_continuation.py:358–453`) implements a two-kernel multi-stage reduction:

1. `_numba_global_argmax_initial_block_reduce_u32_f64_kernel` (lines 971–1033): each block reduces its input slice into one summary row using 256-element shared memory arrays (`shared_scores`, `shared_item_ids`, `shared_row_indices`, `shared_valid_counts`). The stride-halving loop operates over `blockDim.x // 2` and converges to `thread 0` without any `cuda.atomic.*` calls.

2. `_numba_global_argmax_block_reduce_u32_f64_kernel` (lines 1037–1100): the caller iterates until `current_count == 1`, reducing the previous block summaries in the same shared-memory pattern.

The tie-break (`highest_score_then_lowest_item_id_then_lowest_row_index`) is applied correctly inside both kernels at lines 1013–1023 and 1079–1089. No global atomic ops appear in either argmax kernel. The old kernel names (`_numba_global_argmax_score_u32_f64_kernel`, `_numba_global_argmax_item_u32_f64_kernel`, `_numba_global_argmax_row_u32_f64_kernel`) are absent from the file, confirming full replacement.

**Soundness note on shared array sizing:** Shared arrays are fixed at 256 elements. The block size cap (`if block_size > 256: raise ValueError`, line 379) keeps this safe. For block sizes smaller than 256, the stride starts at `blockDim.x // 2`, so indices above `blockDim.x - 1` in the shared arrays are never accessed.

**One mid-chain host sync acknowledged but unlabeled:** After the initial block reduce, `valid_total` is computed by copying `current_valid_counts` to host (lines 402–404). This is a scalar check, not row materialization, and is correctly not labeled as host row materialization. However, it does introduce a device-to-host transfer on the argmax critical path that is invisible in the metadata. This is a correctness check for the empty-input guard, not a structural flaw, but it means `host_row_materialization_used: False` in the metadata describes the output side only.

**Dirty-overlay qualification:** Goal3036 explicitly states the validation was on a dirty overlay (not a clean commit). The report correctly names this limitation and defers clean-source proof to Goal3037.

**Conclusion:** The hardening is correct and complete for its stated scope.

---

## Question 2: Does Goal3037 provide valid clean-source A4000 evidence for the composed path?

**Finding: Yes.**

The JSON artifact (`goal3037_...json`) records:
- `source_commit: "5aebe6e5a80aa8b6783e98bf66a84ec8a58cd468"`
- `source_dirty: []`
- GPU: `NVIDIA RTX A4000, 580.159.03`
- Library rebuilt from clean source via `make build-optix`
- 9 tests passed in 1.118s

All 7 exact-match checks are `true`:
- `query_ids_match_raw_rows`
- `neighbor_ids_match_raw_rows`
- `distances_match_raw_rows`
- `argmax_item_matches_raw_rows`
- `argmax_row_matches_raw_rows`
- `argmax_score_matches_raw_rows`
- `argmax_neighbor_matches_raw_rows`

The expected and actual argmax rows are identical:
```json
{ "query_id": 1344, "neighbor_id": 5492, "distance": 0.02454645186662674, "row_index": 1344 }
```

The producer used `rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_columns` with `native_execution_path=prepared_rt_core_point_group_nearest_witness_2d_device_columns`, confirming the RT-core traversal path. `producer_materializes_neighbor_rows=false` confirms no host row materialization on the output side.

The consumer used `global_argmax_u32_f64` with `reduction_strategy=multi_stage_block_reduce_no_global_atomics`. `consumer_neutral_handoff_status=accept` and `consumer_source_protocols=["cupy", "cupy"]` confirm the CuPy-to-Numba device handoff is working.

**Claim boundary fields all correct:** `v2_6_release_authorized=false`, `true_zero_copy_claim_authorized=false`, `rt_core_speedup_claim_authorized=false`.

The `producer_output_columns_true_zero_copy_authorized=true` is a narrower claim than the global `true_zero_copy_claim_authorized=false`, and the distinction is maintained consistently: the output device columns have no host materialization, but the full pipeline is not true-zero-copy because query points still travel through host-side preparation.

**Conclusion:** Valid clean-source A4000 evidence. The composition is proven with exact parity against the raw row-view oracle.

---

## Question 3: Does Goal3039 wire the composition as app-level Python only, without native engine changes?

**Finding: Yes.**

The directed helper `_directed_rt_grouped_device_columns_numba_argmax_nearest_witness` (`rtdl_hausdorff_v2_function.py:925–1000`) contains only Python strategy code:

1. Packs source points and target group columns using `_pack_point_columns_for_optix` and `_build_uniform_point_group_columns` — same helpers used by all other strategies.
2. Calls `prepared.write_device_nearest_witness_columns(...)` — a generic producer that knows nothing about Hausdorff distance.
3. Calls `rt.global_argmax_u32_f64_partner_columns(...)` — a generic consumer that knows nothing about Hausdorff distance.
4. Copies only the selected scalar witness back to host to compute `_reduce_nearest_max_distance_row`.

The `host_row_materialization_used_on_new_path: False` flag (line 999) is set explicitly in the result, verifying that the intermediate `neighbor_ids` column is not materialized to host for the argmax reduction.

The test `test_strategy_is_app_level_not_native_engine_customization` (goal3039 test, lines 24–34) verifies that `rtdl_optix_run_hausdorff` does not appear in `optix_runtime.py` and that `hausdorff` does not appear in the `PreparedOptixPointGroupNearestWitness2D` class definition, confirming the engine remains app-agnostic.

The user-facing function `hausdorff_distance_2d_rt_grouped_device_columns_numba_argmax_nearest_witness` (lines 1431–1479) follows the same structural pattern as all other `hausdorff_distance_2d_rt_*` functions — it composes two directed calls and selects the max, without any Hausdorff-specific native ABI.

**Conclusion:** The wiring is correctly app-level only. No Hausdorff-specific behavior was added to the native engine.

---

## Question 4: Does Goal3040 correctly interpret the performance result as negative, not a speedup?

**Finding: Yes.**

The measured timing from the JSON artifact (`goal3040_...json`):

| Points/side | CuPy grouped-grid | Adaptive raw RT | Device columns + Numba argmax | Ratio vs CuPy |
|---:|---:|---:|---:|---:|
| 2,048 | 0.002541 s | 0.527363 s | 1.362789 s | 536x slower |
| 4,096 | 0.004778 s | 0.052364 s | 0.732571 s | 153x slower |
| 8,192 | 0.008906 s | 0.173520 s | 0.676493 s | 76x slower |

All distances match the CuPy grouped-grid exact Hausdorff value.

The report correctly labels this as "negative but useful performance result" and does not attempt to reframe it as a speedup or partial win. The all-boundary-flags-false block in the artifact (`public_speedup_claim_authorized: false`, `rt_core_speedup_claim_authorized: false`, `true_zero_copy_claim_authorized: false`, `v2_6_release_authorized: false`) is complete and consistent.

**Observation on 2048-point witness pair:** At 2048 points, the new path returns `target_index=622` while CuPy returns `target_index=462`, both at `distance=0.1389899208830002`. This is an expected tie-breaking difference: two distinct witness pairs achieve the same Hausdorff maximum distance. The test correctly only asserts `matches_cupy_grouped_grid_distance`, not witness-pair identity. This does not weaken the correctness claim.

**Ratio trend:** The ratio decreases from 536x to 76x as N grows (2048 → 8192), consistent with fixed launch overhead (Numba JIT, multi-stage kernel invocations, CuPy warm-up advantage) dominating at small N. This pattern supports the structural diagnosis.

**Conclusion:** The negative result is correctly labeled and the evidence is clean-source.

---

## Question 5: Is the proposed next direction technically justified?

**Finding: Yes.**

The report diagnoses the structural weakness correctly:

- The strategy emits one nearest-witness row per query point in each direction, then does a global argmax over the full column. This is O(N) work with no pruning.
- The Numba reducer launches multiple kernel passes over small N (e.g., for N=2048, initial block count = 8, then 1 — three total kernel dispatches for a trivially small problem).
- No X-HD-style active-set pruning is applied: points that already have a target within the current best distance are not removed from the RT query set before the traversal.

A device-resident active-set / candidate-frontier primitive would skip queries that cannot improve the directed Hausdorff maximum, reducing the RT work from O(N_source × N_target_groups) to O(K × N_target_groups) where K is the frontier size. This is the computational structure of X-HD's first and second stages. The RTDL threshold-flags primitive (`prepared.threshold_flags(...)`) already provides the necessary flag to exclude safe points; the missing piece is keeping the frontier selection and the witness output on-device across iterations.

The CuPy grouped-grid baseline completes in ~2–9 ms for these N values because it exploits the all-pairs structure in a single fused kernel with high occupancy. The RT path cannot match that for dense exact problems without a fundamentally different traversal strategy that avoids materializing all N witness rows.

**Conclusion:** The proposed direction (device-resident active set / candidate frontier with witness selection) is technically justified by the measured evidence.

---

## Question 6: Are claim boundaries intact?

**Finding: Yes, throughout the chain.**

Each goal explicitly blocks the same set of claims. The v2_6_roadmap.py `v2_6_roadmap()` function sets all 9 authorization flags to `False`:

```python
"release_authorized": False,
"public_speedup_claim_authorized": False,
"rt_core_speedup_claim_authorized": False,
"whole_app_speedup_claim_authorized": False,
"true_zero_copy_claim_authorized": False,
"automatic_partner_selection_allowed": False,
"automatic_triton_selection_allowed": False,
"numba_speedup_claim_authorized": False,
"app_specific_native_engine_logic_authorized": False,
```

The `validate_v2_6_roadmap` function enforces each of these programmatically and returns `status: "reject"` if any flag is not False. The roadmap status entries for Goals 3036–3040 each include `not_speedup_evidence`, `not_release`, or `negative_perf_result` qualifiers in their status strings.

The `true_zero_copy_claim_authorized=true` flag on `producer_output_columns` in Goal3037 is narrowly scoped to the output device column write path and does not propagate to the global claim. The global `true_zero_copy_claim_authorized=false` remains intact.

No test or report in the chain uses language that could be read as authorizing release, speedup, or automatic selection.

---

## Remaining Risks

1. **Numba toolchain fragility.** The working dependency boundary is narrow: `numba==0.61.2`, `cuda-python>=12,<13` (not `>=13`), `NUMBA_CUDA_USE_NVIDIA_BINDING=1`. The incompatibility between Numba 0.61's `cuda.cuda` namespace and the CUDA 13 `cuda.bindings` namespace (noted in Goal3036) is a deployment risk for the Numba continuation lane. This constraint is documented but is not enforced at the code level (no version checks in `_import_numba_stack`). Any pod upgrade to cuda-python>=13 would silently break the continuation path.

2. **A4000-specific evidence.** Goal3037's composition proof and Goal3040's performance measurement are both on the RTX A4000 (driver 580.159.03, CUDA 12.8). The L4 pod (CUDA 12.6) was used for earlier goals in the chain (Goal3000, Goal3003, Goal3007, Goal3013). The Goals 3036–3040 chain has only A4000 evidence. This is sufficient for the stated scope (A4000 pod validation) but does not generalize the claims to L4.

3. **Small-N Numba JIT overhead.** At 2048 points, the device-columns + Numba argmax path is 536x slower than CuPy. A significant fraction of this is likely JIT compilation cost (first-call penalty). The current benchmark does not distinguish cold vs. warm Numba timing. This does not affect the verdict (the result is labeled negative) but limits its interpretability as a steady-state performance measurement.

4. **Witness-pair tie-break difference at 2048 points.** As noted above, the new path returns a different `target_index` than CuPy at 2048 points, both achieving the same Hausdorff distance. This is expected behavior but is worth tracking: if downstream code consumes the witness index rather than just the distance, the difference could surface as a behavioral divergence.

---

## Verdict: `accept`

The four-goal chain (Goal3036 → Goal3037 → Goal3039 → Goal3040) is technically sound, correctly bounded, and honestly reported. Specifically:

- **Goal3036** correctly replaces fragile global atomics with multi-stage shared-memory block reduction. The dirty-overlay limitation is properly acknowledged.
- **Goal3037** provides clean-source RTX A4000 evidence that the OptiX producer + Numba argmax consumer composition is correct, with exact parity against the raw row-view oracle.
- **Goal3039** wires the composition as app-level Python only; no Hausdorff-specific behavior is added to the native engine.
- **Goal3040** correctly identifies and reports the result as a negative performance finding (75–536x slower than CuPy grouped-grid at the measured scales), with sound structural diagnosis of why the approach is slow and a technically justified next direction.

All claim boundaries are intact throughout. No release, public speedup, true-zero-copy, broad RT-core acceleration, or automatic partner-selection claim is authorized or implied by this chain.

This review is an independent Claude assessment and does not substitute for Codex or Gemini review, nor does it constitute release consensus on its own.
