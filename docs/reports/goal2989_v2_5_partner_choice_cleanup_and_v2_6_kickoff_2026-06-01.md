# Goal2989 - v2.5 Partner-Choice Cleanup And v2.6 Kickoff

Date: 2026-06-01
Status: internal closeout cleanup and v2.6 planning start; not release authorization

## Purpose

Goal2989 closes the v2.5 wording gap that could make readers think RTDL chooses
partners for users. It also starts v2.6 from Claude's Numba-first-class partner
reference note:

- `docs/reports/claude_v2_6_numba_first_class_partner_work_for_main_ai_2026-05-31.md`

The intended doctrine is now explicit:

```text
Users choose supported partners.
RTDL provides high-performance support for the partners it supports.
Benchmark apps provide reference or recommended implementations with our chosen measured partner path.
The native engine remains a generic app-agnostic primitive engine.
Triton is paused/ignored for recommended v2.5 paths after negative same-contract evidence.
v2.6 begins from neutral-buffer-seam cleanup plus a Numba first-class, user-selectable partner lane.
```

## User Decisions Captured

| # | Decision | Goal2989 handling |
| --- | --- | --- |
| 1 | Partner choice belongs to the user. | `v2_5_primitive_first_selection_doctrine()` and `v2_5_partner_choice_cleanup_policy()` now state user-owned explicit partner choice. |
| 2 | Benchmark apps give reference or recommended implementations with our chosen partner. | The cleanup policy records benchmark apps as `reference_or_recommended_implementations_with_project_chosen_partner_paths`. |
| 3 | RTDL remains a generic engine with high-performance primitives. | The doctrine and cleanup policy require an app-agnostic native primitive boundary. |
| 4 | v2.5 shows Triton is not a good current choice, so ignore it for now. | Triton is recorded as paused/ignored for recommended v2.5 paths after negative same-contract evidence. Historical Triton rows remain evidence, not recommendation. |
| 5 | Claude already supplied a v2.6 reference doc. | `v2_6_roadmap()` indexes the Claude v2.6 Numba-first-class reference report. |
| 6 | Close v2.5 and make wording consistent. | Current architecture, support matrix, partner-boundary docs, readiness validations, and tests now carry the same partner-choice cleanup. |
| 7 | Begin v2.6. | `v2_6_roadmap()` starts v2.6 with N-0 neutral seam cleanup, then a Numba first-class demonstrator path. |

## What Changed

Code/policy:

- `src/rtdsl/v2_5_execution_path_policy.py`
  - Added user-owned partner choice, benchmark-reference role, supported-partner duty, generic-engine boundary, and paused Triton role.
- `src/rtdsl/v2_5_partner_selection_guidance.py`
  - Added `v2_5_partner_choice_cleanup_policy()` and validator.
  - Preserved old Triton negative-evidence rows as historical evidence.
  - Added explicit user-choice and benchmark-recommendation metadata to the guidance packet.
- `src/rtdsl/v2_6_roadmap.py`
  - Added the v2.6 kickoff roadmap with N-0 through N-4 sequencing.
  - Blocks release, speedup, true-zero-copy, automatic partner selection, automatic Triton, Numba speedup, and app-specific engine claims.
- `src/rtdsl/v2_5_internal_readiness.py`
  - Indexes this report.
  - Adds the partner-choice cleanup policy and v2.6 roadmap to core validations.
  - Adds `begin_v2_6_neutral_seam_numba_partner_lane_after_goal2989` as an allowed next action.

Learner-facing docs:

- `docs/current_architecture.md`
  - Replaced "choose the partner by evidence" wording with explicit user-owned partner choice and benchmark-evidence recommendations.
- `docs/current_main_support_matrix.md`
  - Reworded partner continuation rows so benchmark recommendations do not look like hidden dispatch.
- `docs/partner_acceleration_boundaries.md`
  - Added a post-Goal2989 cleanup note and marked older Triton-first notes as historical planning context.

Tests:

- `tests/goal2978_primitive_first_v2_5_closeout_policy_test.py`
  - Updated existing v2.5 closeout expectations to the user-choice wording.
- `tests/goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_test.py`
  - Added the explicit closeout/kickoff gate.

## v2.6 Starting Position

v2.6 starts from the following design point:

| Step | Meaning | Exit Gate |
| --- | --- | --- |
| N-0 | Neutral-buffer-seam cleanup | CuPy and Numba CUDA arrays pass through a neutral descriptor without a torch conversion on the data path; copy/borrow status is runtime-observed and labeled. |
| N-1 | Numba op coverage for one demonstrator | Only the ops used by the chosen benchmark app gain Numba coverage; each has reference parity. |
| N-2 | Benchmark app Numba path | One benchmark app routes a real continuation through user-selected Numba and matches CPU reference. |
| N-3 | Conformance/readiness refresh | Demonstrated Numba ops carry runtime conformance while release conformance remains false. |
| N-4 | Honest closeout line | Support is stated as correctness and choosability, not performance. |

This is deliberately not a Triton-first lane. Triton can return later only with
new same-contract evidence from a user-selected path.

## Claim Boundary

Goal2989 does not authorize:

- v2.5 release;
- v2.6 release;
- release tags;
- public speedup wording;
- broad RT-core speedup wording;
- whole-app speedup wording;
- true-zero-copy wording;
- package-install wording;
- automatic partner selection;
- automatic Triton selection;
- Numba speedup wording;
- app-specific native engine logic.

## Validation

Planned focused gate:

```powershell
$env:PYTHONPATH="src;."
py -3 -m py_compile src\rtdsl\v2_5_execution_path_policy.py src\rtdsl\v2_5_partner_selection_guidance.py src\rtdsl\v2_5_internal_readiness.py src\rtdsl\v2_6_roadmap.py tests\goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_test.py
py -3 -m unittest tests.goal2989_v2_5_partner_choice_cleanup_and_v2_6_kickoff_test tests.goal2978_primitive_first_v2_5_closeout_policy_test tests.goal2981_v2_5_closeout_positioning_and_external_review_packet_test tests.goal2806_v2_5_internal_readiness_packet_test
```
