# v1.1 OptiX/Embree Status

This page summarizes the current `main` post-v1.0 OptiX/Embree evidence. It is
not a new release package and does not move the `v1.0` tag.

v1.1, v1.2, v1.3, and v1.4 are internal engineering milestones only. Do not
create public release packages, release gates, or tags for those milestones;
the next planned public release line is v1.5 unless the roadmap is explicitly
changed.

## Current Decision

| App row | v1.1 status | Public boundary |
| --- | --- | --- |
| `polygon_pair_overlap_area_rows` | accepted bounded positive OptiX candidate | RT-assisted LSI/PIP positive candidate discovery plus native C++ exact area continuation only |
| `database_analytics` | execution-unblocked, still mixed | compact-summary DB path only; no SQL, DBMS, full dashboard, row materialization, or broad DB speedup claim |
| `graph_analytics` | correctness-ready; Goal1267 confirms packed-ray OptiX traversal is extremely fast, but total path is scene-preparation dominated and mixed versus Embree | bounded visibility any-hit path only; no graph database, BFS system, triangle analytics, or whole graph speedup claim |
| `polygon_set_jaccard` | correctness-ready at chunk `1024`, still slower | chunked native-assisted candidate discovery plus native exact continuation only |

## How To Read Slower OptiX Rows

Embree is the same-contract CPU RT/BVH baseline for these app rows, not a plain
Python fallback. A slower OptiX result can still be useful v1.1/v1.2 evidence
when correctness is clean and the bottleneck is explained.

Use `optix_still_slower_with_reason` for rows where OptiX remains slower than
Embree but the cause is identified, such as host input construction,
scene/ray prepare, ray packing, Python materialization, or non-RT continuation.
That outcome is valid engineering evidence and v1.5/v2.0 design input, but it
does not authorize positive public RTX speedup wording.

Current v1.2 `main` uses the direct packed-ray graph visibility path. Goal1267
pod timing confirmed the intended packed metadata (`all_numpy_packed_rays` and
`all_numpy_packed_triangles`) and showed the OptiX any-hit query itself around
`0.0002s` at the tested 30k/60k-copy scales. The remaining bottleneck is
OptiX scene preparation plus host-side preparation, so the next graph work is
prepared-scene reuse or amortization, not any-hit kernel micro-optimization.

## Allowed Polygon-Pair Wording

RTDL v1.1 shows bounded OptiX acceleration for
`polygon_pair_overlap_area_rows` on an RTX A5000 at 40k, 80k, and 160k copies.
The measured path is RT-assisted LSI/PIP positive candidate discovery plus
native C++ exact area continuation. At 160k copies, OptiX measured about `1.4x`
faster candidate discovery and about `1.2x` faster observed pipeline than
Embree under the reviewed same-contract benchmark.

Correctness is confirmed by summary parity under the current v1.1 profiler
contract. `candidate_count_matches_expected: false` remains an unresolved
diagnostic boundary and a tracked v1.2 reconciliation item.

## Blocked Wording

Do not describe this as:

- monolithic GPU polygon overlay;
- broad GIS acceleration;
- whole-app polygon overlap speedup;
- general OptiX speedup for RTDL;
- speedup evidence for database, graph, or Jaccard workloads.

## Evidence Trail

- [Goal1262 v1.1 patched full matrix intake](reports/goal1262_v1_1_patched_full_matrix_intake_2026-05-04.md)
- [Goal1263 polygon-pair scale sweep intake](reports/goal1263_polygon_pair_scale_sweep_intake_2026-05-04.md)
- [Goal1263 three-AI consensus](reports/goal1263_three_ai_consensus_polygon_pair_v1_1_2026-05-04.md)
- [Goal1264 DB/graph scale probe intake](reports/goal1264_db_graph_scale_probe_intake_2026-05-04.md)
- [Goal1267 v1.2 targeted OptiX pod intake](reports/goal1267_v1_2_targeted_optix_pod_intake_2026-05-05.md)
- [Goal1268 Embree 3/4 flexible runtime](reports/goal1268_embree3_4_flexible_runtime_2026-05-05.md)

## Next Work

v1.2 should focus on internal NVIDIA OptiX performance work. v1.5 should replace
app-specific native paths with reviewed generic traversal-plus-reduction
primitives. Vulkan, HIPRT, and Apple RT remain existing proof surfaces and are
not active implementation targets before v2.1.
