# Goal3683 Next Project Goals After Goal3682

Date: 2026-06-07

## Position

The current direction is agreed:

- RTDL is a language/runtime for making high-performance hardware-RT applications much easier to write.
- The native engine stays generic and app-agnostic.
- Users choose their partner stack. RTDL should provide high-performance support for every partner it claims to support.
- Benchmark apps are not just demos; they are how we reconstruct and strengthen the language/runtime.
- The next performance work should attack major bottlenecks, not minor tuning.

Recent RayJoin full-county work changed the immediate diagnosis. Relation-status columns, boundary ordinals, Numba exact-count continuation, and a resident prepared counter now give exact count `47262` on the A5000 full-county CDB workload:

| Route | Median seconds | Count |
| --- | ---: | ---: |
| all-candidate count-only | `0.000459798` | `47264` |
| one-shot corrected exact Numba count | `0.002809492` | `47262` |
| resident corrected exact Numba count | `0.001527618` | `47262` |

But boundary-status rows are dense (`47241 / 47264`), so relation-status filtering is not the final performance answer. The next real leap is a generic scalar-correction/output-workspace primitive that avoids dense boundary row materialization for scalar count-only workloads.

## Goal 1: Generic Dense-Boundary Exact Scalar Count

Build a generic closed-shape exact scalar-count primitive or native/partner continuation that handles dense boundary-status workloads without materializing a dense boundary row stream.

Acceptance:

- Native ABI and runtime vocabulary remain generic: closed shape, relation status, boundary element, scalar count, correction, workspace.
- No RayJoin, CDB, county, map, GIS policy, or app-specific ownership logic in the native engine.
- Full-county A5000 exact count remains `47262`.
- Same-contract comparison includes Goal3681 resident route as baseline.
- Report separates one-shot and resident prepared timings.
- All claim-boundary flags remain false unless a later reviewed release packet authorizes otherwise.

## Goal 2: Reusable Candidate/Correction Workspace

Generalize reusable output/workspace ownership so repeated workloads can reuse native buffers, launch parameters, and partner-side correction state without reallocation churn.

Acceptance:

- Explicit owner/lifetime API with `close`, context-manager support, and fail-closed overflow semantics.
- Device-resident buffers expose row count, capacity, required capacity, overflow status, device ordinal, and timing.
- Works for RayJoin PIP exact scalar count first, but is named and structured for generic relation/candidate streams.
- Tests verify no partial rows are exposed on overflow.

## Goal 3: Numba Partner Coverage For All Partner-Needed Benchmark Apps

For every benchmark app that needs custom partner logic, provide a Numba-based high-performance reference implementation.

Rationale:

Users should not be forced to write CuPy RawKernel, C++/CUDA, or app-native code to use RTDL seriously. CuPy can remain supported, but Numba must become the default recommended custom-logic partner where custom logic is needed.

Acceptance:

- Produce a table for all 10 benchmark apps:
  - primitives only,
  - Numba continuation,
  - CuPy continuation,
  - no partner needed,
  - not yet covered.
- For any app still requiring CuPy RawKernel, either add a Numba path or document the exact missing primitive/runtime feature.
- Same-contract perf artifacts compare current CuPy and Numba paths where both exist.
- Docs explain that users may still choose CuPy, C/CUDA extensions, or other partners, but RTDL’s reference path must not require raw kernel strings.

## Goal 4: Benchmark Matrix Refresh With Meaningful Runtime Scale

Refresh the benchmark matrix for the 10 benchmark apps with seconds-scale or repeated steady-state measurements, not tiny one-off timings.

Acceptance:

- Each row states:
  - app,
  - contract,
  - backend,
  - partner,
  - dataset,
  - one-shot timing,
  - resident/prepared timing when applicable,
  - correctness oracle,
  - claim boundary.
- RayJoin is summarized both as subcontracts and as an app-level composite score.
- Weak rows are labeled as design gaps, not hidden behind averaging.
- No public speedup or paper-reproduction claim is made without fresh 3-AI consensus.

## Goal 5: RayJoin-Level Generic Primitive Work

Continue RayJoin as the top benchmark application, but implement only generic primitives/contracts.

Near-term targets:

- dense-boundary exact scalar count,
- generic point/closed-shape ambiguity-set derivation,
- generic boundary ownership/tie-break contracts,
- general simple-polygon overlay-area continuation over resident relation streams.

Acceptance:

- Match exact oracle on public CDB slices including full county.
- Compare against project-owned baselines and, when available, RayJoin paper/repo evidence.
- Clearly distinguish RTDL implementation, RayJoin reproduction, and RTDL-beats-RayJoin claims.

## Goal 6: Partner Choice Product Surface

Make the user-facing model simple:

1. Use a built-in RTDL primitive when one fits.
2. If custom logic is required, choose a partner.
3. RTDL provides high-performance reference paths for supported partners.
4. Users can still use their own Python, C/CUDA extensions, CuPy kernels, Numba kernels, or future partners; that logic is outside the native engine.

Acceptance:

- Docs and examples say "user chooses partner"; they do not imply RTDL auto-selects a magic partner.
- Partner capability matrix lists Numba, CuPy, and any other active partner honestly.
- For each benchmark app, docs explain why the recommended implementation uses primitives only, Numba, CuPy, or a fallback.

## Goal 7: AMD HIP RT Preparation

Prepare the project to validate RTDL on AMD HIP RT when AMD GPU cloud is available.

Acceptance:

- HIP RT support matrix names implemented, proof, missing, and frozen surfaces.
- Generic primitive parity plan maps OptiX concepts to HIP RT concepts without app-specific ABI names.
- Build/run checklist for AMD cloud pods is written before renting hardware.
- First AMD validation target is functional parity, then performance.

## Goal 8: Public Documentation Discipline

Keep learner/user docs version-current and not frustrating.

Acceptance:

- Active learner docs show the current recommended RTDL model only.
- Historical/versioned material lives under historical or internal directories.
- Benchmark docs explain how to run examples and how to interpret claim boundaries.
- No release, install, zero-copy, broad RT-core speedup, or paper-reproduction wording appears without current evidence and required consensus.

## Review Rule

- Important engineering goals require Codex plus at least one external AI review.
- Public claims, roadmap changes, release gates, and major performance conclusions require 3-AI consensus.
- Codex plus Codex never counts as independent consensus.

## Immediate Next Goal

Start with Goal 1: generic dense-boundary exact scalar count / reusable correction workspace.

Reason:

It is the clearest current blocker exposed by the latest RayJoin full-county evidence. It directly improves a major benchmark app while also strengthening RTDL as a generic runtime.
