# Goal4079 Current Grouped-Union Root-Work Refresh

Date: 2026-06-09

## Verdict

`accept-with-boundary`

Goal4079 refreshes the generic OptiX fixed-radius grouped-union diagnostic at
current `main` after the Goal4074-4078 route decisions. It does not change the
runtime, does not add an ABI, and does not promote a new default. Its purpose is
to decide what kind of primitive work is worth doing next.

## Scope

The refresh reran the existing 10-counter telemetry path on the RTX 4000 Ada
pod at source commit `f80245b7`.

Artifacts:

- `docs/reports/goal4079_current_grouped_union_root_work_refresh_pod/clustered3d_65536.json`
- `docs/reports/goal4079_current_grouped_union_root_work_refresh_pod/road3d_65536.json`
- `docs/reports/goal4079_current_grouped_union_root_work_refresh_pod/ngsim_dense_65536.json`

Each profile used the current benchmark radius, 65,536 points, three repeats,
and a 10-counter telemetry buffer.

## Important Timing Boundary

The telemetry path adds atomic diagnostic counter updates. Its median elapsed
times are useful for sanity, but they are not production-route timings and
should not be compared directly with Goal4074 app-level timing. The important
evidence here is the work shape: radius-candidate hits, same-root culls,
reported candidates, root-find calls, and root parent-link steps.

## Default-Route Work Shape

Rows below use the accepted diagnostic variant `same_root_on_direct_off`.

| Profile | Radius | Candidate hits | Same-root culled | Reported | Root calls | Parent-link steps | Root calls / candidate | Steps / root call |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `clustered3d` | 0.055 | 273,911,978 | 273,834,399 | 77,579 | 547,999,682 | 646,975,610 | 2.001 | 1.181 |
| `road3d` | 0.030 | 85,627,372 | 85,465,232 | 162,140 | 171,701,650 | 314,297,000 | 2.005 | 1.830 |
| `ngsim_dense` | 0.012 | 12,299,418 | 12,225,228 | 74,190 | 24,763,954 | 33,055,992 | 2.013 | 1.335 |

Same-root culling removes most candidate hits:

| Profile | Culled / candidate | Reported / candidate |
| --- | ---: | ---: |
| `clustered3d` | 99.972% | 0.028% |
| `road3d` | 99.811% | 0.189% |
| `ngsim_dense` | 99.397% | 0.603% |

## Interpretation

Goal4074 already showed that the production RT-DBSCAN route is dominated by
native grouped-union traversal, not by Numba signature continuation. Goal4075
then removed a small Numba launch-warning cost, and Goal4078 rejected root
path-compression because extra atomics did not improve the route.

Goal4079 explains why those outcomes make sense. The accepted grouped-union
path is doing huge exact radius-candidate work and roughly two readonly root
finds per candidate. The native pass is not slow because many candidates are
ultimately reported; it is slow because the engine must examine and cull a very
large number of exact candidates while repeatedly reading component roots.

This also explains why the rejected options are weak:

- disabling same-root culling removes a crucial correctness-preserving cull and
  does not reduce candidate enumeration;
- direct side effects remove the report-buffer path but do not remove candidate
  traversal or root-read work;
- blocked query ranges add native launches while preserving the same work;
- root path-compression adds atomics without reducing candidate pressure.

## Next Primitive Target

The next useful work should be a generic grouped-union work-reduction primitive,
not another wrapper-level toggle. The evidence points to a
`partition-convergence hybrid`:

1. prepare device-resident spatial partition columns and per-partition AABBs;
2. summarize safe full-partition pairs without materializing point pairs;
3. route ambiguous boundary partition pairs through exact RT traversal;
4. preserve explicit component-root/convergence metadata;
5. expose the contract as fixed-radius grouped-union work, not as DBSCAN,
   clustering, epsilon/min-points, or any app-specific native ABI.

The design goal is to reduce candidate enumeration and root-read work together.
Any next probe should report candidate hits, same-root culls, reported
candidates, root calls, parent-link steps, correctness signatures, and
production-route timing separately.

## Boundary

This report does not authorize release, public speedup wording, broad RT-core
speedup wording, whole-app acceleration wording, paper reproduction wording,
true-zero-copy wording, automatic partner/backend selection, app-specific
native-engine logic, or a default route switch. It is current-head diagnostic
evidence for the next generic primitive.
