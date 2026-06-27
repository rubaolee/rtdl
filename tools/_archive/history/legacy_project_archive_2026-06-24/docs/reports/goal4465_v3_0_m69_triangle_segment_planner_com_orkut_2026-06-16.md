# Goal4465 V3.0 M69 Triangle Segment Planner Optimization

Goal4465 removes a real app-partner planning debt from the Triangle Counting
segmented RT-2A1 route.

Problem: Goal4464 made `com-orkut` correct and scalable, but the source/ray
planner still spent `28.885s` in `build_geometry` on the RTX 4000 Ada pod. The
hot path was `_segment_edge_ranges_from_counts`, which walked every directed
edge count in Python. On `com-orkut`, that means `117,117,316` Python-loop
iterations just to produce `1,744` ray segments.

Change: `_segment_edge_ranges_from_counts` now converts counts to a NumPy
array, builds an `int64` prefix sum, and uses `np.searchsorted` to jump from one
segment boundary to the next. The Python loop is now proportional to segment
count rather than directed-edge count. This is app/partner planning logic only;
the RTDL engine still receives generic prepared triangle scenes, generic rays,
and a weighted any-hit summary.

## Evidence

Planning-only measurement on `com-orkut`, 2M directed-edge scene cap and 5M
two-hop ray cap:

| Metric | Goal4464 | Goal4465 |
| --- | ---: | ---: |
| Planner/build_geometry time | 28.885s | 3.665s median |
| Planner speedup | 1.00x | 7.88x |
| Count download median | n/a | 0.175s |
| Source-range scenes | 59 | 59 |
| Ray segments | 1,744 | 1,744 |
| Directed-edge triangles | 117,117,316 | 117,117,316 |
| Logical duplicate rays | 8,579,930,671 | 8,579,930,671 |

In short, M69 reduces the `com-orkut` planner from 28.885s to 3.665s while
preserving the same segmentation and result.

Full app phase context:

| Metric | Goal4464 formal phase | Goal4465 probe |
| --- | ---: | ---: |
| Build contract | 3.889s | 3.902s |
| Build geometry / plan segments | 28.885s | 4.288s |
| Prepare scenes | 0.713s median | 1.208s |
| Duplicate-ray build | 6.752s median | 6.725s |
| RT query traversal | 19.013s median | 19.032s |
| Observed triangles | 627,584,181 | 627,584,181 |

The result is exactly what we wanted: a large avoidable Python planning cost is
gone. The M69 full-app probe itself took `35.409s` wall time with warmup 0 and
repeat 1. The remaining heavy phases are now more visible: duplicate-ray
construction, RT traversal over 8.58B logical rays, and comparison against
cuGraph/authors/Numba under one explicit timing contract.

## Claim Boundary

Allowed:

- Internal RTDL app-route optimization wording for the segmented RT-2A1
  `com-orkut` path.
- The planner optimization is app/partner-side and does not add graph-specific
  native engine logic.
- The route remains exact on the largest paper row.

Blocked:

- Public triangle-count RT-core speedup wording.
- RTDL beats cuGraph wording.
- RTDL beats authors-code wording.
- Paper-system reproduction wording.
- Automatic partner selection.

## Evidence Files

- `docs/reports/goal4465_v3_0_m69_triangle_segment_planner_com_orkut_2026-06-16.json`
- `docs/reports/goal4465_v3_0_m69_triangle_segmented_scene_com_orkut_probe_2026-06-16.json`
- `docs/reports/goal4464_v3_0_m68_triangle_segmented_scene_com_orkut_2026-06-16.json`
