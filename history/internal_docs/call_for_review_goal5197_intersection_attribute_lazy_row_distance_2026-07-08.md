# Call For Review - Goal5197 Intersection Attribute And Lazy Row Distance

Please strictly review Goal5197:

```text
history/internal_docs/goal5197_intersection_attribute_lazy_row_distance_result_2026-07-08.md
```

Relevant implementation:

```text
src/native/optix/rtdl_optix_workloads.cpp
src/rtdsl/optix_runtime.py
src/rtdsl/partner_continuations.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py
Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py
tests/goal5197_intersection_attribute_lazy_row_distance_test.py
```

Relevant artifacts:

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_intersection_attribute_lazy_row_distance_goal5197_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_intersection_attribute_lazy_row_distance_final2_goal5197_graphics_dragon_happy_buddha_2026-07-08.json
Paper-reproduction-apps/x-hd-paper/results/xhd_full_public_all_source_intersection_attribute_lazy_row_distance_final3_goal5197_graphics_dragon_happy_buddha_2026-07-08.json
```

## Context

Goal5197 is a native OptiX micro-optimization / cleanup. The intersection
program already computes `min_sq` for pruning. The any-hit program previously
recomputed `min_sq`, then computed row-only distance values even on the
inline-nearest path where no row is emitted. Goal5197 carries `min_sq` through
OptiX intersection attributes and computes row-only values lazily.

This should be reviewed as generic cell-MBR traversal behavior. It is not an
X-HD-specific shortcut and not a performance headline.

## Review Questions

1. Does the intersection program correctly report `min_sq` as two 32-bit OptiX
   attributes?
2. Does the any-hit program reconstruct `min_sq` from `optixGetAttribute_0/1`
   rather than recomputing `min_distance_sq(query, cell)`?
3. Does the any-hit program still preserve payload-current-best pruning and
   lower-id tie-break semantics?
4. Are `max_distance_sq` and row min-distance now computed only on the row
   output path?
5. Does the implementation remain app-neutral in RTDL core and avoid X-HD /
   paper / author identity?
6. Are the tests sufficient as structural guards, given the runtime behavior is
   validated by POD route gates?
7. Does the POD evidence show the full-public Level-B route still matches the
   author HDResult?
8. Is it correct to treat the first route after rebuild as cold/noisy and not
   use it as the performance comparison?
9. Is the performance interpretation honest: warm route remains about
   `2.25-2.28s`, with no decisive speedup over Goal5196?
10. Are the claim boundaries correct: no author-vs-RTDL ratio, no exact paper
    dataset reproduction, no full X-HD paper reproduction, and no strong speedup
    claim over Goal5196?
11. Should Goal5197 close as `implemented_review_pending` with verdict
    `intersection_attribute_lazy_row_distance_approved_or_neutral`, or are
    amendments required?

## Expected Answer Shape

```text
Verdict: <label>

Blocking findings:
- ...

Required amendments:
- ...

Non-blocking notes:
- ...

Answers:
1. ...
...
11. ...
```
