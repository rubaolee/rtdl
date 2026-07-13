# Goal4899 Critical External Review: Numba Partner Current Comparison

Date: 2026-07-03

## Verdict Label
**`approve_goal4899_numba_partner_app_continuation_result`**

***

## Findings & Answers to Review Questions

### 1. Does the report correctly state that Numba accelerates app-layer continuation/writer work, not RTDL primitive traversal?
Yes. The [comparison report](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4899_numba_partner_current_comparison_report_2026-07-03.md) is highly explicit and rigorous regarding this boundary. It states that Numba does not replace RTDL LSI/PIP primitives, does not reside on the RTDL primitive traversal path, and operates strictly in the application-layer continuation/writer path. This is verified by checking the harness file [goal4886_section57_public_primitives_overlay_numba_harness.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_section57_public_primitives_overlay_numba_harness.py), where Numba JIT-compiled kernels from [goal4886_rayjoin_numba_overlay_kernels.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py) are monkeypatched only onto application-layer wrappers (`midpoint_points`, `dedupe_point_pairs`, and `write_output_chains_streaming`).

### 2. Is the three-way table fair enough, especially the warning that AuthorOfficial raw CDB read and RTDL packed-cache load are not the same IO condition?
Yes. The report includes a clear disclaimer immediately below the table stating:
> *The AuthorOfficial total includes raw CDB reading. The RTDL totals use the current packed-cache path. Therefore, do not headline total wall-clock ratios as a language-stack speedup. The cleaner comparison is by phase.*

This warning prevents unfair comparison or misleading overclaims based on total wall-clock ratios.

### 3. Does the evidence support the stated writer speedup (`17.101s` to `2.358s`) and compute+write speedup (`27.034s` to `13.936s`)?
Yes, the logged timings in the JSON artifacts match the report's numbers exactly:
* **Writer Speedup:**
  * Python-only writer: `17.101s` (specifically `17.1014s` in [goal4898_prepared_query_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4898_prepared_query_overlay_summary_2026-07-03.json))
  * Numba+RTDL writer: `2.358s` (specifically `2.3577s` in [goal4899_numba_prepared_query_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4899_numba_prepared_query_overlay_summary_2026-07-03.json))
  * This yields a **`7.25x`** speedup on the writer phase.
* **Compute+Write Speedup (Excluding Load):**
  * Python-only: `27.034s` (specifically `27.0338s` in [goal4898_prepared_query_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4898_prepared_query_overlay_summary_2026-07-03.json))
  * Numba+RTDL: `13.936s` (specifically `13.9362s` in [goal4899_numba_prepared_query_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4899_numba_prepared_query_overlay_summary_2026-07-03.json))
  * This yields a **`1.94x`** speedup on the compute+write phase as a whole.
* **No RTDL Traversal Speedup:**
  * The report also transparently shows that `compute excluding load+write` actually increased slightly from `9.932s` to `11.578s` due to Numba JIT overheads and conversions, reinforcing that Numba did not accelerate the native RTDL traversal path.

### 4. Does the report avoid claiming that RTDL+Numba matches AuthorOfficial hot performance?
Yes. The report highlights a `155x` gap in hot-compute time (`0.074s` for AuthorOfficial vs `11.578s` for Numba+RTDL). It explains that this gap exists because the AuthorOfficial implementation fuses traversal and geometry work inside C++/CUDA/OptiX kernels, whereas the current RTDL Python wrapper path has multiple materialized, Python-visible stages.

### 5. Does the report preserve the key correctness fact: byte-identical output to AuthorOfficial on the representative pair?
Yes. The report and the evidence files ([goal4899_numba_prepared_query_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4899_numba_prepared_query_overlay_summary_2026-07-03.json)) confirm:
* `byte_equal_to_author: true`
* `sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`
* Lines: `276320`, Bytes: `6189260`

### 6. Does the report correctly identify the next high-performance problem as fusion/materialization/dataflow placement rather than "install Numba and done"?
Yes. The report notes that Numba helps downstream continuation, but the remaining gap to the AuthorOfficial hot path is about traversal, fusion, and dataflow placement. It suggests that future high-performance R&D must focus on reducing intermediate Python-layer materialization and pushing dataflow down into runtime-managed/fused stages.

### 7. Are any claims too broad or misleading?
No. The report is carefully constrained, well-documented, and explicitly outlines what Numba did and did not improve.

***

## Non-Authorization Boundaries (Preserved)

This review strictly enforces and preserves all non-authorization boundaries. The following claims or activities remain **unauthorized**:
1. **Broad RTDL/RayJoin speedup claims:** The observed gains are strictly restricted to the specific app-layer writer/continuation phase on the Australia representative workload.
2. **Full Section 5.7 eight-pair claims:** Claims are only validated on the representative current-source lakes × parks pair.
3. **Claims that Numba accelerates RTDL primitive traversal:** Numba operates entirely outside RTDL primitive traversal (e.g., LSI and PIP).
4. **Claims that total wall time beats AuthorOfficial in a fair same-I/O comparison:** Total wall time comparisons remain invalid due to differing I/O pathways (raw CDB vs packed cache).
5. **V3/V4 release resurrection claims:** No statements regarding future major releases are authorized.
