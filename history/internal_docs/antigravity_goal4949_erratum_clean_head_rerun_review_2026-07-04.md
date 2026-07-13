# Review of Goal4949 Erratum: Clean-HEAD Rerun

- **Date:** 2026-07-04
- **Reviewer:** Antigravity (Advanced Agentic Coding Pair)
- **Verdict:** `approve_goal4949_erratum_clean_head_rerun`

---

## Verdict Summary

The erratum documented in [goal4949_erratum_clean_head_rerun_2026-07-04.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4949_erratum_clean_head_rerun_2026-07-04.md) is **approved** with the verdict **`approve_goal4949_erratum_clean_head_rerun`**.

The erratum correctly identifies that the initial Goal4949 measurement was contaminated by stale, un-tracked files in the remote POD directory left over from the experimental Goal4940 path-split adapter branch. It properly invalidates the stale timing metrics, presents clean measurements obtained from a verified local `HEAD` archive, and shifts the bottleneck explanation to the correct current-source metrics without altering the core engineering conclusions of Goal4949.

---

## Answers to Review Questions

### 1. Does the erratum correctly identify the stale POD directory as invalid evidence for current `HEAD`?
**Yes.**
The erratum correctly points out that the POD directory used for the first measurement (`/root/rtdl_goal4937`) was not a clean checkout of `HEAD` but a copied runtime directory. It contained stale experimental writer code containing path-splitting logic that had already been reverted at local `HEAD`. Because of this, the subphase measurements (like `path_split_materialize_map*_sec`) came from un-tracked, out-of-tree code and did not represent the state of the codebase at local `HEAD`. Disqualifying this evidence is correct and necessary for engineering rigor.

### 2. Does the clean rerun preserve correctness for both baseline and current Numba route?
**Yes.**
The clean rerun on the clean POD directory `/root/rtdl_goal4951_clean` confirms that both the baseline `section57_overlay.py` and current `section57_overlay_numba.py` preserve byte-for-byte correctness against the author's reference output:
- **Checksum (SHA256):** `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e`
- **Byte Equal:** `true` for both routes.

### 3. Does the clean rerun still justify saying the current Numba helper is not a performance win?
**Yes.**
Even with the clean rerun (which is faster than the stale run since it doesn't execute the slow path-splitting overhead), the Numba helper remains a performance regression compared to the baseline:
- **Total Elapsed:** `7.337s` (Numba) vs `6.917s` (Baseline) — a slowdown of `0.420s` (~6%).
- **Writer Phase:** `3.281s` (Numba) vs `2.093s` (Baseline) — a slowdown of `1.188s` (~57%).

Thus, the core conclusion that the current tracked Numba helper is not a performance win remains correct.

### 4. Does the erratum correctly supersede the stale `path_split_*` fields?
**Yes.**
The erratum explicitly disqualifies the four path-split subphase metrics:
- `path_split_materialize_map0_sec`
- `path_split_materialize_map1_sec`
- `path_split_format_map0_sec`
- `path_split_format_map1_sec`

It replaces them with the actual timing fields defined in the current tracked Numba helper code [section57_overlay_numba.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/Paper-reproduction-apps/rayjoin-paper/section57_overlay_numba.py#L101-L450):
- `skip_plan_sec`: `0.330s`
- `group_xsects_map0_sec`: `0.087s`
- `group_xsects_map1_sec`: `0.013s`
- `chain_loop_map0_sec`: `1.318s`
- `chain_loop_map1_sec`: `0.981s`
- `generic_output_assembly_sec`: `0.353s`
- `bulk_writelines_sec`: `0.079s`

These corrected subphase timings accurately reflect the current structure of the tracked code.

### 5. Is the corrected bottleneck interpretation consistent with Goal4930 / Goal4938 / Goal4940?
**Yes, entirely.**
- [Goal4930](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/antigravity_goal4930_result_v2_14_2_layer0_writer_phase_decomposition_review_2026-07-03.md) classified the bottleneck as `structure_assembly_dominant` (~2.0s baseline structural assembly).
- [Goal4938](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/antigravity_goal4938_layer3_boundary_relocation_review_2026-07-03.md) diagnosed that downstream materializers are "too late" to optimize performance because they run after the application has already paid the cost of the custom Python chain loops.
- [Goal4940](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/antigravity_goal4940_rayjoin_path_split_adapter_pod_gate_review_2026-07-04.md) reverted the experimental path-splitting adapter because executing path-split logic and row-buffer materialization in Python/NumPy-host code introduced a severe performance regression (~4.17s vs ~2.56s).

The corrected Numba helper timings align perfectly with this paradigm:
- The helper still runs the custom Python chain loops (`chain_loop_map0_sec` + `chain_loop_map1_sec` = `2.299s` total).
- It then incurs additional overhead from the generic output assembly layer (`generic_output_assembly_sec` = `0.353s`).
- Because it does not bypass the Python chain loops and instead adds generic assembly overhead on top, it is slower than the baseline writer (`3.281s` vs `2.093s`).

This confirms that the host-side structural chain/path assembly is the bottleneck and that wrapping it in the app layer cannot succeed.

### 6. Should Goal4949 remain closed, with the erratum attached, rather than being treated as a broad failure?
**Yes.**
The primary objective of Goal4949 was to determine whether the current Numba app-layer helper is a performance win on a real Section 5.7 County x Soil public sample. The high-level engineering conclusion (that the helper is a regression, prepared-hot PIP traversal is not the bottleneck, and future work must target reprojection/sorting or native Layer 3 path-split compiling) remains completely intact. The erratum is a documentation correction of the supporting subphase metrics. Attaching the erratum and keeping the goal closed is the correct lifecycle action.

---

## Comparison of Timing Data

| Metric / Phase | Stale POD Run (Goal4949) | Clean-HEAD Rerun (Erratum) | Timing Shift / Impact |
| :--- | :---: | :---: | :--- |
| **Baseline Elapsed** | `6.305s` (Hot rerun) | `6.917s` | Baseline runtime corrected. |
| **Numba Elapsed** | `8.034s` (Hot rerun) | `7.337s` | Numba helper runtime corrected. |
| **Slowdown Delta** | `+1.729s` | `+0.420s` | Slowdown is less severe than initially reported but still a clear regression. |
| **Baseline Writer** | `2.615s` (Hot rerun) | `2.093s` | Correct baseline writer time. |
| **Numba Writer** | `4.237s` (Hot rerun) | `3.281s` | Correct Numba helper writer time. |
| **Writer Subphases** | `path_split_materialize_map0` (`1.356s`) <br> `path_split_materialize_map1` (`1.039s`) <br> `path_split_format_map0` (`0.751s`) <br> `path_split_format_map1` (`0.610s`) | `skip_plan_sec` (`0.330s`) <br> `group_xsects_map0` (`0.087s`) <br> `group_xsects_map1` (`0.013s`) <br> `chain_loop_map0` (`1.318s`) <br> `chain_loop_map1` (`0.981s`) <br> `generic_output_assembly` (`0.353s`) | Timings correctly mapped to current-source loops and generic output assembly. |

---

## Conclusion & Action Items

1. **Verdict:** `approve_goal4949_erratum_clean_head_rerun` approved.
2. **Action Item:** Ensure that all future performance tracking points to `/root/rtdl_goal4951_clean` (or future clean-archive checkouts) as the authoritative environment, and strictly avoid reusing dirty/copied runtime directories for benchmark measurements.
