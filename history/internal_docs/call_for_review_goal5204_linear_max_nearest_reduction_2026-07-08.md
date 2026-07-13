# Call For Review: Goal5204 Linear Max-Nearest Reduction

Date: 2026-07-08

Please strictly review Goal5204.

Files under review:

```text
history/internal_docs/goal5204_linear_max_nearest_reduction_result_2026-07-08.md
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5204_max_nearest_linear_reduction_test.py
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5204_linear_max_reduction_final2_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_goal5204_linear_max_reduction_final3_graphics_dragon_happy_buddha_2026-07-08.json
```

## Reviewer Questions

1. Does `max_nearest_distance_witness_numpy_columns(...)` preserve the existing
   semantics: maximum nearest distance, then smallest group/source index, then
   smallest item id?
2. Does the finite-distance path avoid full-array lexsort and sort only the
   maximum-distance tie set?
3. Does the non-finite fallback preserve the old full-lexsort behavior?
4. Do tests cover unique maximum, tied maximum, non-finite fallback, app-neutral
   source window, and X-HD route metadata surfacing?
5. Do full-public POD artifacts still match the Goal5186 author HDResult?
6. Do the artifacts self-report `max_reduction_strategy =
   finite_max_then_tie_lexsort` and `max_tie_candidate_count = 1`?
7. Is the claimed movement (`max_nearest_reduction ~=0.072s ->
   ~=0.0007-0.0008s`, route wall `~=1.238s -> ~=1.17-1.18s`) supported by the
   artifacts?
8. Does the result avoid claiming exact paper dataset reproduction, full paper
   reproduction, author performance parity, or author-vs-RTDL performance
   ratio?
9. Is this a generic RTDL reducer optimization rather than an X-HD-specific
   primitive?
10. Should Goal5204 close as:

```text
completed_linear_max_nearest_reduction__small_generic_reducer_floor_removed
```

Expected answer shape:

```text
Verdict:
Blocking findings:
Required amendments:
Non-blocking notes:
Answers to the 10 questions:
```
