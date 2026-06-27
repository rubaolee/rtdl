# Goal1124 Claude Review

Date: 2026-04-29

Reviewer: Claude Sonnet 4.6

## Verdict

ACCEPT.

## Review Scope

Reviewed against the four mandatory criteria from the task brief:

1. Facility and Barnes-Hut promoted only as narrow sub-path wording
2. Robot remains blocked
3. Stale below-100ms wording removed from current public surfaces
4. No whole-app/default-mode speedup claim leaked

## Criterion 1 — Facility and Barnes-Hut as Narrow Sub-Path Wording

**PASS.**

`facility_knn_assignment` carries `PUBLIC_WORDING_REVIEWED` in
`_RTX_PUBLIC_WORDING_MATRIX` with the wording "RTDL's prepared facility
coverage-threshold RTX query sub-path measured 0.103119 s and 87.24x versus
the reviewed same-contract CPU oracle baseline." The boundary field explicitly
excludes ranked nearest-facility assignment, KNN fallback output,
facility-location optimization, Python-side setup, and whole-app speedup.

`barnes_hut_force_app` carries `PUBLIC_WORDING_REVIEWED` with the wording
"RTDL's prepared Barnes-Hut node-coverage RTX query sub-path measured 0.240634
s and 222.19x versus the reviewed same-contract Embree node-coverage baseline."
The boundary field explicitly excludes Barnes-Hut opening-rule evaluation,
candidate-row output, force-vector reduction, N-body simulation, and whole-app
speedup.

Both entries are consistently reflected across:

- README.md (lines 99–105): both listed under the narrow sub-path label, with
  the explicit disclaimer that each is "not a whole-app, default-mode,
  Python-postprocess, or broad RT-core acceleration claim."
- `docs/v1_0_rtx_app_status.md`: table Scope column reads "prepared facility
  coverage-threshold query sub-path only" and "prepared Barnes-Hut
  node-coverage query sub-path only."
- `docs/rtdl_feature_guide.md` (lines 103–106): "Goal1123 did accept narrow
  public wording for facility coverage-threshold and Barnes-Hut node-coverage
  prepared RTX query sub-paths."
- `docs/app_engine_support_matrix.md` readiness table: both rows cite Goal1123
  and name the sub-path only.
- `_GOAL1058_FACILITY_VALIDATED_POLICY` and the maturity-matrix entries for
  both apps explicitly hold the out-of-scope paths outside the claim.

The ratios (87.24x and 222.19x) are large but are consistently presented with
their sub-path labels ("same-contract CPU oracle baseline" for facility;
"same-contract Embree node-coverage baseline" for Barnes-Hut). Goal1123 reviewed
and accepted these baselines; no inflation to whole-app scope occurs anywhere in
the public surface.

## Criterion 2 — Robot Remains Blocked

**PASS.**

`robot_collision_screening` carries `PUBLIC_WORDING_BLOCKED` in
`_RTX_PUBLIC_WORDING_MATRIX`. The reviewed_wording field reads "No public RTX
speedup wording is authorized for robot_collision_screening yet." The boundary
field reads "public ratio wording remains blocked until a same-scale or
explicitly normalized baseline review is accepted."

This is consistently reflected:

- README.md (lines 107–111): robot explicitly excluded with the Goal1121/1123
  rationale.
- `docs/v1_0_rtx_app_status.md` (lines 37–42): robot excluded paragraph present
  and accurate.
- `docs/v1_0_rtx_app_status.md` status table (row for robot): status column
  shows `rt_core_ready / blocked_for_public_speedup_wording`; allowed wording
  and cloud action describe the block.
- `docs/app_engine_support_matrix.md` readiness table: robot listed as
  `blocked_for_public_speedup_wording` with the same-scale baseline gate cited.
- `docs/rtdl_feature_guide.md` (lines 101–104): robot is explicitly
  `public_wording_blocked` with the correct reasoning.
- `docs/release_facing_examples.md` (lines 72–76): robot explicitly noted as
  excluded from public RTX speedup wording.
- `_GOAL1058_ROBOT_VALIDATED_POLICY` string in `app_support_matrix.py` carries
  the correct Goal1121/Goal1123 reference.
- Tests in `goal947_v1_rtx_app_status_page_test.py` assert `blocked_public_wording
  == 1` and assert `robot_collision_screening` has `public_wording_status ==
  "public_wording_blocked"`.

No file in the reviewed set authorizes or implies public robot speedup wording.

## Criterion 3 — Stale Below-100ms Wording Removed

**PASS.**

The Goal1124 report records a targeted ripgrep over all public surfaces for
phrases including "larger RTX repeats stayed below", "below the 100 ms
public-review timing floor", "Goal1008 keeps public speedup wording blocked",
"facility_knn_assignment.*public_wording_blocked", and
"timing-floor/baseline review" — with zero matches. I did not find any such
wording in the files reviewed directly. References to the 100 ms floor now
correctly state that the timing floor was cleared (for robot via Goal1121) or do
not mention it at all. No file describes facility or Barnes-Hut as falling below
the 100 ms threshold.

## Criterion 4 — No Whole-App/Default-Mode Speedup Claim Leaked

**PASS.**

The public surface consistently uses limiting language:

- README.md explicitly: "not broad speedup claims for DB, graph, one-shot
  calls, or full emitted-row workloads"; "not a whole-app, default-mode,
  Python-postprocess, or broad RT-core acceleration claim."
- `docs/v1_0_rtx_app_status.md` Forbidden Wording section explicitly bars
  "RTDL accelerates the whole app."
- `docs/release_facing_examples.md`: "These commands are bounded sub-paths, not
  broad speedup claims."
- `docs/rtdl_feature_guide.md`: "These are not whole-app speedup claims."
- `app_support_matrix.py` policy strings and boundary fields consistently exclude
  whole-app, default-mode, Python-postprocess, and ranking acceleration from the
  claims.
- The `reviewed_public_wording` count is 9, matching the tested assertion in
  `goal947_v1_rtx_app_status_page_test.py`.
- Test assertion: "RTDL accelerates the whole app" must not appear in any
  `allowed_claim` field — this is enforced by the test suite.

## Additional Observations

- The three-AI consensus from Goal1123 is faithfully reflected: facility and
  Barnes-Hut promoted, robot kept blocked. The Goal1124 application does not
  exceed the scope authorized by Goal1123.
- `app_support_matrix.py` correctly shows `PUBLIC_WORDING_REVIEWED` for 9 apps
  and `PUBLIC_WORDING_BLOCKED` for robot, matching the summary count in
  `docs/v1_0_rtx_app_status.md`.
- Evidence citations (Goal1121/Goal1123) are present in the matrix, the README
  trail, and the status page.
- No release authorization, cloud-run trigger, or new benchmark claim appears
  anywhere in the update.

## Summary

All four mandatory criteria pass. Goal1124 correctly and conservatively applied
the Goal1123 consensus to the live matrix and public docs. The update is
bounded to the accepted wording for two sub-paths, keeps robot blocked with the
correct rationale, removes stale timing-floor language, and introduces no
whole-app or default-mode speedup claim.
