# Goal4897 Critical External Review: Numba Partner Continuation Validation

Date: 2026-07-03

## Verdict Label
**`approve_goal4897_numba_partner_enabled_bounded_speedup`**

***

## Findings & Answers to Review Questions

### 1. Does the evidence correctly identify that the prior `numba_available=false` state was caused by missing POD package installation, not by a broken code path?
Yes. The validation report correctly demonstrates that the underlying harness and kernels were already wired and functional on the fallback reference path, but the Python environment on the POD threw a `ModuleNotFoundError` for `numba`. Once the package was installed (`python -m pip install --break-system-packages numba`), JIT compilation succeeded, the kernels loaded correctly, and the harness successfully reported `NUMBA_AVAILABLE: true` with version `0.66.0`.

### 2. Does synthetic parity show that the Numba kernels match their Python references?
Yes. The synthetic parity summary logged in [goal4897_numba_synthetic_parity_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4897_numba_synthetic_parity_summary_2026-07-03.json) confirms that all JIT-compiled kernels match their Python references exactly. The verified keys are:
* `midpoint_pairs_match: true`
* `dedupe_mask_match: true`
* `chain_keep_match: true`
* `chain_has_xsects_match: true`
* `writer_skip_decision_match: true`

### 3. Does the representative overlay remain byte-equal after enabling Numba?
Yes. The representative Australia lakes × parks current-source overlay run with Numba active remains fully byte-equal to the reference AuthorOfficial comparator. This is evidenced by:
* `byte_equal_to_author: true` reported in both [goal4897_numba_first_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4897_numba_first_overlay_summary_2026-07-03.json) and [goal4897_numba_repeat_overlay_summary_2026-07-03.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4897_numba_repeat_overlay_summary_2026-07-03.json).
* The output has exactly 276,320 lines and produces the identical SHA256 signature (`a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`).

### 4. Is the reported performance effect bounded and honest: about 1.30x on writer/app-continuation and about 1.07x end-to-end under the representative warmed condition?
Yes. The comparison against the same-wrapper, pair-id LSI baseline without Numba (Goal4896) demonstrates honest, bounded, and qualified speedups:
* **Writer/App-Continuation Phase:** Decreased from `3.355789s` (Goal4896) to `2.583972s` (Goal4897), achieving a speedup of **`1.30x`** (`3.3557888 / 2.5839716 = 1.2987x`).
* **Wrapper Total Time:** Decreased from `14.055081s` (Goal4896) to `13.167668s` (Goal4897), achieving a speedup of **`1.07x`** (`14.0550806 / 13.1676682 = 1.0674x`).
The report transparently attributes this modest end-to-end speedup to the fact that JIT optimization is limited to specific Python helper routines (like midpoint extraction, deduplication, and skip planning), leaving file I/O and text formatting unaccelerated.

### 5. Does the report correctly classify the Numba code as application-layer partner continuation, not RTDL core and not RTDL primitive-path execution?
Yes. The report correctly maps the boundaries:
* **Generic RTDL Core (unmodified):** Public LSI primitive, public point-location/PIP primitive, pair-id rows retrieval, and CDB packed cache.
* **Application Layer (Numba JIT-compiled):** Section 5.7 workflow logic, midpoint generation, file output writing, chain-skip plans, and JIT-compiled kernels in `goal4886_rayjoin_numba_overlay_kernels.py`.
The JIT compiler only runs on application-layer wrappers and does not modify or execute inside `src/rtdsl/**` or `src/native/**`.

### 6. Does the report avoid overclaiming full Section 5.7, broad RayJoin speedup, or AuthorOfficial overall win?
Yes. The report lists these restrictions under its "Boundaries" section, stating clearly that it does not claim a broad RayJoin speedup, does not validate the full Section 5.7 eight-pair suite, does not suggest that RTDL beats the overall AuthorOfficial wall-time, and does not claim Numba is on the RTDL native primitive path or correctness-critical.

### 7. Is it acceptable to close Goal4897 with `completed_numba_partner_enabled__bounded_app_continuation_speedup`?
Yes. The verification metrics, correctness match, and bounded speedups provide sufficient and complete evidence to close Goal4897 with the status of `completed_numba_partner_enabled__bounded_app_continuation_speedup`.

***

## Non-Authorization Boundaries (Preserved)

This review strictly preserves all non-authorization boundaries. The following claims or activities remain **unauthorized**:
1. **Broad RTDL/RayJoin performance claims:** The performance improvement is explicitly restricted to the Australia representative Section 5.7 public-primitives route.
2. **Full Section 5.7 eight-pair claims:** Correctness and performance claims have not been extended to the full eight-pair set.
3. **AuthorOfficial overall performance win claims:** Overall wall-time comparisons against the author codebase are prohibited due to missing official overall wall-time logs.
4. **Claiming Numba is correctness-critical:** Numba remains an optional performance continuation partner and is not correctness-critical.
5. **Claiming Numba runs inside RTDL primitives:** The JIT kernels operate strictly on application-layer outputs post-traversal.
6. **Claiming this solves the in-traversal fusion/callback gap:** The architecture bottleneck for in-kernel callbacks remains open.
7. **V3/V4 release claims:** No claims are authorized regarding future major releases.
