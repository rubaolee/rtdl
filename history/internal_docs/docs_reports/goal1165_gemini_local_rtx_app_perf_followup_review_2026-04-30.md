# Goal1165 Gemini Local RTX App Performance Follow-Up Review

Date: 2026-04-30
Reviewer: Gemini CLI

## Verdict: ACCEPT

The changes for Goal1165 are technically justified, honest, and effectively resolve the scaling bottlenecks identified during the Goal1164 RTX pod validation.

## Technical Analysis

### 1. ANN Candidate Search
The transition to `expected_tiled_candidate_threshold` is correct for the `make_ann_case` fixture. The fixture tiles copies with a 12-unit offset, which is much larger than the 0.2-unit candidate radius, ensuring that points in different tiles do not interact. Computing the oracle for a single tile and projecting the results to all copies reduces the validation complexity from $O(\text{copies}^2)$ to $O(\text{copies})$, which is critical for testing scales like 65,536 copies where the previous oracle timed out.

### 2. Robot Collision Screening
The app-level changes are valid for their intended purpose as timing diagnostics.
- Avoiding the CPU oracle before OptiX dispatch prevents unnecessary $O(N)$ work that was stalling the whole-app measurement.
- The analytic validation (`pose_id % 2 == 0`) correctly mirrors the design of the `make_scaled_case` fixture, where collision is deterministically toggled by the pose index.
- The `--skip-validation` flag is implemented with proper metadata tracking (`validation_mode: skipped`), ensuring that performance results are not mistaken for correctness evidence.

### 3. Polygon Jaccard Profiler
Updating the default chunk size to 512 is a reasonable defensive measure. Goal1164 evidence showed that 256 copies missed candidates (likely due to insufficient candidate set coverage across chunk boundaries) and 8192 overflowed capacity. Setting 512 as the default avoids known failure modes while the documentation correctly frames this as a mitigation rather than a final architectural fix for arbitrary chunking.

### 4. RTX Pod Runbook
The documentation updates accurately capture the environmental nuances of the driver 550 / CUDA 13 pod.
- The OptiX 8.0 header pin is a necessary workaround for the `Unsupported ABI version` error.
- The preference for `nvcc` over `NVRTC` for the claim-grade path is justified by the discovered issues with host libc headers and launch-parameter handling.
- The warnings against overclaiming speedups are professional and maintain technical integrity.

## Conclusion
The Goal1165 fixes successfully prepare the codebase for the next iteration of large-scale RTX validation by removing accidental app-level bottlenecks.
