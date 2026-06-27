# Goal 26: Vision-Alignment Audit and Revision

## Purpose

Goal 26 resets the repository around the current project vision:

- **whole project**: a DSL for non-graphical, re-purposed RT-based applications across diverse RT software and hardware ecosystems
- **v0.1**: a RayJoin-focused vertical slice, currently executable on Embree on this Mac

The goal of this round is not to add a new backend or a new workload. It is to review the whole repository against that framing and revise anything that still reflects an older, narrower, or inconsistent understanding of RTDL.

## Core Review Question

Does the current repository consistently present RTDL as:

1. a long-term multi-backend language/runtime/compiler project, while
2. honestly documenting that the current local executable baseline is Embree-only and RayJoin-focused?

## What Must Be Reviewed

Goal 26 explicitly includes:

- top-level framing docs:
  - `README.md`
  - `docs/vision.md`
  - `docs/v0_1_final_plan.md`
- language/runtime framing docs:
  - `docs/rtdl/`
  - `docs/rtdl_feature_guide.md`
  - `docs/runtime_overhead_architecture.md`
  - `docs/ai_collaboration_workflow.md`
  - `docs/development_reliability_process.md`
- current status/report docs that may still carry outdated framing
- core compiler/runtime code under `src/rtdsl/`
- public API surface in `src/rtdsl/__init__.py`
- current benchmark/reporting entry points under `scripts/`
- history/dashboard artifacts if they now misstate the project vision

## Main Audit Themes

1. **Vision consistency**
   - Does the repo consistently distinguish whole-project vision from v0.1 scope?
   - Are future backend families described honestly as roadmap rather than current support?

2. **Backend abstraction honesty**
   - Does the current IR/runtime story reflect the long-term goal of multiple RT stacks without overstating present generality?
   - Are current backend-specific assumptions labeled clearly?
   - Are structural names such as `RayJoinPlan`, `lower_to_rayjoin`, schema IDs, and `backend="rayjoin"` still acceptable as v0.1-local names, or do they now misframe RTDL at the architecture level?

3. **Application-scope honesty**
   - Does the repo clearly state that RayJoin is the current v0.1 validation target, not the definition of RTDL itself?

4. **Architecture direction**
   - Does the current compiler/runtime design still look compatible with future multi-backend growth?
   - Are there docs/code comments that encode older assumptions that should be revised now?

5. **Report and workflow integrity**
   - Do the reports and dashboards still tell the truth after the project-goal reset?

## Expected Revision Types

Goal 26 may revise:

- project framing docs
- architecture notes
- README and status summaries
- structural names, code comments, and docstrings that overfit RTDL to Embree or RayJoin
- planning docs that no longer match the reset goal hierarchy

Goal 26 should avoid:

- adding major new features
- pretending future backends already exist
- weakening current honesty about the local Embree-only reality

## Explicit Decision Point

Goal 26 must make an explicit decision on structural RayJoin naming in the codebase:

- **rename path**: rename structural names that incorrectly encode RayJoin as a backend or permanent IR identity
- **comment-only path**: preserve the current names for v0.1 compatibility, but document them as temporary RayJoin-slice names rather than whole-project architecture names

This decision must be made deliberately and then applied consistently.

## Historical-Artifact Rule

Unless a historical goal document is still referenced by an active framing doc, the `docs/goal_*` planning files should be treated as archived historical artifacts rather than rewritten as part of Goal 26.

## Acceptance Standard

Goal 26 is complete only if:

- Claude reviews the plan, revisions, and final state and approves the round
- Gemini monitors each major step and agrees the round remains aligned with the stated goal
- the repository ends in a cleaner, more internally consistent state with respect to the whole-project vision and the current v0.1 boundary
