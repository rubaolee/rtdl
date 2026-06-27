# Goal4382 v2.14 Benchmark-App Cross Audit

Date: 2026-06-14

## Conclusion

The RTNN lesson generalizes. v2.14 has many same-contract, human-scale timing rows, but human-scale timing is not the same thing as large or paper-faithful data. Several rows are technically useful prepared-phase comparisons but are not yet strong public benchmark-app claims.

The strongest current rows are RTNN after Goal4381, RayDB-style grouped reduction, RayJoin LSI, robot-collision traversal, triangle-counting any-hit, Barnes-Hut fixed-depth node coverage, and Librts AABB-index as RT primitive rows. RTDBSCAN improved after Goal4383 by removing the Embree threshold-row materialization blocker, but its full-app speedup remains continuation-dominated. The weakest public-readiness dimension is data scale/provenance: several rows still use small synthetic inputs repeated many times. That is acceptable for engineering regression tests, but not enough for high-confidence public performance wording.

## Gate Definitions

RT-core optimization asks: does the OptiX row use the best-known RTDL route for the app contract, avoiding avoidable host materialization, query rebuilds, and stale primitive paths?

Embree fairness asks: does the CPU row use the best-known Embree route under the same contract, with an explicit thread policy and no avoidable row/materialization handicap?

Data scale/provenance asks: is the benchmark run on large data or original paper/application data, not merely a small synthetic fixture repeated to accumulate seconds?

Statuses:

- GREEN: good enough for row-scoped review wording.
- YELLOW: useful engineering evidence, but needs follow-up before strong public wording.
- RED: not public-ready for the stated dimension.

## Audit Matrix

| Row | RT-core optimization | Embree optimization/fairness | Data scale/provenance | Public-value verdict | Required next action |
| --- | --- | --- | --- | --- | --- |
| `hausdorff_xhd_threshold` | GREEN: prepared directed-threshold count route, compact scalar output. | GREEN: same prepared threshold route, 64-thread Embree selected. | GREEN/YELLOW after Goal4383: rerun at 65,536, 262,144, and 1,048,576 points per side; large synthetic tiled point sets with oracle-checked threshold decision, not exact X-HD paper data. | Strong large prepared-threshold decision row; not an exact Hausdorff witness-distance app claim. | Keep public wording as `Hausdorff <= r` threshold decision only; exact witness path and X-HD paper data remain follow-up. |
| `spatial_rayjoin_lsi` | GREEN: prepared scalar-count LSI route avoids intersection-row materialization. | GREEN: prepared Embree scalar-count route, thread sweep measured. | YELLOW: real/public CDB-derived subset, but not the complete paper LSI suite. | Good row-scoped primitive claim; paper-reproduction claim remains blocked. | Run full RayJoin LSI datasets and keep author-code comparison separate. |
| `spatial_rayjoin_pip` | YELLOW: prepared PIP scalar count is optimized for the current route, but the RayJoin-specialized CDB closest-hit face-id path remains the higher bar for paper parity. | GREEN: prepared Embree scalar route is same-count contract. | YELLOW: real/public CDB-derived subset, but not full paper PIP coverage. | Modest 1.10x is plausible; wording must stay narrow. | Add/measure the CDB closest-hit face-id point-location route against full PIP datasets. |
| `spatial_rayjoin_overlay` | YELLOW: OptiX path works, but fused/specialized overlay point-location and output assembly remain optimization debt. | YELLOW: Embree path works, but overlay uses app orchestration and only 2/8 exact-ready pairs. | YELLOW: the available exact CDB subset is 2/8; six paper pairs are unavailable in the current public/pod artifact set. | Public-review-ready for the available 2/8 exact subset. No full 8/8 Section 5.7 wording. | Keep the 2/8 subset wording explicit; if the unavailable 6/8 exact inputs appear later, rerun the full matrix with author/RTDL timing basis separated. |
| `rt_dbscan_core_flags_numba_signature` | GREEN: OptiX uses prepared fixed-radius count-threshold device columns plus the fixed Numba continuation. | YELLOW/GREEN after Goal4383: Embree now uses a generic prepared 3D fixed-radius count-threshold compact-row route with no neighbor-row materialization or timed scene rebuild; CPU host rows plus measured upload remain explicit. | YELLOW: validated at 4,096 clustered synthetic points and rerun up to 524,288 synthetic points; still not RTDBSCAN paper data. | Fairer same-continuation engineering row; total speedup is small because shared Numba continuation dominates large runs. | Keep narrow wording, or add a fused/device-side component-continuation primitive before making a stronger full-app speedup claim. |
| `robot_collision_grouped_segment_flags` | GREEN after Goal4383: prepared-buffer same-contract row now reports both total hot run and traversal phases at large scale; OptiX traversal remains much faster while total includes shared host output work. | GREEN: same prepared-buffer grouped-segment any-hit flags contract, 64-thread Embree selected. | GREEN/YELLOW after Goal4383: scaled to 262,144 poses, 1,048,576 groups, 9,437,184 query segments, and 16,384 static triangles; large synthetic robot-like fixture, not original robotics paper data. | Strong large prepared-primitive row; not continuous collision or planner acceleration. | Keep wording as discrete sampled grouped-segment any-hit flags; native device-buffer OptiX route can be reported separately but not mixed into Embree fairness table. |
| `contact_manifold_aabb_collect_k` | GREEN after Goal4383: generic AABB-index candidate discovery plus bounded witness-row collection are compact and prepared. | GREEN: same broadphase and bounded-row contracts, 64-thread Embree selected. | GREEN/YELLOW after Goal4383: scaled to `jittered_grid_65536`, 4,294,967,296 possible pairs, and 65,536 validated witness rows; large deterministic jittered synthetic data, not app-derived contact data. | Reasonable large broadphase/contact-witness primitive claim; not a full contact-manifold solver. | Keep wording as AABB broadphase plus bounded contact-witness rows; add app-derived physics/contact data before stronger contact-manifold wording. |
| `raydb_style_grouped_i64_count` | GREEN: prepared ray batch is resident, grouped reduction avoids hit-stream materialization. | GREEN: same grouped reduction contract, 64-thread Embree selected. | GREEN/YELLOW: 262,144 rows, 884,736 rays is large enough; generated RayDB-style data is not yet proven paper-original. | Strong row-scoped RT primitive claim. | Add original RayDB workload/data comparison if available; otherwise label as RayDB-style generated large input. |
| `barnes_hut_node_coverage` | GREEN after Goal4383: prepared node-coverage threshold decision now supports fixed-depth quadtree-cell node fixtures and keeps compact scalar output. | GREEN: same prepared node-coverage route, 64-thread Embree selected. | GREEN/YELLOW after Goal4383: validated at 4,096 bodies x 4,096 nodes and rerun at 1,000,000 bodies x 65,536 nodes; large but synthetic fixed-depth cells, not full RT-BarnesHut paper data. | Strong large prepared-primitive row; still not a force-solver or whole Barnes-Hut claim. | Keep wording strictly as node-coverage traversal; app-level force/opening-rule acceleration remains v3.0 work. |
| `librts_spatial_index_aabb` | GREEN: prepared AABB-index all-ops route is very fast and compact. | GREEN after Goal4383: same all-ops contract, 64-thread Embree selected, fp32 envelope predicate aligned with OptiX/authors-code counts. | GREEN/YELLOW after Goal4383: 100K and 1M boxes x 1K queries on paper-like uniform data, `paper_equivalent_dataset=false`; large but not exact paper artifact data. | Strong row-scoped prepared hot-query primitive claim; cold total and exact-paper reproduction must be stated separately. | Keep hot-query and cold-total wording separate; exact LibRTS paper artifact/authors-code timing remains follow-up. |
| `rtnn_ranked_summary` | GREEN after Goal4381: native aggregate, prepared-query graph, same-stream CuPy best path measured separately. | GREEN after Goal4381: Embree native aggregate avoids summary-row/Python materialization. | GREEN/YELLOW: 1M uniform and 262K shell large inputs; exact RTNN paper datasets still absent. | Strong large RTNN-shaped row; no paper-dataset claim. | Acquire KITTI/Stanford/N-body paper-family data and rerun; keep exact float64 and float32 best rows separate. |
| `triangle_counting_any_hit` | GREEN after Goal4383: prepared weighted any-hit summary avoids hit-row output and now scales to 1,048,576 rays. | GREEN: same weighted any-hit summary contract, 64-thread Embree selected. | GREEN/YELLOW after Goal4383: 524,288 synthetic RT-Graph fixture copies, 1,048,576 rays, 2,621,440 triangles; large but not exact paper dataset. | Strong large prepared-primitive row; full RT-Graph paper reproduction remains out of scope. | Keep hot-query and total wording separate; exact paper datasets/authors-code timing remain follow-up. |

## Overall Answers

1. RT-core performance is not uniformly "done." Several rows are optimized enough for their current primitive contract, but RTDBSCAN, RayJoin overlay/PIP, robot full-loop residency, and Barnes-Hut app-level force work still have visible optimization debt.

2. Embree fairness is better than before, but not perfect. Goal4383 fixed the biggest RTDBSCAN unfairness by replacing Embree threshold-row materialization with a generic prepared 3D fixed-radius count-threshold compact-row route. RTNN was fixed by adding native Embree aggregate; the same pattern should continue to be reused for any other row that still aggregates through avoidable rows.

3. Data scale/provenance is the weakest dimension. RTNN is now large; RayDB is large; Hausdorff threshold is now large at 1,048,576 points per side; robot collision is now large at 9,437,184 query segments; LibRTS AABB is now large on paper-like uniform fixtures; triangle counting is now large on synthetic RT-Graph-shaped fixtures; Barnes-Hut node coverage is now large on synthetic fixed-depth quadtree cells; contact is now large at 4,294,967,296 possible pairs on deterministic jittered synthetic data. Many other rows still rely on small synthetic inputs repeated many times. Repeats make timing stable, but they do not turn a small fixture into a public benchmark dataset.

## Closeout Rule For v2.14

Rows with GREEN/GREEN/YELLOW can remain in v2.14 as row-scoped prepared-phase evidence if the wording is narrow. For RayJoin overlay, the 2/8 available exact subset is allowed as public-review evidence; the full 8/8 Section 5.7 matrix remains blocked until unavailable exact inputs exist.

The v2.14 release should not claim "all benchmark apps are fully optimized and paper-scale." The honest claim is:

> v2.14 contains fresh row-scoped RTDL OptiX-vs-Embree evidence with explicit contracts and phase explanations. Several rows are public-review-ready as prepared primitive comparisons; app-scale and paper-dataset claims require the listed v2.14 cleanup reruns.
