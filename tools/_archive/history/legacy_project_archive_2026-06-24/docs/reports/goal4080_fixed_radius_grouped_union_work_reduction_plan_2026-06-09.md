# Goal4080 Fixed-Radius Grouped-Union Work-Reduction Plan

Date: 2026-06-09

## Verdict

`planned`

Goal4080 defines the next serious RT-DBSCAN performance direction after the
Goal4074-4079 evidence chain. The target is not an app-specific DBSCAN engine.
It is a generic fixed-radius grouped-union work-reduction primitive candidate.

## Evidence Chain

Recent evidence constrains the design:

| Evidence | Lesson |
| --- | --- |
| Goal4071 | The current recommended route remains RTDL/OptiX grouped stream plus Numba component-size signature. Partition previews are 6.1x-12.8x slower at 65K clustered data and must not displace the default. |
| Goal4074 | Production RT-DBSCAN timing is dominated by native grouped-union traversal, not by Numba signature continuation. |
| Goal4075 | Fusing Numba workspace reset removes a warning but does not materially move route timing. |
| Goal4078 | Root path-compression with extra atomics is not a material win and was reverted. |
| Goal4079 | Current-head telemetry shows hundreds of millions of candidate hits and roughly two root finds per candidate; the next primitive must reduce candidate enumeration and root-read work together. |
| Goal3999 / Goal4014 / Goal4066 | Partition summaries are useful for capacity control and safe-full/ambiguous classification, but partner-preview execution is not fast enough to promote. |

## Current Design Problem

The accepted grouped-stream route is exact and RT-core accelerated, but it still
performs massive candidate work in dense fixed-radius graphs:

| Profile | Candidate hits | Same-root culled | Reported candidates | Root calls |
| --- | ---: | ---: | ---: | ---: |
| `clustered3d_65536` | 273,911,978 | 273,834,399 | 77,579 | 547,999,682 |
| `road3d_65536` | 85,627,372 | 85,465,232 | 162,140 | 171,701,650 |
| `ngsim_dense_65536` | 12,299,418 | 12,225,228 | 74,190 | 24,763,954 |

Same-root culling is highly effective, but it happens after the engine has
already visited and root-checked the candidates. This is why wrapper-level
changes do not produce a major speedup.

## Candidate Primitive

The proposed candidate is:

`prepared_fixed_radius_partition_convergence_grouped_union_3d`

It must remain generic. Allowed words include fixed-radius, partition,
candidate, component, root, grouped-union, AABB, summary, ambiguous, safe-full,
and traversal. Forbidden in native ABI names and core internals: DBSCAN,
cluster, epsilon, min-points, road, trajectory, or benchmark-app labels.

## Required Contract

The candidate should expose a prepared device-resident flow:

1. consume prepared 3D points and radius;
2. build or consume partition columns with AABBs and counts;
3. classify partition pairs into `safe_skip`, `safe_full`, and `ambiguous`;
4. union safe-full partition pairs without materializing point pairs;
5. execute exact RT traversal only for ambiguous boundary work;
6. produce component parent/label/signature columns compatible with the existing
   fixed-radius grouped-stream component contract;
7. emit diagnostic counters for candidate hits, safe-full unions, ambiguous
   traversal hits, root calls, parent-link steps, pass count, overflow, and
   completeness.

## Acceptance Bars

The candidate may be promoted from `candidate` to `accepted_preview` only if all
bars pass:

| Bar | Requirement |
| --- | --- |
| App-agnostic boundary | No app-shaped native ABI, no DBSCAN vocabulary in native/core runtime symbols, no hidden dispatch, no automatic partner selection. |
| Correctness | Same component-size signature as the current grouped-stream route on `clustered3d`, `road3d`, and `ngsim_dense`; label equivalence where label materialization is requested. |
| Completeness | Fail closed on overflow, incomplete candidate coverage, unsupported partner/device, or stale partition metadata. |
| Performance | Beat the current recommended route on at least `clustered3d_65536` and `road3d_65536` in production timing, not telemetry timing; record `ngsim_dense_65536` and block promotion on a material regression there. |
| Partition overhead | Record partition-build elapsed time separately as `partition_summary_build_sec` and include it in net production-route timing. |
| Work reduction | Demonstrate at least 50% lower candidate hits or root calls than Goal4079 on every row it claims to improve. Smaller reductions may remain diagnostic but cannot promote the candidate. |
| Traceability | Artifact must include source commit, GPU, OptiX library path, route flags, counters, stdout, and all claim-boundary booleans. |
| Claim discipline | No release, public speedup, paper reproduction, broad RT-core, whole-app acceleration, true-zero-copy, or default-route claim until external consensus. |

## Implementation Sequence

1. **Goal4081 native/API feasibility:** add no new default route; inspect whether
   the existing grouped-union OptiX path can consume partition pair ranges
   without rebuilding the whole pipeline.
2. **Goal4082 device partition summary bridge:** expose partition summary
   columns to the native candidate without app vocabulary and with fail-closed
   capacity/completeness metadata.
3. **Goal4083 safe-full partition union:** implement a native or partner-neutral
   device continuation that unions safe-full partition pairs without point-pair
   materialization.
4. **Goal4084 ambiguous RT traversal route:** restrict RT traversal to
   ambiguous partition ranges while preserving exactness.
5. **Goal4085 current-route comparison:** compare against the accepted
   grouped-stream Numba route at 65K and larger profiles, including
   `ngsim_dense_65536`, with correctness, partition-build timing, and work
   counters.

If any step cannot preserve exactness or app-agnostic symbols, the candidate
must stay rejected or deferred.

## Questions For External Review

1. Is this the right next engineering direction after Goals4074-4079?
2. Are the acceptance bars strong enough to avoid another slow preview?
3. Is there a simpler generic candidate that could reduce candidate/root work
   without building a partition-convergence route?
4. Does the plan preserve the user-choice partner principle and native
   app-agnostic boundary?
5. What should be measured before any code promotion?

## Boundary

This plan does not authorize implementation promotion, release, public speedup
wording, broad RT-core wording, whole-app acceleration wording, paper
reproduction wording, automatic partner selection, true-zero-copy claims, or
app-specific native-engine logic. It is a plan for the next candidate primitive.
