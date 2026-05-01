# Goal1220 v0.9.8 Final Authorization

Date: 2026-05-01

## Verdict

`AUTHORIZED_FOR_RELEASE_ACTION_AFTER_THIS_GOAL_HAS_2_AI_CONSENSUS`

## Scope

Goal1220 is the final authorization record for the `v0.9.8` bounded RTX app
evidence and public-claim cleanup release.

This record authorizes the next release-action step only after this Goal1220
record itself receives external review and a saved two-AI consensus report.

## Evidence Accepted

- Goal1214 full local discovery: `2366` tests OK, `196` skips, `0` failures,
  `0` errors.
- Goal1215 release-surface documentation audit: `64` tests OK.
- Goal1216 release-candidate audit: accepted with two-AI consensus.
- Goal1217 version-marker sync: accepted with two-AI consensus.
- Goal1218 release-authorization gate: valid evidence, no pod needed.
- Goal1219 v0.9.8 release package: accepted by Gemini and Codex.
- v0.9.8 release package exists under `docs/release_reports/v0_9_8/`.

## Public Claim Boundary

The authorized release boundary remains narrow:

- reviewed public RTX wording rows: `11`;
- newly reviewed row:
  `road_hazard_screening / prepared_native_compact_summary_40k`;
- `database_analytics` public speedup wording remains `blocked`;
- `polygon_set_jaccard` public speedup wording remains `blocked`;
- road-hazard wording is limited to the prepared native compact-summary
  traversal/count sub-path at 40k copies;
- no broad app-suite, whole-app, or all-OptiX RT-core speedup claim is
  authorized.

## Hardware Decision

No additional pod run is required before the release action. Existing
Goal1206/Goal1208 RTX evidence is sufficient for the currently bounded public
claims.

## Authorized Next Release Action

After Goal1220 receives external review and a saved two-AI consensus report,
the release action may proceed in a separate step:

1. Bump `VERSION` from `v0.9.6` to `v0.9.8`.
2. Run the focused release gate and any final smoke selected by the release
   operator.
3. Commit the release docs and version bump.
4. Create annotated tag `v0.9.8`.
5. Push `main` and tag `v0.9.8`.

## Not Authorized In This Step

This record by itself does not perform the release action. Do not tag, push,
publish, upload packages, or bump `VERSION` until Goal1220 external review and
two-AI consensus are saved.

## Boundary

Goal1220 authorizes the release action only after its own 2-AI closure. It does
not expand public RTX claims beyond the reviewed v0.9.8 package boundary.
