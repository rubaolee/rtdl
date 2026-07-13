# Goal4886 Critical External Re-Review: AuthorOfficial Wall Boundary Assessment

Date: 2026-07-03

## Verdict Label
**`approve_goal4886_authorofficial_wall_boundary_honest`**

***

## Executive Summary

This re-review focuses on the amended evidence under **Goal4886** (RayJoin Numba Partner Acceleration), specifically evaluating the two attempts to recover a wall-time baseline for the `AuthorOfficial` program.

Neither rerun reproduced the reference output's SHA256 checksum (`a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`) or line count (`276320`). Consequently, neither has been promoted as a valid wall baseline.

This assessment concludes that [goal4886_rayjoin_numba_partner_acceleration_report_2026-07-03.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_rayjoin_numba_partner_acceleration_report_2026-07-03.md) handles the three-way comparison boundary honestly and conservatively. It accurately models:
1. A valid comparison between **Current RTDL** and **RTDL+Numba** wall-times (both byte-equal to the reference).
2. The validity of **AuthorOfficial** phase timings recorded in the final comparator logs for structural insight.
3. The unavailability of a final **AuthorOfficial** overall wall-time baseline.

***

## Detailed Findings

### 1. Analysis of the AuthorOfficial Rerun Attempts

Two distinct attempts were made to run the `AuthorOfficial` binary on the POD environment to capture `/usr/bin/time` wall-time metrics:

#### Rerun 1: Serialized Maps Reuse
* **Evidence File:** [goal4886_authorofficial_wall_attempt_invalid_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_authorofficial_wall_attempt_invalid_summary.json)
* **Execution Details:** Reused final pre-deserialized maps.
* **Captured Wall-time:** `3.453s`
* **Output Signature:**
  * SHA256: `3fbd155e2b90938c8f11db876055c14c71ed532e7c5acf84103aad8910618ca8`
  * Line Count: `276444`
* **Result:** **Invalid Baseline**. Mismatched the reference SHA256 and line count. The `3.453s` timing represents a partial run that bypassed full text CDB parsing, and is topologically mismatched.

#### Rerun 2: Fresh Serialize from Text CDB (Correct Working Directory)
* **Evidence File:** [goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_authorofficial_wall_attempt_freshser_cwd_invalid_summary.json)
* **Execution Details:** Fresh serialization starting directly from raw text CDB inputs, using the correct `release/bin` execution directory context.
* **Captured Wall-time:** `148.363s`
* **Output Signature:**
  * SHA256: `9d82b38aac634c76738e6c2552cbac6255a30460377ceb66e66b13450d223639`
  * Line Count: `276407`
* **Result:** **Invalid Baseline**. Mismatched the reference SHA256 and line count. Although this represents the closest operational run, differences in geometry or face ordering under this runtime setup resulted in minor topological discrepancies (276,407 lines vs. 276,320 lines).

> [!IMPORTANT]
> Because neither execution produced byte-equal outputs compared to the target reference, the report's decision **not** to promote either of these timings as a baseline is correct. Promoting them would violate the project's strict correctness-first comparator boundary.

---

### 2. Evaluation of the Three-Way Comparison Boundary

The report splits the three-way comparison into three clear, well-bounded segments:

| Target | Status | Validation / Availability |
| :--- | :--- | :--- |
| **Current RTDL** vs **RTDL+Numba** | **Valid Wall-Time Comparison** | Both configurations output byte-equal results (`sha256: a15e0dd4...`) under identical POD runtime conditions. |
| **AuthorOfficial Phase Timings** | **Valid Architectural Reference** | Phase timings are cited directly from the final log of the reference comparator run. |
| **AuthorOfficial Overall Wall-Time** | **Unavailable** | The original reference log did not capture overall wall-time, and rerun attempts did not preserve byte-equality. |

#### A. Validity of RTDL vs RTDL+Numba Comparison
The wall-time comparison between Current RTDL and RTDL+Numba is fully verified:
* **Current RTDL Repeat:** `117.258s` overall (with `16.525s` writer phase) — [goal4886_pod_current_au_repeat_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_pod_current_au_repeat_summary.json)
* **RTDL+Numba Writer Skip Repeat:** `100.531s` overall (with `1.811s` writer phase) — [goal4886_pod_numba_au_skip_repeat_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_pod_numba_au_skip_repeat_summary.json)
* **Output Checksum:** Both outputs match the reference SHA256 (`a15e0dd4...`) and line count (`276320`) exactly, confirming zero correctness regression.
* **Speedup Metric:** An overall speedup of `1.166x` (and a writer-phase speedup of `9.12x`) is validly proven for the Australia representative dataset.

#### B. Validity of AuthorOfficial Final Phase Timings
The report cites the original phase timings (e.g., Read map 0: `134.688s`, Compute output polygons: `0.00866s`) from the official log. This provides a valid structural representation of the C++/OptiX codebase's internal profile. It highlights that the C++ version spends the vast majority of its time on serialization/deserialization and reading CDB data (~144 seconds), while native GPU traversals are near-instantaneous.

#### C. Honesty Regarding Missing AuthorOfficial Wall Baseline
The report does not attempt to estimate or patch an overall wall-time denominator for AuthorOfficial.
* It notes that the older run recorded `AUTHOR_WALL_SEC=146`, but explicitly designates this as non-final.
* It documents the failures of the two rerun attempts to match the target SHA256.
* It concludes that AuthorOfficial overall wall-time is **unavailable** for a direct speedup claim denominator.

> [!NOTE]
> By restricting all speedup claims to `Current RTDL` vs `RTDL+Numba`, the report prevents misleading comparisons against an unverified or structurally mismatched baseline.

***

## Conclusion & Non-Authorization Enforcement

The amended Goal4886 report handles the comparison boundary with high integrity. The non-authorization boundaries are fully preserved:
1. **No overall speedup claims against AuthorOfficial wall-time** are made.
2. **Performance metrics are strictly limited** to the Australia representative dataset and route.
3. **No native RTDL code edits** were introduced, keeping core codebases untouched.

The evidence is complete, the logic is sound, and the comparison is honest. The review recommends approval under the verdict label:
**`approve_goal4886_authorofficial_wall_boundary_honest`**
