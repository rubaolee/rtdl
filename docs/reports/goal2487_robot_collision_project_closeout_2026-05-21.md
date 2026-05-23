# Goal2487 Robot Collision Project Closeout

Date: 2026-05-21

Status: Goal2487 is complete with Codex, Gemini, and Claude consensus.

## Summary

The robot-collision benchmark campaign is complete for the intended first pass.
It did not try to reproduce a robotics paper. It used the app shape to force a
useful RTDL language/runtime reconstruction while keeping the native engine
app-agnostic.

## What Robot Collision Forced Into RTDL

The campaign added or validated these reusable RTDL patterns:

- dynamic transformed query geometry in Python;
- prepared static scene plus changing query batches;
- compact byte-per-group any-hit flags;
- phase-separated timing across app lowering, query packing, native traversal,
  and output postprocess;
- explicit prepared-state reuse metadata;
- native app-vocabulary scans for active Embree and OptiX engines;
- bounded performance matrix rows for CPU reference, Embree prepared, and OptiX
  prepared paths.

The native engine remains app-agnostic. Active Embree/OptiX native paths use
scene, triangle, segment, query, group, hit, and flag vocabulary. They do not
expose native robot, link, pose, planner, or collision APIs.

## Goal Outcomes

| Goal | Outcome |
| --- | --- |
| Goal2479 | Roadmap and claim boundary approved. |
| Goal2480 | Deterministic CPU reference app added. |
| Goal2481 | Generic grouped 3D segment-probe contract approved. |
| Goal2482 | Embree prepared static triangle scene implementation added. |
| Goal2483 | OptiX same-contract implementation validated on NVIDIA A5000 pod. |
| Goal2484 | Prepared/reused benchmark protocol and app-level prepared modes added. |
| Goal2485 | Bounded CPU/Embree/OptiX performance matrix collected. |
| Goal2486 | Continuous/swept collision implementation deferred. |

## Performance Conclusion

Goal2485 shows that the exact measured native traversal phases are small, while
the current prepared native total path is dominated by Python-side query packing.
On the A5000 pod with 256 poses, 3 links, 32 obstacles, 768 query groups, and
6912 finite segment probes:

```text
CPU reference tail median:      3.5098454765975475 s
Embree prepared tail median:    0.04113018698990345 s
OptiX prepared tail median:     0.036702703684568405 s
Embree traversal phase median:  0.000197899 s
OptiX traversal phase median:   0.000129123 s
```

This is not a public speedup claim. It is internal evidence for the exact
sampled finite segment-probe subpath.

## Claim Boundary

No paper reproduction claim.

No authors-code comparison claim.

No public speedup claim.

No exact solid-contact claim.

No continuous/swept support claim.

No native robot/link/pose/planner/collision API claim.

No package-install claim.

No release/tag action.

## Deferred

Deferred work is explicit:

- native query/output buffer reuse or device-column handoff for the segment
  probe path;
- larger fixture sweeps after query packing overhead is reduced;
- bit-packed flags only if Goal2485-style evidence shows flag bandwidth matters;
- continuous/swept collision as a separately reviewed v3.0-or-later candidate;
- paper/authors-code comparison only after official code/data are verified in a
  separate scoping goal.

## External Review

Gemini and Claude independently approved the closeout. The consensus artifact is:

```text
docs/reviews/goal2487_codex_gemini_claude_consensus_robot_collision_closeout_2026-05-21.md
```

The reviews checked:

- whether the native engine boundary remains app-agnostic;
- whether the performance matrix is bounded honestly;
- whether the continuous/swept deferral is correct;
- whether Goal2487 can close the robot-collision benchmark campaign.
