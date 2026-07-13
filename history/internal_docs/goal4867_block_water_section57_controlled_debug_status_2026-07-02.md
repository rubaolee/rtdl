# Goal4867 Block x Water Section 5.7 Controlled Debug Status

## Scope

Current target: exact AuthorPatch-compatible Block x Water Section 5.7 polygon-overlay reproduction through RTDL OptiX point-location/overlay code.

This is not a broad performance run. The active problem is correctness.

## Current Narrowed Bug Class

The remaining mismatch is narrowed to directed point-location/PIP selection for duplicate half-edges that have:

- the same vertical hit height,
- the same scaled line coefficients `(a, b, c)`,
- opposite directions / different adjacent faces,
- no slope difference for the author SoS slope perturbation to distinguish.

This is not currently an LSI issue, not an output-format-only issue, and not a normal "same height, different slope" PIP issue.

## Confirmed Fixes / Non-Issues

- LSI count/path for Block x Water was previously matched at the count level.
- Per-map midpoint face storage was repaired earlier and is not the active first-order suspect here.
- Output intersection points now use author display coordinates for xsect identity.
- Text/display dedupe was rejected and reverted; dedupe must use raw tuple identity because AuthorPatch can emit duplicate-looking 6-decimal points as distinct raw points.
- CDB point-location AABB z height and final AABB rounding were aligned with author `FillPrimitivesGroupNew`.
- `BlockMerge64` grouping exists and is the active route for large point-location.
- Stable-count block merge sorting was aligned with author control flow: do not sort when the merge count is already stable.
- Custom accel compaction is now implemented when `ALLOW_COMPACTION` is requested, matching the author custom-primitive GAS build pattern.

## Explicitly Rejected Heuristics

The following were tested/considered and must not be reintroduced as "the rule":

- choose larger scaled span `b`;
- choose reverse-x duplicate;
- choose lower/higher segment id;
- choose nonzero face over exterior.

They each fix one local witness while regressing another. The author source does not contain such a second-order geometry/id fallback. For equal slope it only leaves traversal/source order to decide, after the slope-based `t_reported` perturbation has no separating power.

## Key Witnesses After Latest Repairs

Latest POD probe:

`/workspace/goal4867_specific_pip_probe_after_actual_compaction.json`

Known point-location results:

| point index | current RTDL face | current segment | status |
|---:|---:|---:|---|
| 1069665 | 323443 | 15220835 | matches expected witness |
| 5693875 | 0 | 828110 | still suspect; author output includes this coordinate in kept chains |
| 7386601 | 0 | 880129 | matches corrected witness; avoids previous spurious chain |
| 7906217 | 38799 | 1839712 | matches expected witness |
| 9926545 | 0 | 16153901 | matches expected witness |

The still-suspect `5693875` duplicate pair is:

- edge 827259 / segment 827260 / face-by-direction 17144;
- edge 828109 / segment 828110 / face-by-direction 0;
- identical scaled `(a, b, c)` and same slope.

Current RTDL selects the exterior segment `828110`; the author output contains the coordinate around chains 2540635-2540636, implying this point affects the output stream and cannot be ignored.

## Author Dump Attempt

The author source has `RJ_DUMP_PIP_QUERY_MAP_ID` / `RJ_DUMP_PIP_POINT_INDEX` hooks in `map_overlay_rt.h`.

However, the attempted dump using `/workspace/RayJoin_goal4867_author_dump/release/bin/polyover_exec` with `-output=/dev/null` remained in map0 load for more than 100 seconds, unlike the earlier baseline log where cached map loading completed quickly. Treat this as an author-dump tooling issue, not algorithm evidence.

Relevant failed log:

`/workspace/goal4867_author_release_dump_point_5693875_long.log`

## Next Controlled Step

Do not run another full 3.8GB-output overlay as an inner loop.

Next useful steps are:

1. Build a tiny/medium CDB-like duplicate-half-edge case that reproduces the same ambiguity and compare AuthorPatch vs RTDL.
2. Or make the author dump route reliable enough to extract `closest_eid/face` for the named witnesses without writing full output.
3. Only after the duplicate-half-edge rule is understood, rerun a bounded streaming compare.

## Anti-Regression Principle

Any fix must be justified as a directed planar-map point-location contract repair. It must not be a RayJoin output patch or a hard-coded app-specific exception.
