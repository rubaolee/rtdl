# Goal1126 Three-AI Consensus

Date: 2026-04-29

Verdict: `ACCEPT`

Goal1126 is accepted as an explicit normalized-baseline review for `robot_collision_screening / prepared_pose_flags`. It remains a review packet only: it does not itself edit public wording, authorize release, start cloud resources, or authorize broad whole-app speedup claims.

## Reviewed Artifacts

- `scripts/goal1126_robot_normalized_public_wording_review.py`
- `tests/goal1126_robot_normalized_public_wording_review_test.py`
- `docs/reports/goal1126_robot_normalized_public_wording_review_2026-04-29.json`
- `docs/reports/goal1126_robot_normalized_public_wording_review_2026-04-29.md`
- `docs/reports/goal1123_public_wording_review_after_goal1121_2026-04-29.json`
- `docs/reports/goal1086_robot_chunked_embree_baseline_intake_2026-04-29.json`
- `docs/reports/goal1121_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json`
- `docs/handoff/REFRESH_LOCAL_2026-04-13.md`

## Consensus

- Codex: `ACCEPT`. The packet is valid, the scale asymmetry is explicit, and the wording is normalized per-pose rather than same-total-work wall time.
- Claude: `ACCEPT`. Claude judged the normalized comparison acceptable despite 64M RTX versus 36M Embree because the obstacle count and result contract match, RTX correctness is separately validated at the same source commit, Embree chunked timing is valid under its split validation/timing contract, and the wording is narrow.
- Gemini: `ACCEPT`. Gemini judged the wording acceptable because it explicitly says normalized per-pose, acknowledges the pose-count difference, and preserves the non-whole-app boundary. Gemini's stdout review is saved in `docs/reports/goal1126_gemini_review_2026-04-29.md`.

## Accepted Wording Scope

The accepted scope is only:

`robot_collision_screening / prepared_pose_flags`: prepared ray/triangle any-hit pose-count query sub-path.

The accepted normalized wording is:

RTDL's prepared robot collision pose-count RTX query sub-path measured 0.178698 s for 64M poses and 917.75x per-pose throughput versus the reviewed 36M chunked Embree any-hit baseline.

## Required Boundary

This is normalized per-pose wording, not a same-total-work wall-time claim. It covers only the prepared ray/triangle any-hit pose-count query sub-path. Full robot kinematics, scene construction, ray packing, witness-row output, continuous collision detection, Python input construction, and whole-app planning speedup are outside the wording.

## Follow-Up

A separate follow-up goal may update only `robot_collision_screening` in `rtdsl.rtx_public_wording_matrix()` and synchronized public docs. That follow-up must keep the normalized wording and boundary intact.

## Verification

```bash
PYTHONPATH=src:. python3 scripts/goal1126_robot_normalized_public_wording_review.py
PYTHONPATH=src:. python3 -m unittest tests.goal1126_robot_normalized_public_wording_review_test tests.goal1125_unresolved_rtx_public_wording_prioritization_test tests.goal1123_public_wording_review_after_goal1121_test -v
python3 -m py_compile scripts/goal1126_robot_normalized_public_wording_review.py tests/goal1126_robot_normalized_public_wording_review_test.py
git diff --check
```
