# Goal 170: Linux Backend Small Demo Artifacts

## Objective

Produce small, honest Linux demo artifacts for the orbiting-star 3D demo line on
the two GPU-facing backends already closed in Goal 169:

1. Vulkan
2. OptiX

This goal is not a performance or production-movie claim. It exists to ensure
that both Linux GPU backends have saved, viewable demo artifacts in addition to
the compare-smoke summaries.

## Accepted Scope

- keep the Linux host as the execution platform:
  - `lestat@192.168.1.20`
- use small scene sizes only
- require compare-backend parity against `cpu_python_reference`
- save tiny replay artifacts:
  - `summary.json`
  - `frame_000`
  - `frame_001`
  - two-frame GIF
- preserve honesty that the Windows Embree movie remains the premier public
  visual artifact

## Out of Scope

- Linux 4K movie production
- replacing the Windows Embree ad artifact
- strong Linux GPU performance claims
- any claim that RTDL has become a general rendering engine

## Success Criteria

- Linux Vulkan small demo run matches `cpu_python_reference`
- Linux OptiX small demo run matches `cpu_python_reference`
- both backends have copied-back local repo artifacts
- goal package records the bounded artifact role honestly
