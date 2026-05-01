# Goal1165 Local RTX App Performance Follow-Up

Date: 2026-04-30

## Scope

This local follow-up addresses the three actionable findings from Goal1164 before another paid RTX pod run:

- ANN candidate search timed out at 65,536 copies because the app-level correctness oracle scaled as a full query-by-candidate loop.
- Robot collision timed out at the largest generated pose scale because the app computed CPU any-hit oracle rows before entering the prepared OptiX summary path.
- Polygon Jaccard failed or overflowed at unsafe chunk sizes; Goal1164 showed safe 8,192-copy chunk sizes in the 512-4096 range.

## Changes

### ANN candidate search

`examples/rtdl_ann_candidate_app.py` now validates the prepared OptiX candidate-threshold decision with `expected_tiled_candidate_threshold(...)` for the authored tiled fixture instead of running `candidate_threshold_oracle(...)` over the fully expanded query and candidate arrays. This preserves correctness for the deterministic fixture while removing the accidental O(copies^2) local validation work from the prepared OptiX path.

### Robot collision screening

`examples/rtdl_robot_collision_screening_app.py` no longer computes CPU oracle rows before prepared OptiX summary dispatch. For generated scaled pose fixtures, `prepared_pose_flags` uses the fixture's analytic even/odd collision pattern as validation. The app also exposes `--skip-validation` for prepared OptiX summary timing diagnostics; skipped validation is explicit in JSON via `validation_mode: skipped` and `matches_oracle: null`.

### Polygon Jaccard profiler

`scripts/goal877_polygon_overlap_optix_phase_profiler.py` now defaults `--chunk-copies` to `512` and documents the Goal1164 evidence: Jaccard at 8,192 copies passed at 512-4096, failed parity at 256, and overflowed capacity at 8192. This does not fully solve arbitrary chunk-boundary correctness, but it prevents the profiler's default from selecting a known-bad scale.

### RTX pod runbook

`docs/rtx_cloud_single_session_runbook.md` now records the concrete Goal1164 pod setup:

- driver `550.127.05` needs OptiX headers `v8.0.0`;
- OptiX 8.1/9.1 headers produced `Unsupported ABI version`;
- CUDA 13 driver/header mismatch required the primary-context runtime patch;
- the validated path used `RTDL_OPTIX_PTX_COMPILER=nvcc` and `/usr/local/cuda/bin/nvcc`, not NVRTC.

## Verification

Focused local tests:

```text
PYTHONPATH=src:. python3 -m unittest \
  tests.goal880_ann_candidate_threshold_rt_core_subpath_test \
  tests.goal953_robot_native_continuation_metadata_test \
  tests.goal701_robot_collision_compact_output_test \
  tests.goal877_polygon_overlap_optix_phase_profiler_test -q

Ran 23 tests in 1.007s
OK
```

## Boundaries

- This goal is a local pre-cloud fix. It does not produce new RTX timing artifacts.
- ANN and robot still need a new pod run to confirm large-scale timing improvement.
- Polygon Jaccard still needs a true chunk-boundary/capacity design before arbitrary chunk sizes can be claimed safe.
- `--skip-validation` artifacts are timing diagnostics only unless paired with a separate same-source correctness artifact.
