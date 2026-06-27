# Goal 519 Review: RT Workload Universe Roadmap

Reviewer: Claude Sonnet 4.6  
Date: 2026-04-17  
Source report: `docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md`  
Paper: arXiv 2603.28771v1 — *Ray Tracing Cores for General-Purpose Computing: A Literature Review*

---

## Verdict: PASS — Correct and Honest Roadmap

---

## Workload Coverage Check

The paper's Table 3 lists 35 rows across 32 distinct problems (Range Queries, Point Queries, and Particle Transport each appear twice with different citations). The report correctly states "32 distinct non-graphics RT-core problems" and accounts for all 32 in its roadmap table.

Cross-check — all 32 paper workloads present in the report:

| Paper workload | Present in report |
| --- | --- |
| Penetration Depth | yes |
| SpMM | yes |
| BFS | yes |
| Triangle Counting | yes |
| Set Intersection | yes |
| Binary Search | yes |
| Point Queries | yes |
| Range Queries | yes |
| Barnes-Hut | yes |
| Discrete CD | yes (Discrete Collision Detection) |
| Continuous CD | yes (Continuous Collision Detection) |
| RMQ | yes |
| Line-Segment Intersection | yes |
| Point in Polygon | yes |
| Non-euclidean kNN | yes |
| ANN | yes |
| Outlier Detection | yes |
| Index Scan | yes |
| kNN | yes |
| Particle Simulation | yes |
| Radio Wave Propagation | yes |
| DBSCAN | yes |
| Point Location | yes |
| FRNN | yes |
| Particle Tracking | yes |
| Graph Drawing | yes |
| Space Skipping | yes |
| Segmentation | yes |
| Particle-Mesh Coupling | yes |
| Infrared Radiation | yes |
| Particle Transport | yes (single entry covers both citations) |
| Voxelization | yes |

No workload is missing. No workload is fabricated.

---

## Paper Takeaways Accuracy Check

Each of the report's "Paper Takeaways" is verified against the paper:

**"nearest neighbor search and proximity variants are the strongest broad family"**  
Confirmed. Paper abstract: "nearest neighbor search, including its variants, benefit the most from ray tracing cores." Table 3 shows kNN reaching 200× best speedup, FRNN and ANN also strong.

**"Heuristic/approximate workloads benefit because they reduce work"**  
Confirmed. Paper conclusions: "problems that can use heuristics to avoid performing unnecessary work" are the second major beneficiary class. Paper explicitly frames this as work reduction rather than raw hardware speed.

**"BVH pruning and work reduction are the best performance levers"**  
Confirmed. Paper: "discarding tree branches when traversing a tree to avoid unnecessary work" is cited as the biggest strength of RT cores.

**"Latency-bound graph-style workloads are weaker performance candidates"**  
Confirmed. Paper: "reducing memory accesses in BFS does not improve performance because of latency, and even building the BVH takes more time than traversal with CUDA cores. Also, BFS does not take advantage of the biggest strength of RT cores, to avoid work, as all nodes need to be visited." The report's "covered but performance-weak" status for BFS is accurate and well-supported.

**"Rigid RT-core model, lack of internal BVH-node access, FP32 geometry, 3D coordinate limits, and context switching are real limits"**  
Confirmed. Paper conclusions: "the rigidity of the ray tracing model and the focus of the implementation on rendering tasks restricting the generalization to other problems." Hardware modification papers (e.g., [5] Barnes et al. extending RT cores) are cited but excluded from scope, matching the report's out-of-scope boundary.

**"Higher-dimensional exact problems need bounded embeddings or approximations"**  
Confirmed. Paper future work section: "mapping higher dimensional problems to the ray tracing 3D scene; it would be interesting to see more development in this direction" — framed as underexplored, not solved.

---

## Roadmap Staging Accuracy Check

**Stage 1 (v0.9): Proximity and heuristic apps**  
Correctly prioritized. These are the paper's strongest performing category (kNN 200× best, ANN 8.5×, FRNN 10×, Outlier Detection 9.9×, DBSCAN 4×). The "start with ANN/Outlier/DBSCAN" immediate recommendation is well-supported by paper data and by current RTDL surface (existing `fixed_radius_neighbors` and `knn_rows`).

**Stage 2 (v1.0): Indexing and DB-style query apps**  
Reasonable. Paper covers Range Queries (85-94× best), Point Queries (7.6×), Index Scan (4.7×), RMQ (2.3×), Binary Search (2×). The lower performers (RMQ, Binary Search) are correctly treated as feasibility studies, not commitments.

**Stage 3 (v1.1): Collision and geometry apps**  
Reasonable. Penetration Depth (5.33×), Discrete CD (2.8×), Continuous CD (3.0×) have documented results. Continuous CD correctly noted as requiring swept-volume semantics beyond current RTDL.

**Stage 4 (v1.2): Simulation and wave/particle apps**  
Reasonable. These are direct/native RT mappings. Particle Transport (1.67×, 1.5×) and Particle-Mesh Coupling (1.47×) have more modest speedups, and the report does not overclaim.

**Stage 5: Support/infrastructure**  
Space Skipping, Segmentation, and Voxelization correctly identified as candidates that may be internal support infrastructure before public apps.

---

## Out-Of-Scope Boundaries Check

All five out-of-scope boundaries are well-reasoned and consistent with the paper:

- **Hardware modification**: Paper explicitly treats Barnes et al. [5] hardware extension work as outside scope; the report matches this.
- **Full systems**: Not a paper claim; this is correct RTDL scoping. No issue.
- **High-dimensional exact geometry**: Consistent with paper's "underexplored" framing of dimensionality reduction mappings.
- **Internal BVH-node programmability**: Paper confirms RT cores do not expose internal node hooks. The report's caveat that RTDL "must not claim the same capability as hypothetical hardware changes" is honest.
- **Performance-impossible claims**: BFS support for language completeness without performance guarantees is consistent with paper evidence (BFS worst case 0.4×, "improves" rating 1 out of 5).

---

## Minor Gaps (Not Blocking)

**Short-ray preference not documented**  
The paper explicitly states "many short-length rays should be preferred over a few large rays" as a design principle with performance implications. The report does not carry this forward as an RTDL design note. This is a usable implementation constraint that could inform future kernel design and documentation.

**Set Intersection worst case**  
Table 3 shows Set Intersection worst case of 0.4× (slower than baseline). The report marks it "partially covered" without noting performance risk. Worth flagging when the dedicated Set Intersection app is planned.

**SpMM worst case**  
SpMM worst case is 1.1× (barely breaks even). The report marks it "not yet" and calls it "possible but needs careful proof of value" — that hedging is appropriate, but the performance risk should be stated explicitly when it reaches roadmap planning.

---

## Summary

The GOAL519 report is factually accurate against the paper. Every workload from the paper's Table 3 is accounted for. No workload is fabricated. The performance characterizations and priority ordering of workload families match the paper's statistical findings. The out-of-scope boundaries are honest and grounded in paper-documented RT-core limitations. The staging order correctly places the strongest performers earliest. The immediate recommendation (ANN, Outlier Detection, DBSCAN) is the correct call given both paper evidence and current RTDL primitives.

The two minor gaps (short-ray design principle, Set Intersection / SpMM performance risk disclosure) are informational notes for future planning, not errors in the roadmap.

**Verdict: PASS.**
