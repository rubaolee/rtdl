# RTDL v2.14 Benchmark-App Phase Explanations

Status: final v2.14 closeout phase explanation packet for maintainer review.

Date: 2026-06-15

Every row in the comparison table needs a phase-level explanation. Rows without an explanation remain blocked from public wording.

| Row | Major phases | Explanation | Boundary |
| --- | --- | --- | --- |
| `rtnn_ranked_summary` | prepared search, fixed-radius ranked-summary aggregate, optional prepared-query graph replay, optional same-stream CuPy continuation | Exact OptiX rows are traversal/aggregate dominated after native aggregate removed Python summary materialization. The best graph+CuPy rows remove per-repeat query upload but use float32 and have boundary-level deltas. | no paper-dataset claim; do not mix exact float64 and best float32 rows |
| `rt_dbscan_core_flags_numba_signature` | Embree/OptiX threshold flags, host/device handoff, Numba prepared-grid continuation, signature reduction | Embree fairness is repaired by compact threshold output. At large scale the shared Numba continuation dominates, compressing total speedup to 1.05x even though OptiX threshold is faster. | no large full-app RTDBSCAN speedup claim |
| `spatial_rayjoin_lsi` | segment-pair prepare, traversal/count, avoided row materialization | Prepared scalar-count LSI is a good RT primitive fit because it avoids emitting intersection rows. | no full RayJoin reproduction claim |
| `spatial_rayjoin_pip` | shape/point prepare, traversal, scalar count | Current PIP scalar route is short and output-light; 1.10x is plausible and should be worded as modest. | CDB closest-hit face-id route deferred |
| `spatial_rayjoin_overlay` | author process wall, RTDL load/pack, LSI, vertex/midpoint point-location, PIP traversal, output orchestration | OptiX beats Embree on the 2 available exact-ready pairs. This is valid public-review evidence for the available exact subset, but author process wall is not hot-compute parity and the unavailable 6/8 pairs cannot be used for a full-matrix claim. | available 2/8 exact subset only; no full Section 5.7 reproduction |
| `raydb_style_grouped_i64_count` | ray/triangle prepare, traversal, grouped reduction, avoided hit-stream materialization | Prepared grouped reduction keeps the result compact and avoids shipping the whole hit stream. | generated/paper-shaped data only |
| `librts_spatial_index_aabb` | AABB scene prepare, point/range traversal, compact count outputs | Hot query is the correct RT-core comparison and is 13.39x faster at 1M boxes; cold total is smaller because scene build dominates one-shot runs. | hot-query/cold-total wording must stay separate |
| `triangle_counting_any_hit` | graph lowering, ray/triangle prepare, any-hit traversal, scalar weighted accumulation | Any-hit traversal is extremely RT-core friendly, but total time includes Python graph lowering and scene preparation. | no full RT-Graph paper claim |
| `barnes_hut_node_coverage` | body/node fixture build, prepared threshold query, scalar coverage decision | Node-coverage traversal sees a 2.06x hot-query gain at 1M bodies x 65,536 nodes. | not a force solver |
| `hausdorff_xhd_threshold` | point-set prepare, directed fixed-radius threshold queries, scalar decision | Threshold decision is compact and large enough for human-scale timing; exact nearest-witness Hausdorff is not measured. | threshold decision only |
| `robot_collision_grouped_segment_flags` | scene prepare, grouped segment traversal, compact flags, output postprocess | Traversal is 6.69x faster at xlarge, while total is 1.86x because shared output/postprocess remains visible. | not continuous collision or planner acceleration |
| `contact_manifold_aabb_collect_k` | AABB prepare, broadphase traversal, bounded-row collect, Python exact refinement | OptiX broadphase is 1.23x faster, but bounded rows and Python refinement compress the hot path to 1.16x. | not full contact-manifold physics |

## Blocking Rule

If a row cannot explain the observed direction using measured phases, remove it from public wording. The fix is instrumentation or route repair, not softer prose.
