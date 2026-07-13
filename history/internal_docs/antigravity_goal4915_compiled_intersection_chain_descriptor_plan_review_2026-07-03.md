# Antigravity Review: Goal4915 Compiled Intersection-Chain Descriptor Plan

**Date**: 2026-07-03
**Verdict**: `approve_goal4915_compiled_intersection_chain_descriptor_probe`
**Reviewer**: Antigravity (External Technical Reviewer)

---

## Executive Summary

[Goal4915](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4915_compiled_intersection_chain_descriptor_plan_2026-07-03.md) proposes a compiled application-layer descriptor probe targeting the remaining prepared-hot performance bottleneck in the `rtdl` execution path. Timing results from [Goal4914](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4914_workspace_api_pod_smoke_report_2026-07-03.md) indicate that setup and query phases are well-optimized, leaving the app-layer output writer—specifically the intersection-bearing chain loop—as the primary contributor to execution time.

The proposed plan is sound, well-bounded, and avoids modifying the RTDL core or native interfaces. It employs a compiled descriptor table (using Numba or structured NumPy) to assemble chain metadata, leaving Python responsible only for final text formatting. Strict performance gates (`writer <= 1.50s`, `hot body <= 3.60s`) and correctness gates (byte equality with the `AuthorOfficial` baseline) are specified.

We recommend approval of the plan under the verdict `approve_goal4915_compiled_intersection_chain_descriptor_probe`.

---

## Detailed Answers to the Six Review Questions

### 1. Does Goal4915 target the true remaining prepared-hot bottleneck after Goal4914?

**Yes.** According to the phase breakdown verified in [Goal4914](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4914_workspace_api_pod_smoke_report_2026-07-03.md#L110-L121), the warm hot body took `3.955s` in total. The output writer consumed `1.875s` (47.4% of the hot body). Within the writer, the chain loop (map0 + map1) took `1.709s` (`1.380s + 0.329s`), which represents 91.1% of the entire writer phase. Since query indexing, re-projection, and traversal (PIP) are already optimized, the chain-loop assembly in the output writer is the true remaining prepared-hot bottleneck.

### 2. Is the plan meaningfully different from the failed/shallow Goal4908 and marginal Goal4910 attempts?

**Yes.**
* **Goal4908 & Goal4910**: Targeted only the simple case of no-intersection (no-xsect) chains by skipping them or routing them via direct descriptor paths. This left the heavy, complex intersection-bearing chains untouched in the slow Python chain loop.
* **Goal4915**: Directly targets the intersection-bearing chains. It builds a compiled descriptor table (chain IDs, map indices, edge spans, intersection group offsets, midpoint face IDs, point slice ranges, keep/drop decisions) in compiled code (Numba or structured NumPy) to bypass Python overhead during heavy assembly.

### 3. Is the scope correctly app-layer only, with no RTDL core/native changes?

**Yes.** The plan specifies that public RTDL LSI, PIP, and workspace APIs remain unchanged. The implementation will be isolated within the application-layer writer, with a strict boundary gate preventing any modifications to code located in `src/rtdsl` or `src/native`.

### 4. Are the acceptance bars (`writer <= 1.50s`, hot body `<= 3.60s`, byte equality) strict enough?

**Yes.** The acceptance bars are rigorous:
* **Writer speed (`<= 1.50s`)**: Requires a minimum reduction of `0.375s` (20%) from the current `1.875s` baseline.
* **Hot body (`<= 3.60s`)**: Requires a minimum reduction of `0.355s` (9%) from the current `3.955s` hot-body baseline.
* **Byte equality**: Mandates 100% byte-for-byte identity with the `AuthorOfficial` baseline output, ensuring absolutely no correctness regressions or semantic drift.

### 5. Is it correct to close as `correct_but_not_worth_productizing__python_text_writer_floor` if the bar is missed?

**Yes.** If compiling the descriptor table does not reduce the writer time to `1.50s` or below, it indicates that Python's text formatting and file write layers have hit a physical execution floor. Documenting this floor with a dedicated termination label ensures that future efforts do not waste resources on shallow application-layer writer micro-optimizations, and points to the necessity of a fully native C++ output writer product if further performance gains are needed.

### 6. Should implementation be authorized?

**Yes.** The plan targets the correct bottleneck with an appropriate compiled approach, establishes strict performance and correctness validation gates, preserves the library's architectural boundaries, and defines a clear and transparent exit condition.

---

## Non-Authorization Boundary Compliance

Approval of [Goal4915](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4915_compiled_intersection_chain_descriptor_plan_2026-07-03.md) does **not** authorize:
* **Modifications to RTDL core/native**: Changing files in `src/rtdsl` or `src/native` is strictly forbidden.
* **Semantic changes**: Public workspace, LSI, and PIP query semantics and interfaces must remain completely unchanged.
* **Architectural leakage**: RayJoin application logic must not be hidden inside the generic RTDL core package.
* **Broad performance claims**: Performance measurements and claims must remain restricted to the Section 5.7 Australia representative dataset and workload.
* **OptiX exposure**: Raw OptiX callbacks must remain encapsulated.
* **V3/V4 resurrection**: No deprecated V3/V4 codebases or claims may be resurrected.
