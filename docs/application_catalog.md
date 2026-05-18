# RTDL Application Catalog

This is the v2.0-facing catalog of runnable RTDL application examples. It keeps
normal users focused on the current architecture: Python application code around
RTDL kernels, with optional partner-owned columns for supported paths.

Older app/version evidence belongs in
[Learner Doc Version Notes](history/learner_doc_version_notes.md)
and the report archive.

Archived scenario-specific DB and Apple RT helpers remain in the repository for
compatibility and audit tests, but users should start from the unified Apple and
database app wrappers listed below.

## Reading Rule

Each app below has two boundaries:

- what RTDL owns;
- what remains Python, partner, or domain-library work.

Do not turn an app row into a broad speedup claim unless the exact backend,
partner, hardware, command shape, output contract, and artifact are cited.

## Beginner Examples

| Example | File | What it teaches |
| --- | --- | --- |
| Hello world | `examples/rtdl_hello_world.py` | source-tree import and first output |
| Backend hello world | `examples/rtdl_hello_world_backends.py` | same app idea through selected runtime backends |
| Feature cookbook | `examples/rtdl_feature_quickstart_cookbook.py` | compact recipe per public feature |
| Partner any-hit | `examples/rtdl_partner_anyhit.py` | first partner-owned column path |

## Spatial And Geometry Apps

| App | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Segment/polygon hit count | `examples/rtdl_segment_polygon_hitcount.py` | candidate traversal and compact counts | not a full GIS engine |
| Segment/polygon any-hit rows | `examples/rtdl_segment_polygon_anyhit_rows.py` | exact witness pairs or streaming witness columns where supported | full Python row tables are convenience output, not the fast v2 shape |
| Polygon pair overlap rows | `examples/rtdl_polygon_pair_overlap_area_rows.py` | bounded candidate discovery and summary contracts | not arbitrary polygon overlay |
| Polygon set Jaccard | `examples/rtdl_polygon_set_jaccard.py` | bounded candidate discovery and summary contracts | not a general GIS/Jaccard engine |
| Road hazard screening | `examples/rtdl_road_hazard_screening.py` | segment/polygon candidate and priority summaries | no routing or road-network system claim |
| Continuous Frechet distance | `examples/rtdl_continuous_frechet_distance_app.py` | broadphase free-space candidate discovery | Python owns the Frechet decision/search algorithm |

## Proximity And Search Apps

| App | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Service coverage gaps | `examples/rtdl_service_coverage_gaps.py` | fixed-radius coverage counts/rows | not a service-optimization product |
| Event hotspot screening | `examples/rtdl_event_hotspot_screening.py` | fixed-radius density counts/rows | not a full analytics pipeline |
| Facility KNN assignment | `examples/rtdl_facility_knn_assignment.py` | KNN or threshold coverage rows | richer assignment policies remain app code |
| Hausdorff distance | `examples/rtdl_hausdorff_distance_app.py` | nearest-candidate rows or threshold summaries | exact rich witness extraction is app/partner work unless documented |
| ANN candidate search | `examples/rtdl_ann_candidate_app.py` | candidate-subset reranking and coverage summaries | not a general ANN index |
| Outlier detection | `examples/rtdl_outlier_detection_app.py` | radius density rows/counts | final anomaly policy is Python/app code |
| DBSCAN clustering | `examples/rtdl_dbscan_clustering_app.py` | core-count/core-flag primitives | cluster expansion remains app/partner graph work |

## Analytical, Graph, And Simulation Apps

| App | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Database analytics | `examples/rtdl_database_analytics_app.py` | bounded columnar scan/group summaries | not SQL or a DBMS |
| Graph analytics | `examples/rtdl_graph_analytics_app.py` | frontier/edge and triangle-style rows/summaries | not a graph database |
| Robot collision screening | `examples/rtdl_robot_collision_screening_app.py` | any-hit pose flags/counts | not a planner or physics simulator |
| Barnes-Hut force approximation | `examples/rtdl_barnes_hut_force_app.py` | node/body candidate discovery and coverage summaries | force-vector reduction remains app/partner work unless documented |

## Visual Demos

| Demo | File | RTDL role | Boundary |
| --- | --- | --- | --- |
| Hidden star visual demo | `examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py` | ray/triangle query core | RTDL is not a renderer |
| Lit ball demo | `examples/visual_demo/rtdl_lit_ball_demo.py` | query core inside Python presentation | Python owns rendering/presentation |

## v2.0 Output Guidance

For performance-oriented v2.0 apps, prefer compact or partner-owned outputs:

- flags instead of full witness rows when only yes/no is needed;
- counts instead of pair tables when only totals are needed;
- streaming witness columns instead of Python dictionaries for large witness
  output;
- partner-owned arrays when the next computation will run in PyTorch or CuPy.

Use Python row dictionaries when clarity or inspection matters more than
throughput.

## Read Next

- [App And Example Quickstart](app_example_quickstart.md)
- [Partner Acceleration Boundaries](partner_acceleration_boundaries.md)
- [App Engine Support Matrix](app_engine_support_matrix.md)
- [v2.0 Release Package](release_reports/v2_0/README.md)
