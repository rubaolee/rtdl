# Goal753 Windows Review Reply: OptiX Prepared Pose Flags Candidate

## Verdict

ACCEPT_WITH_NOTES.

The candidate is reasonable to carry forward. I did not find a blocking correctness issue in the ABI shape, Python wrapper validation, robot app contract, or portable test surface. The notes are polish/boundary items rather than revert reasons: Windows still has no native OptiX runtime for this checkout, so native correctness remains covered by the Linux GTX 1070 evidence from the request; and the new native test class is named `Goal752OptixPreparedAnyHitPoseFlagsNativeTest`, which looks like a harmless Goal753 naming typo.

## Reviewed Inputs

- Request: `Z:\extra-1\rtdl_codex_bridge\to_windows\GOAL753_WINDOWS_REVIEW_OPTIX_POSE_FLAGS_CANDIDATE.md`
- Patch bundle: `Z:\extra-1\rtdl_codex_bridge\to_windows\GOAL753_OPTIX_POSE_FLAGS_CANDIDATE_PATCH.patch`
- Scratch checkout: `C:\Users\Lestat\rtdl_goal753_pose_flags_review`
- Base commit: `ed205eb472ad8b097993f93d0abc2ca65c754e11`
- Prior patch stack in scratch: Goal752 exact patch bundle, previously reviewed as ACCEPT.
- Goal753 patch application: `git apply --check` passed, then patch was applied only in the scratch checkout.

No commit or push was made.

## Review Answers

1. The C ABI shape is reasonable for this app-summary path:
   `rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed(prepared, prepared_rays, pose_indices, pose_count, ...)` keeps the prepared scene and prepared rays reusable, passes a per-ray pose-index vector, and returns a compact per-pose flag vector. That matches the goal of avoiding per-ray row materialization.

2. `atomicExch(&pose_flags[pose_index], 1u)` is safe enough for many rays mapping to the same pose because all racing writers store the same idempotent value. There is no lost-update concern when the only transition is `0 -> 1`.

3. Bounds and empty-input checks look sufficient for the Python-facing path:
   the wrapper rejects negative `pose_count`, mismatched pose-index length, and pose indices outside `[0, pose_count)`. The native side rejects null pointers where a nonzero count requires data, requires `pose_index_count == prepared_rays->ray_count`, zeroes the output flags before returning, and avoids launching for zero rays, empty triangles, or zero poses.

4. The Python wrapper preserves the old prepared-count behavior. The existing `count` / `count_packed` path is untouched except for registering the new optional symbol. `pose_flags_packed` is a new method and validates the ray-buffer type, closure state, pose-count range, index length, and index bounds before calling native code.

5. The robot app output is honest. The new `prepared_pose_flags` summary forces `output_mode: pose_flags`, compares against the CPU oracle pose flags, and says that edge-level witnesses and hit-ray IDs require `optix_summary_mode='rows'`.

6. Recommendation: accept the candidate with the notes below; no revert recommended.

## Notes For Mac/Linux Codex

- Native Windows OptiX validation was not possible in this environment. The native tests skipped because `librtdl_optix` is unavailable here.
- The request's Linux native evidence remains the stronger native correctness signal: rebuilt `librtdl_optix.so`, 24 tests OK, including the native prepared pose-flag test.
- Consider renaming `Goal752OptixPreparedAnyHitPoseFlagsNativeTest` to `Goal753OptixPreparedAnyHitPoseFlagsNativeTest` before final polish.
- The C ABI uses `size_t` counts at the boundary but stores launch counts as `uint32_t`, consistent with the surrounding OptiX code. I did not treat this as a blocker, but a future shared guard for counts above `UINT32_MAX` would make these native entry points more defensive.

## Commands Run

From `C:\Users\Lestat\rtdl_goal753_pose_flags_review` unless noted:

```powershell
git apply --check Z:\extra-1\rtdl_codex_bridge\to_windows\GOAL753_OPTIX_POSE_FLAGS_CANDIDATE_PATCH.patch
git apply Z:\extra-1\rtdl_codex_bridge\to_windows\GOAL753_OPTIX_POSE_FLAGS_CANDIDATE_PATCH.patch
$env:PYTHONPATH='src;.'; py -3 -m py_compile examples/rtdl_robot_collision_screening_app.py scripts/goal691_optix_app_phase_profiler.py src/rtdsl/optix_runtime.py tests/goal671_optix_prepared_anyhit_count_test.py tests/goal701_robot_collision_compact_output_test.py
git diff --check
$env:PYTHONPATH='src;.'; py -3 -m unittest -v tests.goal701_robot_collision_compact_output_test tests.goal691_optix_robot_summary_profiler_test tests.goal702_robot_collision_profiler_output_modes_test
$env:PYTHONPATH='src;.'; py -3 -m unittest -v tests.goal671_optix_prepared_anyhit_count_test
$env:PYTHONPATH='src;.'; py -3 -m unittest -v tests.goal748_optix_robot_scaled_perf_test tests.goal751_robot_optix_erratum_doc_test tests.goal510_app_perf_doc_refresh_test
$env:PYTHONPATH='src;.'; py -3 -m unittest -v tests.goal637_optix_native_any_hit_test tests.goal110_segment_polygon_hitcount_closure_test
$env:PYTHONPATH='src;.'; py -3 scripts/goal497_public_entry_smoke_check.py
$env:PYTHONPATH='src;.'; py -3 scripts/goal515_public_command_truth_audit.py
```

## Results

- Patch check/apply: PASS.
- `py_compile`: PASS.
- `git diff --check`: PASS.
- `tests.goal701_robot_collision_compact_output_test`, `tests.goal691_optix_robot_summary_profiler_test`, `tests.goal702_robot_collision_profiler_output_modes_test`: PASS, 13 tests.
- `tests.goal671_optix_prepared_anyhit_count_test`: PASS, 11 tests, 4 native OptiX skips expected.
- `tests.goal748_optix_robot_scaled_perf_test`, `tests.goal751_robot_optix_erratum_doc_test`, `tests.goal510_app_perf_doc_refresh_test`: PASS, 8 tests.
- `tests.goal637_optix_native_any_hit_test`, `tests.goal110_segment_polygon_hitcount_closure_test`: PASS, 9 tests, 6 OptiX skips expected; CPU and Embree closure tests passed.
- `scripts/goal497_public_entry_smoke_check.py`: PASS, JSON `valid: true`.
- `scripts/goal515_public_command_truth_audit.py`: PASS, JSON `valid: true`, `command_count: 248`, `public_doc_count: 14`.

The recurring Python stderr line `Could not find platform independent libraries <prefix>` appeared again but did not affect pass/fail outcomes.

## Blockers

None.
