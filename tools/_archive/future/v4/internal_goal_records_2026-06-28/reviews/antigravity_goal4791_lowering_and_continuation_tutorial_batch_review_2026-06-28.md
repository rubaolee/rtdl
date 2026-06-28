# Review Report: Goal4791 Lowering and Continuation Tutorial Batch

**Date:** 2026-06-28  
**Reviewer:** Antigravity (AI Coding Assistant)  
**Verdict:** `approve_goal4791_lowering_and_continuation_tutorial_batch_complete`

---

## Executive Summary

We have reviewed the implementation of Goal4791 (Lowering and Continuation Tutorial Batch) within the [rtdl_v0_4_release_prep_review](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review) workspace. 

The goal extends the current V4 tutorial sequence with three programs and three corresponding lessons:
1. Component union from fixed-radius rows
2. Bounded witness collection from emitted witness rows
3. Aggregate-frontier rows with weighted grouped continuation

All 21 regression tests run and pass on Windows. The documentation maps, READMEs, and program command parameters are consistent and correct. The teaching materials successfully prioritize RTDL row/relation/kernel conceptual thinking before introducing V4 operator/runtime surfaces.

No unauthorized release claims or boundary violations were found. We recommend approving Goal4791 as complete.

---

## Required Question Responses

### 1. Does [component_union_from_radius.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/component_union_from_radius.py) teach fixed-radius kernel rows and app-owned component-union continuation before introducing the V4 Numba surface?

**Yes.** The program structure and lesson content in [12_component_union_from_radius.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/12_component_union_from_radius.md) teach fixed-radius kernel rows first:
- The RTDL kernel [radius_edges_kernel](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/component_union_from_radius.py#L20) is defined, compiled, and executed to emit radius-neighbor rows.
- The component union logic is presented as a pure Python continuation function [_component_union_from_neighbor_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/component_union_from_radius.py#L53) operating on these neighbor rows.
- Only after this conceptual flow is established does the file introduce the V4 planning request (`plan_operator_request_v4("component_union", partner="numba")`) to map the continuation to the Numba execution surface.

### 2. Does [bounded_witness_collection.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/bounded_witness_collection.py) teach kernel-produced witness rows and bounded collection before introducing the V4 grouped-argmin surface?

**Yes.** The script and the accompanying lesson [13_bounded_witness_collection.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/13_bounded_witness_collection.md) first establish:
- An RTDL kernel [segment_witness_rows_kernel](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/bounded_witness_collection.py#L20) that yields raw segment intersection witness rows.
- A witness extraction helper [_witness_rows_from_kernel_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/bounded_witness_collection.py#L71) followed by the custom continuation [_bounded_collect](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/bounded_witness_collection.py#L42) to sort, cap capacity, and generate validation/overflow rows.
- The V4 grouped-argmin surface (`closest_hit_argmin` with `torch` partner) is only requested and discussed as the measured implementation route once the user understands how the underlying rows are produced.

### 3. Does [aggregate_frontier_rows.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aggregate_frontier_rows.py) honestly use a relation-first lesson instead of faking an `@rt.kernel` predicate that the public tutorial API does not expose?

**Yes.** The program explicitly does not fake an `@rt.kernel` predicate. Instead, [14_aggregate_frontier_rows.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/14_aggregate_frontier_rows.md) teaches the aggregate frontier relation using direct row concepts:
- The frontier rows are calculated in [_frontier_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aggregate_frontier_rows.py#L45) to determine whether to keep aggregate-cell or exact-body rows.
- The force contribution and grouped weighted vector outputs are calculated in [_force_rows](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aggregate_frontier_rows.py#L82) as a python continuation.
- It explicitly documents this in the `honesty_note` field and notes that V4 is used to request the prepared `aggregate_frontier` (native) and `grouped_sum` (cupy) continuation surfaces for this named relation.

### 4. Are the script modes coherent?

**Yes.** The command-line interface `--mode` choices are fully coherent:
- **Component union** ([component_union_from_radius.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/component_union_from_radius.py)): `kernel`, `v4`, `both`, `visible`.
- **Bounded witness collection** ([bounded_witness_collection.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/bounded_witness_collection.py)): `kernel`, `v4`, `both`, `visible`.
- **Aggregate frontier** ([aggregate_frontier_rows.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/aggregate_frontier_rows.py)): `relation`, `v4`, `both`, `visible`.
Using `relation` instead of `kernel` for aggregate frontier is correct because it aligns with the relation-first approach of the tutorial without faking a kernel decorator.

### 5. Do the tutorial pages explain the RTDL relation/row/continuation model clearly enough that the V4 wrapper does not become a black-box substitute for learning?

**Yes.** Each page outlines the exact data flow:
- [12_component_union_from_radius.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/12_component_union_from_radius.md) details how radius neighbor rows are mapped to density-reachable union edges and component labels.
- [13_bounded_witness_collection.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/13_bounded_witness_collection.md) focuses on witness ranking, slots, capacity limits, and inspecting overflow validation rows.
- [14_aggregate_frontier_rows.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/14_aggregate_frontier_rows.md) presents the Barnes-Hut opening ratio check and grouped vector reduction.
By showing how these operations work step-by-step on row structures, the lessons teach the conceptual model rather than presenting V4 as a black box.

### 6. Are partner statements honest and bounded?

**Yes.** The partner claims are carefully bounded to their respective operations:
- Numba is described strictly as an explicit partner for the component-union continuation.
- Torch is discussed as the partner for closest-witness grouped argmin.
- CuPy is introduced as the partner for grouped vector sum.
None of the statements imply that the V4 compilation converts the application-specific continuation logic itself into a custom native kernel.

### 7. Are public links and commands consistent?

**Yes.**
- The [tutorials/current/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/tutorials/current/README.md), [examples/tutorial_programs/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/tutorial_programs/README.md), [examples/README.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/examples/README.md), and [public_documentation_map.md](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/docs/public_documentation_map.md) all list the new programs with their correct `--mode` flags.
- Relative links inside the markdown tutorials resolve correctly.
- Documentation indexes correctly include the new lessons.

### 8. Are Windows and Linux validations sufficient for this goal?

**Yes.**
- Windows execution has been verified locally. All individual tutorial modes run without errors, and the main validation suite (`v4_goal4640_public_docs_cleanup_test.py`, `v4_frontdoor_test.py`, `v4_goal4643_publication_decision_test.py`) passed successfully in 84.92 seconds.
- The completion record documents a clean Linux checkout simulation (`/tmp/rtdl_goal4791_lowering`) passing all 21 tests and program outputs.

### 9. Should Goal4791 be accepted as complete, require amendments, or be blocked?

Goal4791 satisfies all teaching requirements, passes all documentation cleanup and regression tests, has coherent modes, and contains no boundary violations. It should be accepted as complete with the verdict label:
`approve_goal4791_lowering_and_continuation_tutorial_batch_complete`

---

## Non-Authorization Boundary Check

This review confirms that the following are **not** authorized by this goal acceptance:
- a V4 public tag,
- broad V4 speedup wording,
- whole-app performance claims,
- Tier-3 arbitrary callback claims,
- raw OptiX callback claims,
- C ABI or embedding claims,
- paper-reproduction claims,
- app-specific native-kernel claims.
