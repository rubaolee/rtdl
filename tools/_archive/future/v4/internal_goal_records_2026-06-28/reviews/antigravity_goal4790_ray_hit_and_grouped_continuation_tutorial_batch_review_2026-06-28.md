# RTDL V4 External Review: Goal4790 Ray Hit And Grouped Continuation Tutorial Batch

**Date:** 2026-06-28  
**Reviewer:** Antigravity (External Reviewer)  
**Verdict:** `approve_goal4790_ray_hit_and_grouped_continuation_tutorial_batch_complete`

---

## Required Review Questions & Answers

### 1. Does `ray_triangle_hits.py` teach the RTDL kernel relation before the V4 runtime surface?
**Yes.**  
In [ray_triangle_hits.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/ray_triangle_hits.py), the kernel definition `ray_triangle_any_hit_kernel` is placed at the top (lines 20–26). The script first shows execution under `--mode kernel` using `rt.run_cpu_python_reference` (lines 101–120), mirrors the relation in Python via `--mode visible` (lines 122–155), and introduces the V4 planning interface (`rtdl_v4.plan_operator_request_v4`) last in `--mode v4` (lines 158–174).  
Similarly, the tutorial page [10_ray_triangle_hits.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/10_ray_triangle_hits.md) teaches the kernel relation and the concept of any-hit/closest-hit/hit-count rows first, before introducing the V4 runtime mapping at the end of the lesson.

### 2. Does `continuation_grouped_sum.py` teach continuation as a post-kernel reduction over relation rows?
**Yes.**  
In [continuation_grouped_sum.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/continuation_grouped_sum.py), the kernel emits `hit_count` rows per ray (lines 21–27), which are then consumed by the Python function `_group_hit_count_rows` (lines 46–67) to group by application-owned keys and calculate sums.  
The tutorial page [11_grouped_continuations.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/11_grouped_continuations.md) introduces the continuation concept explicitly as a post-kernel step:
> "This lesson teaches continuation as a step after a kernel relation, not as a magic replacement for the relation."

It explains how relation rows are grouped by app-owned keys and reduced, showing manual Python loops before explaining V4 partner-backed operators.

### 3. Do both programs coherently support `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`?
**Yes.**  
Both programs successfully parse these options and run the corresponding functions:
- `run_kernel_mode()`
- `run_visible_flow()`
- `run_v4_mode()`
- `run_both_modes()`

Each function returns a well-structured dict printed as JSON. The CLI arguments and behavior are consistent across both programs.

### 4. Do the tutorial pages avoid teaching a one-call black-box app API?
**Yes.**  
Both [10_ray_triangle_hits.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/10_ray_triangle_hits.md) and [11_grouped_continuations.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/11_grouped_continuations.md) decompose the RTDL pipeline step-by-step (inputs, traversal, refinement, emission, and continuation reduction) instead of wrapping the logic in a single opaque call. They show that V4 operator planning maps specific recognized relation patterns to partner-backed routes without altering the program semantics.

### 5. Is partner wording honest and explicit, without implying broad V4-over-V2/V3 speedup?
**Yes.**  
The partner wording in the lessons is honest, localized, and explicit:
- In lesson 10, it states: *"The V4 surface does not change the program meaning. It is the prepared partner-backed route for a recognized ray/triangle any-hit relation."*
- In lesson 11, it states: *"The partner is explicit. CuPy or Torch being good at a continuation does not turn that continuation into an app-specific RTDL kernel. It remains a generic operator over relation rows."*

No broad, unqualified claims about V4-over-V2/V3 speedups are made.

### 6. Are lessons 10 and 11 correctly linked into the public tutorial path?
**Yes.**  
They are linked in the sequential list in [tutorials/current/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/README.md) as lessons 10 and 11. Lesson 10 links to Lesson 11 at the bottom, and Lesson 11 links forward to subsequent lowering topics.

### 7. Are the Windows and Linux validation results sufficient to move to the next tutorial batch?
**Yes.**  
Both Windows and Linux validation test runs passed successfully (21 tests in ~79s on Windows, ~30s on Linux). A local validation run of the test suite (`tests.v4_goal4640_public_docs_cleanup_test`, `tests.v4_frontdoor_test`, `tests.v4_goal4643_publication_decision_test`) was executed and also completed successfully without errors.

---

## Non-Authorization Boundaries Check
As requested, this review explicitly preserves all boundaries and does **not** authorize:
- A new release claim
- A new performance claim
- A broad V4-over-V2/V3 speedup claim
- Tier-3 arbitrary callback support
- Raw OptiX callback support
- C ABI, embedding, or non-Python host claims
- Full paper-reproduction support
- Any application-specific native-kernel exceptions
