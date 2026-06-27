# Goal 499: External Review — Paper Workload Classifications
Date: 2026-04-16
Reviewer: Claude (claude-sonnet-4-6)

## Verdict: ACCEPT

The workload classifications and RTDL/Python splits are technically sound. The
recommended next-release set and deferral of Juno are well-reasoned.

---

## Per-Workload Findings

### X-HD Hausdorff Distance — ACCEPT, low risk

The RTDL/Python split is correct. Directed Hausdorff distance is structurally a
nearest-neighbor scan followed by a scalar max reduction. RTDL owning the spatial
search and emitting `(point_id, neighbor_id, distance)` rows, with Python calling
`max()` over those rows, is an architecturally clean decomposition.

The distinction between *expressiveness feasibility* (doable now with existing
nearest-neighbor rows) and *performance faithfulness* (needs prepared dataset
reuse and HD pruning primitives) is accurate and honest.

Minor note: for very large point sets, Python-side `max()` over millions of rows
may be a secondary bottleneck worth calling out in the app example, but it is not
a language gap.

### Juno High-Dimensional ANN — ACCEPT deferral

The not-feasible classification is correct. Current RTDL is strongest on 2D/3D
spatial geometry; IVF/PQ requires high-dimensional vector types, product
quantization data models, and subspace codebook primitives that do not exist in
the language. The gap is an expressiveness gap, not a performance gap, so a toy
demo would not be faithful to the paper's contribution. Keeping Juno as a
roadmap/research item is the right call.

### RT-BarnesHut — ACCEPT with risk note

The simplified app split (Python builds and owns the tree, RTDL emits accepted
candidate/contribution rows, Python integrates timesteps) is technically correct.
The identified missing primitives (`TreeNodes2D/3D`, `barnes_hut_accept(theta=)`,
force-contribution rows) are accurate.

**Risk note:** the "medium-risk" label may be slightly optimistic. The core
Barnes-Hut contribution is that *internal* tree nodes (not just leaves) can
accept and contribute approximate forces under the opening criterion. This
requires RTDL to support heterogeneous geometry (internal nodes vs leaf nodes)
with a predicate that gates contribution, which is a non-trivial language
addition. The report acknowledges this correctly in the missing-additions list
but the risk label should be understood as medium/high, not pure medium.

The two-phase plan (start simplified, grow language only after app correctness is
proven) is the right mitigation.

### RT Collision Detection (DCD/CCD) — ACCEPT

The DCD/CCD split is the correct one. Discrete-pose collision screening using
ray/triangle rows fits the existing RTDL spatial query pattern cleanly. Python
owning forward kinematics, pose/path batch construction, and bidirectional
checking policy is appropriate — those are orchestration concerns, not kernel
concerns.

Deferring continuous CCD until RTDL has sphere/curve/swept-volume primitives is
correct; doing CCD without those primitives would require RTDL to be bypassed
entirely, which defeats the purpose of the app.

The identified gap (`ray_triangle_anyhit_rows` vs hit counts, batch pose/link
IDs) is precise and actionable.

---

## Cross-Cutting Notes

**Feasibility claims depend on unverified current-API assertions.** The report
asserts that RTDL currently has `fixed_radius_neighbors` and `knn_rows`. These
claims are central to the X-HD and RT-DCD feasibility conclusions. Before
committing the roadmap, verify these names against the actual public RTDL API
surface. If the names differ or the semantics are narrower, the bounded-app
feasibility for those two workloads may need qualification.

**Language growth rule is sound.** The rule (prefer emitted rows over hidden
system behavior, keep orchestration in Python, add reusable types only after
multi-app proof) is a principled constraint that will prevent paper-specific
one-off primitives from accumulating.

**Recommended next-release order is correct:** X-HD first (lowest risk, proves
the spatial-metric app pattern), RT-DCD second (proves batched geometry query),
RT-BarnesHut third (proves hierarchical contribution rows). Juno deferred.

---

## Summary

| Workload | Classification verdict | RTDL/Python split verdict |
|---|---|---|
| X-HD Hausdorff | Correct | Correct |
| Juno ANN | Correct (defer) | Correct |
| RT-BarnesHut | Correct, risk slightly underweighted | Correct |
| RT-DCD/CCD | Correct | Correct |

No blocking issues. One pre-commitment action item: verify that `fixed_radius_neighbors`
and `knn_rows` exist in the current public RTDL API before publishing feasibility
commitments for X-HD and RT-DCD.
