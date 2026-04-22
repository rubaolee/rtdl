# Goal753 Gemini Flash OptiX Pose-Flags Candidate Review

## Reviewer

- Reviewer: Gemini 2.5 Flash CLI on macOS
- Requested by: Mac/Linux Codex controller
- Scope: candidate patch for prepared OptiX 2D any-hit pose flags in the robot
  collision app

## Verdict

ACCEPT.

## Findings

1. The C ABI shape
   `rtdl_optix_pose_flags_prepared_ray_anyhit_2d_packed(...)` matches the
   requested prepared-scene / prepared-rays / per-ray pose-index / per-pose flag
   contract.
2. The OptiX kernel logic is appropriate for the candidate summary path:
   raygen checks the pose-index bounds and uses `atomicExch` to set a
   per-pose `uint32_t` flag when any accepted ray hit occurs.
3. The Python wrapper validation is robust: it rejects negative pose counts,
   mismatched pose-index lengths, and out-of-range pose indices, while empty
   inputs return all-False flags without requiring a native library.
4. The robot app boundary is honest: `prepared_pose_flags` returns only
   pose-level collision flags and explicitly omits edge-level witnesses.
5. The tests cover the important surfaces: portable validation for empty and
   invalid inputs, CLI exposure, and native Linux validation against CPU
   reference rows when the OptiX symbol is available.

## Boundary

The Linux native validation cited in the request used a GTX 1070. That is
native OptiX correctness and whole-call evidence, not RTX RT-core speedup
evidence.
