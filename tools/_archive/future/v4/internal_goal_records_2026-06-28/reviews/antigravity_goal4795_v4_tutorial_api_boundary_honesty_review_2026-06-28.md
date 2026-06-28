# Review Result: Goal4795 V4 Tutorial/API Boundary Honesty Review

**Date:** 2026-06-28  
**Reviewer:** Antigravity (AI Coding Assistant)  
**Target Goal:** Goal4795 V4 tutorial/API boundary honesty pass  
**Verdict:** `approve_goal4795_v4_tutorial_api_boundary_honesty_complete`  

---

## Required Questions & Answers

### 1. Do the public docs now clearly distinguish RTDL language-layer lessons from V4 runtime/operator-surface lessons?
**Yes.** The public documentation has been updated to prevent users from assuming that being in the V4 tutorial path implies the existence of a V4 runtime surface or specific operator.
- [README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/README.md) clarifies that the tutorial programs include both language-layer lessons and runtime/operator-surface lessons.
- [docs/current_v4_status.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/current_v4_status.md) and [docs/public_documentation_map.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/public_documentation_map.md) explicitly warn that the quick-check path mixes language-layer lowering lessons (like `sorting_rows.py`) with V4 runtime-surface checks.

### 2. Does `sorting_rows.py` now machine-state that it has no V4 operator surface?
**Yes.** The program [examples/tutorial_programs/sorting_rows.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/sorting_rows.py) returns a JSON payload containing the following metadata fields explicitly stating the boundary:
```json
"lesson_layer": "rtdl_kernel_relation",
"v4_operator_surface": null,
"v4_runtime_claim": "none; this lesson has no V4 sort or segment-intersection operator surface"
```

### 3. Does `03_sorting_rows.md` clearly say there is no V4 sorting operator surface and no V4 segment-intersection runtime surface?
**Yes.** The tutorial file [tutorials/current/03_sorting_rows.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/03_sorting_rows.md) contains an explicit **Boundary** warning block:
> Boundary: this lesson has no V4 sorting operator surface and no V4 segment-intersection runtime surface. It is here because V4 includes the current RTDL kernel/relation language path, not because V4 exposes a `sort` operator.

Additionally, under the "What You Should Learn" section, it explicitly states:
> - A V4 tutorial can be a language-layer lesson without having a V4 operator surface.

### 4. Do the tutorial and examples indexes avoid implying every V4 tutorial-path program has a V4 runtime surface?
**Yes.**
- The tutorial index [tutorials/current/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/README.md) details that the path contains two kinds of lessons (language-layer lessons vs. V4 runtime lessons) and warns: *"Do not read 'in the V4 tutorial path' as 'has a V4 operator surface.'"*
- The examples index [examples/tutorial_programs/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/README.md) has a similar warning block and explicitly describes `sorting_rows.py` as: *"Convert nonnegative integers into segment-intersection hits, then use hit counts as rank. This is a language-layer lesson with no V4 sorting operator surface."*
- The root examples index [examples/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/README.md) also warns: *"A tutorial program has a V4 runtime/operator surface only when it explicitly names one."*

### 5. Does the new test protect this boundary from regression?
**Yes.** The unit test `test_sorting_is_language_layer_not_v4_runtime_surface` added to [tests/v4_goal4640_public_docs_cleanup_test.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tests/v4_goal4640_public_docs_cleanup_test.py):
1. Reads `03_sorting_rows.md`, `tutorials/current/README.md`, and `examples/tutorial_programs/README.md` to ensure the required disclaimer disclaiming V4 operator/runtime surfaces is present.
2. Invokes `sorting_rows.py` programmatically and asserts that `lesson_layer` is `"rtdl_kernel_relation"`, `v4_operator_surface` is `None`, and `v4_runtime_claim` contains `"no V4 sort"`.

### 6. Are Windows and Linux validations sufficient for this goal?
**Yes.** Validation was completed successfully. The unittests were executed locally on the Windows workspace and ran to completion successfully:
```text
Ran 22 tests in 85.336s
OK
```
Clean-copy Linux simulation was verified on host `192.168.1.20` under `/tmp/rtdl_goal4795_boundary_honesty` with identical success. This cross-platform validation is fully sufficient for documentation and API boundary logic.

### 7. Should Goal4795 be accepted as complete, require amendments, or be blocked?
**Accepted as complete** under the verdict label `approve_goal4795_v4_tutorial_api_boundary_honesty_complete`.

---

## Non-Authorization Boundary

As required by the review standard, this review **does not authorize**:
- a V4 sorting operator claim,
- a V4 segment-intersection runtime-surface claim,
- broad V4 speedup wording,
- whole-app performance claims,
- a V4 public tag,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims, or
- paper-reproduction claims.
