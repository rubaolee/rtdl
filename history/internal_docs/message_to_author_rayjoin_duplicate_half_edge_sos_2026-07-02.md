Subject: RayJoin Section 5.7 PIP determinism: same-height / same-slope duplicate half-edge rule?

Hi Liang,

We have made progress reproducing RayJoin Section 5.7 and found a narrower determinism issue than the earlier equal-height / different-slope case.

Your previous clarification and patch for encoding the slope tie-break into `t_reported` makes sense and fixes the case where multiple boundary candidates have the same vertical intersection height but different slopes. We implemented the same idea in RTDL: the preferred slope reports a slightly smaller `t_reported`, so OptiX pruning does not discard the intended candidate before the shader can compare it.

The remaining case we are seeing is more specific:

- the query ray intersects two candidates at the same vertical height;
- the two candidates have the same scaled line coefficients `(a, b, c)`;
- they are opposite directed half-edges of the same geometric boundary;
- therefore they also have the same slope, so the slope-based `t_reported` perturbation gives them the same reported distance;
- the two half-edges map to different adjacent faces, so choosing one versus the other changes exterior/interior classification and can change polygon-overlay output chains.

Concrete Block x Water example:

Query point from map0:

```text
point_index = 5693875
point = (-121.74681801, 36.808320909)
scaled = (1605107877856, -21527854960909)
```

The nearest same-line duplicate candidates in map1 are:

```text
edge_index=827259, segment_id=827260
left_face_id=17144, right_face_id=0
direction: reverse-x
scaled line: a=-3378081565, b=2348568130, c=55940535548092058999995
face_by_direction=17144

edge_index=828109, segment_id=828110
left_face_id=17160, right_face_id=0
direction: forward-x
scaled line: a=-3378081565, b=2348568130, c=55940535548092058999995
face_by_direction=0
```

Both have identical `(a, b, c)` and identical slope. In this situation, the existing slope-based SoS perturbation cannot distinguish them.

The AuthorPatch output contains this coordinate in kept output chains:

```text
2540635 2 2528349 2528350 180035 179975
-121.746176 36.810027
-121.746818 36.808321
2540636 2 2528350 2528351 180035 179975
-121.746818 36.808321
-121.747041 36.807702
```

We also built a small RTDL micro-probe with just two duplicate half-edges on the same line. If we only change the input order of the two half-edges, the selected face/segment changes. That suggests this remaining case is not governed by a visible mathematical rule in the current comparator; it is effectively controlled by primitive/source order or OptiX traversal order after all explicit tie-breakers are exhausted.

Our questions:

1. Is this same-height / same-slope / duplicate-half-edge case expected in the RayJoin data model?
2. Does RayJoin have an intended Simulation-of-Simplicity rule for choosing between opposite directed half-edges that represent the same geometric boundary?
3. If yes, should the rule be encoded into `t_reported` as an additional deterministic perturbation after the slope term, so that OptiX pruning cannot decide it by traversal order?
4. What should the rule be? For example, should it depend on query map id, half-edge orientation, source edge id, face id, exterior-vs-interior side, or a canonical topology-side convention?
5. If the original code relies on stable BVH/source traversal order for this exact duplicate case, is that considered part of the RayJoin contract, or should a deterministic second-order SoS rule be added?

For clarity, we are not trying to introduce a RayJoin-specific shortcut in RTDL. We want the generic directed planar-map point-location contract to match the intended RayJoin semantics, and if you provide a duplicate-half-edge rule or patch, we can implement the same rule on both sides and compare against an updated AuthorPatch baseline.

Thanks,
Rubao
