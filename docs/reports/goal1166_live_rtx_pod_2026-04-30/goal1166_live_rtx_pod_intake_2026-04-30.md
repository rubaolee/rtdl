# Goal1166 Live RTX Pod Intake

Date: 2026-04-30

## Verdict

ENGINEERING ACCEPT, CLAIM-GRADE BLOCKED.

The Goal1166 packet ran successfully on an RTX A5000 pod and confirmed that the
Goal1165 local fixes removed the two practical large-scale blockers from
Goal1164: ANN no longer times out at the 65k packet scale, and robot pose-count
timing no longer spends minutes in CPU validation.

This run is not claim-grade public speedup evidence because the pod tree was
copied from a dirty local working tree rather than a clean git checkout.

## Pod Environment

- Host: `6f66014279a0`
- GPU: NVIDIA RTX A5000
- Driver: `580.126.09`
- CUDA runtime reported by `nvidia-smi`: `13.0`
- Python: `3.12.3`
- Native library: `build/librtdl_optix.so`
- OptiX headers: `/root/vendor/optix-dev`, branch/tag source copied from
  `optix-dev` v8.0.0

## Source Boundary

The pod source tree was copied from local
`/Users/rl2025/rtdl_python_only`; it was not cloned from a clean git commit.

- Local git HEAD at copy time: `d0ebf9d69041cf013b7af4dcb20a570d25d92c3f`
- Local dirty-path count at copy time: `246`
- Local `.rtdl_source_commit` marker:
  `21fa036881bf9a0c806f69c15727d87b482ccfcf`
- Runner source marker used:
  `d0ebf9d69041cf013b7af4dcb20a570d25d92c3f-local-dirty-goal1166`

Boundary: these artifacts are engineering evidence for the Goal1165/Goal1166
fixes. They are not public wording evidence and not release-speedup evidence
until reproduced from a clean source state and reviewed through the usual
claim gate.

## Bootstrap Notes

- `libgeos-dev`, `pkg-config`, build tools, Python dev packages, and
  `cuda-nvrtc-dev-13-0` were installed on the pod.
- A manual direct compile attempt against split OptiX source files failed
  because that is not the repository build contract.
- The repository `make build-optix` path succeeded after installing
  `cuda-nvrtc-dev-13-0`.
- `goal763_rtx_cloud_bootstrap_check.py --skip-build` reported
  `needs_attention` only because this minimal copied tree lacked older
  bootstrap test modules. GEOS, CUDA headers, NVCC, OptiX headers, and the
  native library build were present.

## Packet Results

| Row | Result | Key timing | Boundary |
| --- | --- | ---: | --- |
| `ann_candidate_8192_validation` | pass, `matches_oracle=True` | OptiX query median `0.000623 s`; validation median `0.004669 s` | correctness validation row |
| `ann_candidate_65536_timing` | pass, validation skipped | OptiX query median `0.000963 s` | timing-only row; not correctness proof |
| `robot_pose_flags_32768_validation` | pass, `matches_oracle=True` | OptiX query median `0.051494 s`; CPU oracle validation `112.779003 s` | correctness validation row; shows why validation must be separated |
| `robot_pose_flags_262144_timing` | pass, validation skipped | OptiX query median `0.000443 s`; total `1.352842 s` | timing-only row; not correctness proof |
| `polygon_jaccard_8192_chunk512_validation` | pass | candidate discovery `1.823074 s`; native exact continuation `2.347039 s` | safe chunk validation row |
| `polygon_jaccard_8192_chunk256_diagnostic` | expected non-fatal failure | candidate discovery `1.671872 s`; native exact continuation `2.517094 s` | diagnostic boundary; not a runner failure |

## Conclusions

- Goal1165 fixed the ANN validation scaling bug: the 65k timing row completed
  instead of hitting the prior 600-second timeout.
- Goal1165 fixed the robot timing path: the 262k pose-count row completed
  quickly because CPU oracle validation was correctly skipped for timing-only
  evidence.
- Robot correctness validation is still expensive: 32k validation spent
  `112.779003 s` in CPU oracle validation while the OptiX warm query median was
  `0.051494 s`.
- Jaccard remains bounded by chunk-size semantics: chunk `512` passed and chunk
  `256` failed non-fatally, matching the Goal1166 packet design.
- The next claim-grade run should be from a clean source checkout or a staged
  source archive with an explicit reproducible source manifest.

## Artifacts

- `goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_8192_validation.json`
- `goal1166_post_goal1165_next_rtx_pod_packet/ann_candidate_65536_timing.json`
- `goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_32768_validation.json`
- `goal1166_post_goal1165_next_rtx_pod_packet/robot_pose_flags_262144_timing.json`
- `goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk512_validation.json`
- `goal1166_post_goal1165_next_rtx_pod_packet/polygon_jaccard_8192_chunk256_diagnostic.json`
- `goal1166_live_pod_runner_2026-04-30.log`
- `goal1166_live_pod_bootstrap_2026-04-30/`
- `goal1166_live_pod_source_context_2026-04-30/source_context.md`
