# Goal 165: Spinning-Ball 3D OptiX Animation Variants

## Why

Goal 164 closed the first true 3D spinning-ball backend line with row-level
Linux parity across all four backends. The demo runs and the parity is clean.

The next step is to polish and validate the visual animation story by running
three named spin-speed variants on the OptiX backend on Linux and capturing the
results as a concrete animation evidence package.

This gives the v0.3 visual-demo line a real multi-variant animation story that
can be referenced in docs, reviews, and future work.

## Goal

Produce and validate Linux OptiX animation variants for three spin-speed cases:

- `current_spin`: spin_speed = 1.1 (default, existing demo speed)
- `slower_spin`: spin_speed = 0.35 (perceptibly slower rotation)
- `no_spin`: spin_speed = 0.0 (static surface, pure lighting animation)

Each variant:

- runs on OptiX backend on Linux
- compares against `cpu_python_reference` per-frame
- writes PPM frame sequence to a build artifact directory
- reports frame parity result and query-share

## Core Architectural Boundary

Same as Goal 161 and 164:

- RTDL owns the heavy ray/triangle hit-count query work per frame
- Python owns scene setup, spin-phase parameterization, shading, and frame
  writing
- OptiX is the primary backend being exercised here
- `cpu_python_reference` is the parity oracle

## Scope

This goal covers:

- running the existing demo with three spin-speed arguments on Linux/OptiX
- capturing frame parity and query-share per variant
- writing a bounded honest report with the Linux results
- preparing a concise handoff package ready for 2+ AI consensus review

This goal does not cover:

- changes to the RTDL runtime or backend code
- new workload types
- broad visual polish or shader redesign
- video encoding (PPM frames are the artifact)

## Spin Variant Definitions

| Variant        | spin_speed | Notes                                     |
|----------------|-----------|-------------------------------------------|
| `current_spin` | 1.1       | Default; ball rotates one full turn in ~0.9 phase units |
| `slower_spin`  | 0.35      | Perceptibly slower, good for examining shading detail |
| `no_spin`      | 0.0       | Surface is static; only lights animate   |

## Run Parameters

Two-tier design:

**Parity tier** (all three variants, compare backend active):

- resolution: 64 × 64
- latitude bands: 12
- longitude bands: 24
- frame count: 4
- backend: `optix`
- compare backend: `cpu_python_reference`

**Full-resolution tier** (all three variants, no comparison):

- resolution: 192 × 192
- latitude bands: 32
- longitude bands: 64
- frame count: 8
- backend: `optix`
- compare backend: `none` (parity already proven in tier 1)

The parity tier is the correctness evidence. The full-resolution tier produces
the visual animation artifact. Running `cpu_python_reference` at 192×192 with 8
frames per variant is prohibitively slow; the two-tier split is the practical
approach.

## Success Criteria

- All three variants run to completion on Linux with OptiX
- Per-frame parity against `cpu_python_reference` is `true` for every frame in
  all three variants
- Query share is reported and is plausible (non-trivial)
- PPM frames are written to build artifact directories
- Report is honest: platform, backend, and parity results are explicit
- Package includes at least one Claude or Gemini review before closure

## Acceptance

- the goal charter exists in this repo
- a bounded Linux run report exists in `docs/reports/`
- the report includes per-frame parity for all three variants
- the report is honest about platform (Linux) and backend (OptiX)
- the package has `2+` AI review coverage before closure
