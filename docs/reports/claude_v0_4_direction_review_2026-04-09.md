# Claude v0.4 Direction Review

Date: 2026-04-09

## Verdict

The direction proposal correctly rejects Proposals A and B, and Proposal C is the
right long-term heading. But the document does not actually commit to it. It argues
for a workload-language-first v0.4 and then ends by asking which single workload
should be the first target. That is not a decision — it is a problem statement.
Before v0.4 opens, one concrete 3D workload must be chosen and contracted. Until
that happens, the recommended direction is sound in principle but not actionable.

## Findings

**1. The proposal defers the only hard question**

The "Immediate next planning questions" section lists four open questions, the first
of which is: "Which single 3D workload should be the first accepted v0.4 public
target?" A direction document that ends on this question has not decided the
direction. It has described the space of candidates and handed the decision back
to the next session. This is the overconfidence problem: the proposal argues
confidently for Proposal C while leaving the specific workload choice — the
only thing that makes v0.4 real — unresolved.

**2. `ray_tri_hitcount_3d` already exists and is not a new release feature**

Objective 1 names `ray_tri_hitcount` as a public workload line candidate for v0.4.
The current repo already uses `ray_triangle_hitcount_3d_demo` as the kernel for both
the camera-hit and shadow-visibility passes in the v0.3.0 demo. The 3D ray/triangle
hit-count capability is not new engineering for v0.4 — it is the current v0.3.0
technical substrate. Promoting it to a formal public feature line is a legitimate
v0.4 move, but it should be called what it is: a contractual and documentation lift,
not a new workload family. If that is the main v0.4 substance, the release identity
should be "formally contract what v0.3.0 proved" rather than "extend RTDL into 3D."
Those are different claims with different scope and different honesty levels.

**3. Point-in-mesh needs a watertightness boundary before it can be contracted**

The proposal lists point-in-mesh / point-in-volume as a v0.4 candidate. For a
watertight closed mesh, point-in-mesh is implementable via odd-even ray casting
using the current ray/triangle hit-count kernel. That is genuinely achievable. But
the proposal says nothing about what happens with open meshes, degenerate triangles,
or near-boundary query points. The v0.2.0 surface is explicitly bounded and
documented. A point-in-mesh feature that does not explicitly state its watertightness
requirement would be a step backward in honesty relative to the current contracts.
It is a viable v0.4 target if and only if the accepted-boundary documentation is
written before the feature is claimed, not after.

**4. Hausdorff-adjacent workloads should not be in the v0.4 candidate list**

The proposal includes "nearest/distance or Hausdorff-adjacent geometry workloads
only if bounded and honestly documented" among Objective 1 candidates. This is
overreach. Hausdorff distance requires a different algorithmic approach from
ray/triangle hit counting. The X-HD paper in the reference list is relevant
future direction, but the current RTDL kernel does not support distance queries.
Adding it to the v0.4 candidate list — even hedged — inflates scope and muddies
the story. It should be removed from the v0.4 candidate list entirely and kept
in the future-directions reference where it belongs.

**5. Objective 3 is the most concrete and most important item**

Objective 3 — "add one non-demo user-facing 3D example chain" — is the single
most valuable item in the proposal regardless of which workload is chosen. The
current front-door 3D proof is a video of a lit sphere. A direct non-graphical
3D query example (e.g., point-in-mesh for a known test volume, counting which
query points fall inside a closed tetrahedral mesh, compared against a brute-force
reference) would do more to establish the intended product identity than any
amount of formal workload contracting. It is also the item that most directly
separates RTDL from a renderer in the eye of a new reader. This objective should
be treated as a v0.4 entry requirement, not one of five parallel objectives.

**6. The performance story is absent**

v0.1 had county_zipcode PIP vs PostGIS. v0.2 had segment_polygon x4096 vs PostGIS.
v0.4 has no external comparison baseline named. For 2D workloads the comparison
target (PostGIS) is natural and well-established. For 3D geometric queries it is
not obvious. What does RTDL compare against for point-in-mesh performance? A
brute-force spatial index? A purpose-built library? Without an answer this is not
a performance story — it is a correctness story only. That is not wrong, but the
proposal should acknowledge it rather than implying the same performance narrative
will transfer from the 2D line to the 3D line.

**7. The Proposal B rebuttal is slightly unfair**

The rebuttal says backend work alone does not give users a new reason to adopt v0.4.
That is true if backend work is the only theme. But the current situation is that
Vulkan is parity-clean but slower than PostGIS on the v0.2 surface, and OptiX/Embree
win only under specific prepared/repeated-run conditions. Strengthening the backend
performance story — especially for the GPU backends — is not just infrastructure
work; it directly affects the validity of the performance claims. Backend performance
work bundled with the Proposal C workload expansion would be a stronger package than
the proposal acknowledges.

## Summary

Accept Proposal C as the direction. Before v0.4 opens, make two decisions that the
current document defers: (1) pick one specific 3D workload as the v0.4 acceptance
target — the most defensible choice given current engineering is a formally contracted
`ray_tri_hitcount_3d` public feature line, since it formalizes proven capability
rather than adding unproven scope; (2) treat Objective 3, the non-demo 3D example,
as a required entry gate rather than one of five parallel objectives. Remove
Hausdorff-adjacent workloads from the v0.4 candidate list. Add an external
performance comparison baseline to the planning questions before the release story
is written.
