# Goal1146 Public RTX Wording Promotion Packet

Date: 2026-04-29

Status: `PROMOTION_REVIEW_PACKET`

## Purpose

Goal1142/Goal1143 now have Codex plus Gemini consensus for evidence validity:
the current-source RTX packet is valid, same-source, and safe to use as
evidence. This Goal1146 packet separates the next decision from that evidence
review: whether to promote any of the three still-blocked public speedup wording
rows.

This packet does not edit public docs, does not change
`rtdsl.rtx_public_wording_matrix()`, and does not authorize release.

## Evidence Trail

- Same-source intake:
  `docs/reports/goal1142_current_source_rtx_rerun_intake_with_robot_64m_2026-04-29.json`
- Gemini evidence review:
  `docs/reports/goal1142_gemini_manual_external_review_2026-04-29.md`
- Codex plus Gemini consensus:
  `docs/reports/goal1142_goal1143_two_ai_consensus_2026-04-29.md`
- Public wording hold sync:
  `docs/reports/goal1145_post_gemini_accept_public_wording_state_sync_2026-04-29.md`

## Proposed Decisions

| App | Path | Proposed public wording status | RTX query median | Baseline comparison | Proposed action |
| --- | --- | --- | ---: | --- | --- |
| `facility_knn_assignment` | `coverage_threshold_prepared_recentered` | `public_wording_reviewed` | `0.111619` s | `80.60x` vs reviewed same-contract CPU oracle; `267.04x` vs same-contract Embree query median | Promote narrow prepared coverage-threshold query wording only. |
| `robot_collision_screening` | `prepared_pose_flags` | `public_wording_blocked` | `0.178471` s for 64M poses | Timing floor cleared; available Embree comparison is 36M chunked aggregate, not same total work | Keep blocked until same-scale or explicitly normalized baseline wording is separately reviewed. |
| `barnes_hut_force_app` | `node_coverage_prepared_rich` | `public_wording_reviewed` | `0.222256` s | `240.56x` vs reviewed same-contract Embree node-coverage query median | Promote narrow prepared node-coverage query wording only. |

## Candidate Public Wording

### facility_knn_assignment / coverage_threshold_prepared_recentered

RTDL's prepared facility coverage-threshold RTX query sub-path measured
`0.111619` s and `80.60x` versus the reviewed same-contract CPU oracle
baseline.

Boundary: only the prepared recentered coverage-threshold query decision is
covered. Ranked nearest-facility assignment, KNN fallback output,
facility-location optimization, Python-side setup, and whole-app speedup remain
outside this wording.

### robot_collision_screening / prepared_pose_flags

No public RTX speedup wording is authorized for `robot_collision_screening` yet.

Boundary: the prepared ray/triangle any-hit pose-flag path is real RT-core work
and has timing-floor evidence, but public ratio wording remains blocked until a
same-scale or explicitly normalized baseline review is accepted. Full robot
kinematics, scene construction, ray packing, witness-row output, continuous
collision detection, Python input construction, and whole-app planning speedup
remain outside any wording.

### barnes_hut_force_app / node_coverage_prepared_rich

RTDL's prepared Barnes-Hut node-coverage RTX query sub-path measured `0.222256`
s and `240.56x` versus the reviewed same-contract Embree node-coverage
baseline.

Boundary: only the prepared depth-8 node-coverage threshold traversal is
covered. Barnes-Hut opening-rule evaluation, candidate-row output, force-vector
reduction, N-body simulation, and whole-app speedup remain outside this wording.

## Reviewer Questions

1. Is it acceptable to promote the facility wording above as a bounded public
   RTX speedup line?
2. Is it acceptable to promote the Barnes-Hut wording above as a bounded public
   RTX speedup line?
3. Is it correct to keep robot public speedup wording blocked despite the 64M
   RTX timing floor being cleared, because the available baseline comparison is
   not same total work?
4. Are the boundaries narrow enough to avoid whole-app, default-mode, Python
   postprocess, or broad RT-core claims?

## Boundary

This is a promotion review packet only. The current public matrix remains
blocked for all three rows until an external review explicitly accepts this
promotion packet and Codex writes a follow-up consensus report.
