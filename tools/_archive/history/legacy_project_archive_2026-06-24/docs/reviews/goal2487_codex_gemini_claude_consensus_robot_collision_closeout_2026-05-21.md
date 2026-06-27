# Goal2487 Consensus: Robot Collision Project Closeout

Date: 2026-05-21

Consensus: Approved

Goal2487 is complete.

## Reviewed Artifacts

- `docs/reports/goal2484_robot_collision_prepared_reuse_2026-05-21.md`
- `docs/reports/goal2485_robot_collision_performance_matrix_2026-05-21.md`
- `docs/reports/goal2485_robot_collision_perf_matrix_local_2026-05-21.json`
- `docs/reports/goal2485_robot_collision_perf_matrix_pod/summary.json`
- `docs/reports/goal2486_robot_collision_continuous_feasibility_2026-05-21.md`
- `docs/reports/goal2487_robot_collision_project_closeout_2026-05-21.md`
- `docs/reviews/goal2487_gemini_review_robot_collision_closeout_2026-05-21.md`
- `docs/reviews/goal2487_claude_review_robot_collision_closeout_2026-05-21.md`
- `examples/v2_0/research_benchmarks/robot_collision/rtdl_robot_collision_benchmark_app.py`
- `tests/goal2484_robot_collision_prepared_reuse_test.py`
- `tests/goal2485_robot_collision_performance_matrix_test.py`
- `tests/goal2486_robot_collision_continuous_feasibility_test.py`
- `tests/goal2487_robot_collision_project_closeout_test.py`

## Consensus Finding

Codex, Gemini, and Claude agree that Goals2484-2487 can close the first
robot-collision benchmark campaign.

The campaign successfully forced a reusable RTDL runtime pattern:

```text
prepared static scene + changing query batches + compact byte flags
```

The native engine boundary remains app-agnostic. Application semantics remain in
Python, and the native Embree/OptiX paths do not expose robot, link, pose,
planner, or collision APIs.

## Review Results

Gemini:

- Verdict: Approved
- Blocking Issues: None
- Main non-blocking notes: consensus file was not yet present during review;
  the review placeholders were observed while the review workflow was still in
  progress.

Claude:

- Verdict: Approved
- Substantive Blocking Issues: None
- Process blockers observed during review: Gemini review, Claude review, and
  consensus files were not yet complete. Those are now resolved by this file and
  the saved review artifacts.
- Main non-blocking notes: clarify cached `prepare_build_seconds_constant`,
  acknowledge dirty-tree pod disclosure, and update stale CLI wording.

Codex disposition:

- Wrote this consensus file after both reviews existed.
- Updated the Goal2487 report status to complete with consensus.
- Clarified that `prepare_build_seconds_constant` is cached prepared-handle
  metadata, not repeated rebuild timing.
- Updated the benchmark CLI description to cover CPU, prepared, and matrix modes.
- Left the pod dirty-tree disclosure intact because it records prior-goal local
  state honestly and does not affect the Goal2484/2485 app-level changes.

## Accepted Evidence

- Goal2484 defines the prepared repeat protocol: 7 default repeats, 2 warmup
  rows, and tail medians over measured rows.
- Goal2484 records prepared run indices, prepared scene reuse, stable
  signatures, query input sequence reuse, and the current lack of native
  query/output buffer reuse.
- Goal2485 local matrix records CPU reference and Embree prepared rows.
- Goal2485 pod matrix records CPU reference, Embree prepared, and OptiX prepared
  rows on NVIDIA RTX A5000.
- Pod `make build-optix` returned 0.
- Pod OptiX prepared row matched the Goal2481 probe reference across measured
  rows.
- Goal2486 correctly defers continuous/swept collision implementation.
- Goal2486 preserves Python ownership of continuous-collision policy.
- Goal2487 records the campaign's RTDL design value and deferred work.

## Claim Boundary

The closeout still does not claim:

- paper reproduction;
- authors-code comparison;
- public speedup;
- exact solid contact;
- continuous or swept collision support;
- native robot, link, pose, planner, or collision APIs;
- package-install support;
- release/tag action.

## Next Step

The robot-collision first-pass campaign is closed. Follow-on work should target
generic query-buffer reuse or device-column handoff for the segment-probe path,
not robot-specific native code.
