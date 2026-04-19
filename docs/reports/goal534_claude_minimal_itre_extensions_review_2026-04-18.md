# Goal 534: Claude Review — Minimal ITRE Extensions Design Study

Date: 2026-04-18
Verdict: **ACCEPT**

## Verdict Summary

The report correctly reframes the rejected Goal 533 rendering brainstorm into
bounded, non-rendering ITRE extensions. Each candidate carries a concrete app
scenario section, an existing-workload impact table, a usefulness rating, and a
challenge rating. Rendering non-goals are named explicitly and excluded cleanly.
The report is ready to drive Goal A (any-hit contract) without revision.

## Per-Candidate Assessment

### Candidate 1: Bounded Any-Hit / Early-Exit Traversal

**App scenarios**: Concrete and non-rendering — robot collision screening,
LOS, sensor coverage, wireless/acoustic occlusion, broad-phase culling. Pass.

**Existing-app impact**: Impact table correctly identifies robot collision as
the highest-value existing app and explains why (over-computation in current
`ray_triangle_hit_count`). Other areas are correctly rated low or no impact.
Pass.

**Usefulness**: Rated high, justified by RT hardware fit and smallest-feature
argument. Pass.

**Challenge**: Rated medium with the right focus — the hard part is cross-backend
parity, not the user API. This is accurate. Pass.

**v0.8 boundary**: User API does not expose shader hooks. Output is still typed
rows. Python still owns decisions. Pass.

### Candidate 2: Line-Of-Sight / Visibility Rows

**App scenarios**: Concrete and non-rendering — robot perception, navigation,
RF/acoustic screening, security/camera planning, GIS viewshed lite. Pass.

**Existing-app impact**: Correctly identifies robot collision as overlapping
foundation. Correctly flags that visual demos must not become renderer features.
Pass.

**Usefulness**: Rated high. The clean "non-rendering, common, maps to RT"
argument is valid. Pass.

**Challenge**: Rated low-to-medium with appropriate caveats (self-intersection
epsilon, deterministic first-blocker ID). Recommendation to defer first-blocker
ID from initial release is correct. Pass.

**v0.8 boundary**: Framed explicitly as a standard-library workload, not a core
language construct. No rendering. Pass.

### Candidate 3: Multi-Hop Graph As Python-Orchestrated Multi-Stage ITRE

**App scenarios**: BFS beyond one hop, multi-hop reachability, influence
propagation, triangle/wedge exploration. Pass.

**Existing-app impact**: Correctly identifies graph BFS as the primary
beneficiary. DB workloads called possible future but not first target. Pass.

**Usefulness**: Rated medium-to-high. Honest that it makes RTDL more useful
without changing backend execution. Pass.

**Challenge**: Rated medium as Python orchestration, high as device recursion,
with device recursion correctly rejected. Pass.

**v0.8 boundary**: Python owns state tables, visited sets, stopping conditions,
and reductions. RTDL owns each per-step kernel. Explicitly aligned with v0.8
app-building contract. Pass.

### Candidate 4: Hierarchical Candidate Filtering

**App scenarios**: Barnes-Hut candidate filtering, broad-phase collision
culling, level-of-detail proximity queries, adaptive spatial search. Pass.

**Existing-app impact**: Correctly identifies Barnes-Hut as the strongest
pressure case and notes the existing app already documents the missing primitives.
Pass.

**Usefulness**: Rated high long-term but not first. Honest about the timing.
Pass.

**Challenge**: Rated high with well-enumerated reasons (stable typed hierarchy,
correctness contract, determinism, backend layout, framework-boundary risk).
Pass.

**v0.8 boundary**: Deferred until contract is precise. Not device recursion.
Framed as a future design study, not an immediate implementation. Pass.

### Supporting Surface A: Bounded Emitted-Row Reductions

**App scenarios**: Hausdorff, outlier, DBSCAN, robot collision, Barnes-Hut
force sums. All existing apps. Pass.

**v0.8 boundary**: Explicitly not mutable ray payloads. Framed as post-emit row
reduction, which is consistent with ITRE. Recommended as standard library first,
native only after evidence. Pass.

### Supporting Surface B: Non-Rendering Probe Generation Helpers

**App scenarios**: Robot links, LOS rays, sensor fans, terrain visibility, RF
paths. Pass.

**v0.8 boundary**: Outputs are typed RTDL input rows. Explicitly excludes
Monte-Carlo rendering distributions, BRDF sampling, hemisphere shading normals,
depth-of-field. Pass.

## Boundary Preservation Check

The Non-Goals section names every item from the rejected brainstorm:

- shader callbacks exposed to users — excluded
- mutable ray payloads — excluded
- device-side recursive ray spawning — excluded
- path tracing — excluded
- global illumination — excluded
- ambient occlusion as a rendering feature — excluded
- BRDF/material/skybox APIs — excluded
- full simulation framework — excluded

The Language Feature Or Standard Library table correctly distinguishes which
extensions require backend changes (any-hit, hierarchical filtering) from which
can start as Python helpers (LOS, graph orchestration, reductions, probe
generation). This is the right architectural split.

## Sequencing Check

The proposed goal sequence (A: contract, B: CPU/oracle, C: LOS app, D: native
backend, E: multi-stage design, F: hierarchy contract) is sensible. Starting
with a formal contract before implementation is correct given cross-backend
parity risk.

## Minor Observations

These do not require revision:

1. The LOS section correctly defers deterministic first-blocker ID to a later
   release. This should be restated in the Goal C acceptance criteria when
   written, to prevent scope creep.

2. The multi-hop graph helper shape (`rt.iterative_rows`) is a conceptual
   sketch. When Goal E begins, the design should decide whether this helper
   belongs in the RTDL package or in a separate app-level utilities module.

3. The performance test requirements across all candidates consistently require
   separating Python orchestration time from RTDL kernel time. This is a good
   discipline rule and should be codified in a standard test reporting template
   before Goal B begins.

## Conclusion

The report does what Goal 534 required: it rewrites the rejected rendering
brainstorm into bounded non-rendering ITRE extensions with app scenarios,
existing-app impact, usefulness, and challenge assessments for each candidate,
while keeping v0.8 boundaries intact. No revisions needed before proceeding to
Goal A.
