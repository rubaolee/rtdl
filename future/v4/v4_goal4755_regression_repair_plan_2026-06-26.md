# V4 Goal4755 Regression Repair Plan

Status: `in_progress_after_complete_serious_matrix`

Source matrix:
`future/v4/evidence/v4_goal4753_serious_all30_clean_2026-06-26/`

Analysis:
`future/v4/v4_goal4754_final_rt_core_matrix_analysis_2026-06-26.md`

## Current Facts

- 30/30 NVIDIA RT-core serious rows executed successfully.
- All rows emitted parseable JSON.
- Embree was not used as a primary denominator.
- V4.0 now has V2.14/V3.0.2/V4.0 rows for all 10 promoted benchmark apps.
- Current hot-metric analysis finds:
  - material candidate: `barnes_hut`
  - parity/control: `rt_dbscan`, `raydb_style`, `librts_spatial_index`,
    `robot_collision`, `contact_manifold`, `rtnn`
  - repair/reclassification required: `triangle_counting`, `hausdorff_xhd`,
    `spatial_rayjoin`

## Goal4755.A: Triangle Counting

Problem:
The clean matrix shows V4/V3 hot replay `0.969x`, while the earlier Goal4733
focused run showed V4/V3 hot replay `1.043x`. The focused rerun after the matrix
showed `0.938x`, so this is not a single bad sample.

Required work:

- Keep the V2.14/V3/V4 same graph fixture and same RT-core route.
- Report two metrics separately:
  - hot prepared replay median
  - one-shot app/backend wall estimate from `phase_split_ms.one_shot_backend_estimate_ms`
- If hot replay remains below `0.98x`, V4 cannot claim no-regression on the hot
  replay path, even if one-shot app wall is faster.
- If one-shot wall is materially faster, classify as `wall_win_hot_replay_regression`
  rather than hiding the hot regression.

Exit:

- Either V4/V3 hot replay `>=0.98x`, or the release packet explicitly carries
  `triangle_counting_hot_replay_regression_open`.

## Goal4755.B: Hausdorff XHD

Problem:
The fair threshold-decision row shows V4/V2.14 hot `0.951x`. However V4 also has
a generic exact nearest-witness / adaptive argmax route that is a stronger output
contract and previously passed focused gates.

Required work:

- Do not divide V4 exact route by V2.14 threshold route as if they are the same
  primitive.
- Add a user-level semantic row:
  - task: "produce Hausdorff decision, with V4 allowed to return exact witness as
    a stronger result"
  - V2.14 denominator: best available RT-core threshold-decision route
  - V4 route: exact nearest-witness/adaptive argmax route
- Report it as `semantic_superset_route`, not `same_primitive_route`.
- Preserve the existing same-primitive threshold row as a regression/control row.

Exit:

- Either the semantic-superset V4 route passes correctness and materially beats
  V2.14 for the user task, or Hausdorff remains a V4.0 release blocker.

## Goal4755.C: Spatial RayJoin

Problem:
The current matrix uses a very small `overlay_seed` command whose hot time is
around 70 microseconds, and V4 is slower than V2/V3. That row is valid as a smoke
compatibility row but too small to be the serious app-level performance row.

Required work:

- Replace the final performance row with the generated shape-pair serious input
  used by Goal4681, or generate the equivalent input in Goal4753.
- Use the V4 shape-pair relation active-count wrapper where appropriate.
- Keep the old `overlay_seed` row as compatibility smoke only.
- If generated-shape serious hot remains below `0.98x` vs V2/V3, Spatial stays a
  release blocker.

Exit:

- A serious generated-shape spatial row with correctness parity and no hidden
  fallback, or explicit `spatial_rayjoin_release_blocker_open`.

## Goal4755.D: Final Reanalysis

After A-C, regenerate:

- `future/v4/evidence/v4_goal4754_final_rt_core_matrix_analysis_2026-06-26.json`
- `future/v4/v4_goal4754_final_rt_core_matrix_analysis_2026-06-26.md`

The release decision remains blocked until:

- every app has a serious, non-toy row;
- no unqualified V4/V2.14 broad speed claim is made;
- any remaining regression is explicitly named in public release wording; and
- external reviewers certify the final packet.
