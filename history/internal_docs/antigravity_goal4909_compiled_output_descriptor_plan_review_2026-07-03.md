# Goal4909 Critical External Review: Compiled Output-Chain Descriptor Plan

Date: 2026-07-03

## Verdict Label
**`approve_goal4909_compiled_descriptor_implementation_gate`**

***

## Findings & Answers to Review Questions

### 1. Is Goal4909 a real compiled descriptor plan rather than another Python micro-fast-path?
**Yes.** Goal4909 is a genuine compiled descriptor plan.
* **Contrast with Goal4908:** The failed [Goal4908](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4908_compiled_descriptor_probe_negative_result_2026-07-03.md) attempt was a Python-layer fast path that merely rearranged conditional checks and constructed python lists of `138,988` direct chain points in Python, which incurred high allocation/duplication overhead and worsened performance (writer: `1.946s -> 2.222s`).
* **Goal4909 Mechanism:** In [Goal4909](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4909_compiled_output_descriptor_plan_2026-07-03.md), the heavy logical loop bookkeeping—including fragment chain indexing, range calculations, and segment classifications (represented by `fragment_kind`)—is offloaded into Numba compiled kernels in [goal4886_rayjoin_numba_overlay_kernels.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py).
* **Python's Role:** Python is relieved of traversing the per-point overlay state machine. Instead, it loops over compact, pre-allocated descriptor arrays, performing only the final text serialization and formatting, thereby eliminating Python-side loop overhead.

### 2. Is the performance bar appropriate and falsifiable?
**Yes.** The performance targets are strict, clear, and fully falsifiable:
* **Falsifiability:** The plan establishes exact, measurable criteria on the Australia representative dataset (using the `prepared-hot repeat1` run):
  * **Correctness:** Byte-for-byte matching with AuthorOfficial output, gated by SHA256 checksum: `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e`.
  * **Writer Time:** `< 1.50s` (a `~23%` reduction from Goal4907's `1.946s` baseline).
  * **Hot Body Time:** `< 3.60s` (an `~10%` reduction from Goal4907's `4.013s`).
* **Appropriateness:** Since introducing Numba compilation adds build complexity, cache management, and strict schema structures, a minor performance improvement would not justify the overhead. Gating the authorization on a hard `<1.50s` writer target ensures that we only proceed with this approach if it yields a substantial, step-function speedup. The fallback classifications (such as `partial_descriptor_win` or `negative_descriptor_result_stop_writer_microline`) are explicitly pre-defined, preventing goalpost shifting.

### 3. Does the plan keep the work in the app-layer/partner boundary rather than hiding RayJoin in RTDL core?
**Yes.** The boundary between the RTDL core and the RayJoin application layer is kept clean and explicit.
* The plan prohibits any changes to RTDL core or native source code under `src/` ("RTDL core/native changes: none").
* The Numba kernels must be placed in [goal4886_rayjoin_numba_overlay_kernels.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4886_rayjoin_numba_overlay_kernels.py) and are explicitly forbidden from importing `rtdsl.rayjoin_overlay`.
* This preserves the architectural division:
  * **RTDL Core:** Handles generic spatial indexing and point location (LSI, PIP).
  * **App Layer:** Handles the paper-specific RayJoin output-chain logic.
  * **Partner:** Numba assists in accelerating the app-layer's CPU bookkeeping.

### 4. Is the boundary against RTDL core/native RayJoin-specific code clear enough?
**Yes.** The plan's boundary separation is robust.
* By separating the generic geometric query processing from the specific output format emission, RTDL core remains generic and reusable for other pipelines.
* RayJoin-specific structures like "left/right/other face ids for emitted fragments" and "sorted intersection rows" are kept strictly at the application layer and passed as flat arrays to the Numba partner module. This prevents any RayJoin-specific concepts or formats from leaking into RTDL's core geometry engines.

### 5. Should the first implementation be conservative, or must it attempt full descriptor coverage immediately?
**It should be conservative.**
* A conservative approach is highly recommended. Developing Numba-compiled code that handles multiple branching conditions, index offsets, and edge cases is notoriously difficult to debug and prone to alignment issues.
* Allowing the initial implementation to handle only no-intersection kept chains and simple single-intersection chains—while utilizing a robust Python fallback state machine for complex cases—mitigates correctness risk.
* This incremental strategy ensures that correctness (byte equality) can be validated at each step, while the performance gains of the optimized descriptor path can be measured and scaled progressively.

***

## Non-Authorization Boundaries (Preserved)

This review enforces and preserves all non-authorization boundaries. The following claims and actions remain **unauthorized**:
1. **RTDL Core Modifications:** No RayJoin-specific acceleration logic or kernels may be introduced into the RTDL core package.
2. **Broad Performance Claims:** Performance claims must remain bounded to the specific prepared-hot replay harness and dataset. No general RTDL traversal or pipeline speedup claims are authorized.
3. **Changing Correctness/Comparator Rules:** The byte-equality output contract with `AuthorOfficial` is non-negotiable and must not be relaxed.
4. **V3/V4 Release Resurrection:** Any revival or prep work for V3/V4 releases remains strictly unauthorized.
