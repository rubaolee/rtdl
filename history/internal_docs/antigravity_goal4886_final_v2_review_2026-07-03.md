# Goal4886 Critical External Review (v2): RayJoin Numba Partner Acceleration

Date: 2026-07-03

## Verdict Label
**`approve_goal4886_final_v2_engineering_evidence_with_claude_debt`**

***

## Executive Summary

This critical review evaluates the final Numba partner evidence submitted under **Goal4886** for the RayJoin paper-reproduction application. The review confirms that the work strictly adheres to correctness, architectural, and performance boundaries. A real, bounded speedup is proven on the Australia representative Section 5.7 route by accelerating the application-layer writer phase through a JIT-compiled chain skip decision, while keeping all core RTDL components and native LSI/PIP primitives untouched.

Claude/third-review debt remains open due to the unavailability of `claude` from the execution path.

***

## Detailed Answers to Review Questions

### 1. Did Goal4886 preserve the current RayJoin correctness/comparator boundary?
Yes. The output validation pipeline remains fully intact. The accelerated harness was validated directly against the final `AuthorOfficial` comparator output (`Author+RTDLContractPatch`), producing a byte-equal file with the matching SHA256 checksum (`a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`) and identical line count (`276320`).

### 2. Did it avoid RTDL core/native edits and avoid bundled rayjoin_overlay imports?
Yes. No edits were made to the core folders `src/rtdsl/**` or `src/native/**`. The harness contains an explicit runtime safety check confirming that `rtdsl.rayjoin_overlay` is not imported. The Numba partner kernels are isolated in [goal4886_rayjoin_numba_overlay_kernels.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py).

### 3. Are the Numba kernels app-layer partner work, not replacement of RTDL LSI/PIP?
Yes. The JIT-compiled kernels (`midpoint_pairs_numba`, `dedupe_consecutive_points_numba`, `chain_keep_numba`, `chain_has_xsects_numba`, and `writer_skip_decision_numba`) operate exclusively on the Python application-layer continuation post-processing. Native RTDL LSI/PIP primitives are executed without modification.

### 4. Does synthetic parity cover the explicit writer skip decision?
Yes. The synthetic tests cover `chain_has_xsects_numba` and `writer_skip_decision_numba` as documented in [goal4886_pod_numba_synthetic_parity_skip_v2.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_pod_numba_synthetic_parity_skip_v2.json), testing four cases:
* `case0_has_xsect_do_not_skip`: `True`
* `case1_no_xsect_terminal_drop_skip`: `True`
* `case2_no_xsect_terminal_keep_do_not_skip`: `True`
* `case3_has_xsect_do_not_skip`: `True`
All tests match the Python reference implementations exactly.

### 5. Does the Australia representative full run remain byte-equal?
Yes. The execution summary files on the POD, including the final explicit skip-decision run ([goal4886_pod_numba_au_skip_v2_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_pod_numba_au_skip_v2_summary.json)), report `byte_equal_to_author: true` and successfully verify against the reference checksum.

### 6. Is the bounded performance claim honest: best repeat 1.166x overall, explicit skip-decision v2 1.130x overall / 8.10x writer phase, no broad RayJoin claim?
Yes. The report transparently reports:
* A negative performance result (`0.964x`) when compiling midpoint/dedupe wrappers alone due to JIT overhead.
* The best-measured writer-skip repeat run overall speedup of **`1.166x`** (`100.531s` vs. `117.258s` Current RTDL) with a `9.12x` writer-phase speedup (`1.811s` vs. `16.525s`).
* The final, better-specified explicit skip-decision v2 run overall speedup of **`1.130x`** (`103.786s` vs. `117.258s`) with an **`8.10x`** writer-phase speedup (`2.040s` vs. `16.525s`).
No broad or generalized RayJoin speedup claims are made.

### 7. Is AuthorOfficial wall-time handling honest: phase timings only, no invalid wall denominator?
Yes. The report documents that overall AuthorOfficial wall-time is unavailable. It reports the failure of the two rerun attempts (one reusing serialized maps and one with fresh serialization) to produce the reference output checksum, properly designates them as invalid baselines, and refuses to use them as denominators for any speedup claims.

### 8. Can this close as engineering evidence, with Claude/third-review debt still open?
Yes. The engineering evidence is complete and verified. The goal can close under the status `engineering_evidence_complete__bounded_numba_writer_skip_speedup__pending_claude_review_debt`, with the Claude/third-review debt logged and remaining open in [goal4886_review_debt_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_review_debt_2026-07-03.md).

***

## Non-Authorization Boundaries (Enforced)
1. **No broad RayJoin speedup claims** are authorized.
2. **No full hidden-input or eight-pair paper claims** are authorized.
3. **No runtime/core edits** are permitted.
4. **AuthorOfficial wall-time attempts** must not be used as overall speedup baselines.
