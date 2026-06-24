# Goal1659 v1.6.11 Local Command Preflight

## Verdict

`accepted_local_preflight`

The local preflight for the v1.6.11 performance matrix passed.

## Scope

- Apps covered by the matrix: `18`
- Local help commands checked: `16`
- Excluded/frozen apps without local perf command: `2`
- Failed commands: `0`

The two skipped apps are `apple_rt_demo` and `hiprt_ray_triangle_hitcount`,
which are frozen/proof surfaces outside the active Embree+OptiX v1.6.11
performance release candidate.

## Pod Need

No pod is needed for this local preflight. A pod is still required for final
NVIDIA OptiX performance evidence because the release candidate needs real RTX
hardware timing for the OptiX rows.

## Artifact

Machine-readable preflight output:

`docs/reports/goal1659_v1_6_11_local_command_preflight_2026-05-10.json`

## Boundary

This preflight only proves that the local command surface for the detailed
performance matrix is structurally available. It does not publish v1.6.11,
authorize a release tag, authorize public speedup wording, promote
`COLLECT_K_BOUNDED`, or claim whole-app performance.
