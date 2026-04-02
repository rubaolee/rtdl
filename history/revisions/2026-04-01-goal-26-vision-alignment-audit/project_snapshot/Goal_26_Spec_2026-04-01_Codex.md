# Goal 26 Spec

## Title

Vision-Alignment Audit and Revision

## Source Commit

`669a5a6`

## Goal

Review the whole repository against the current RTDL framing:

- whole-project goal: multi-backend DSL for non-graphical RT applications
- v0.1 goal: RayJoin-focused vertical slice
- current local executable backend: Embree on this Mac

Then revise the repository so the docs, architecture framing, code comments/docstrings, and status artifacts consistently reflect that hierarchy.

## Review/Consensus Rule

- Claude must review and approve Codex work before closure.
- Gemini must monitor each major step and approve the process integrity.

## Initial Audit Focus

1. Project vision vs v0.1 scope consistency
2. RayJoin-specific framing vs general RTDL framing
3. Multi-backend ambition vs current backend reality
4. Architecture notes and code comments that may still overfit the current Embree/RayJoin slice
5. History/status/docs that may still carry older, narrower framing
