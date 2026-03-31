# Goal 15 Spec

Date: `2026-03-31`
Author: `Codex`

## Goal

Use Claude to review the just-finished Goal 14 state and design a pure C/C++ + Embree comparison path against RTDL+Embree.

The purpose is:

- verify correctness of the current RTDL+Embree Section 5.6 path,
- compare performance between RTDL+Embree and direct C/C++ + Embree programs,
- document the comparison honestly,
- and close the goal only after Codex + Claude agree, followed by a Gemini-written final report.

## Scope

In scope:
- Claude review of current docs/code relevant to Goal 14 and Section 5.6
- Claude-authored pre-action report and revision/implementation plan
- later pure C/C++ + Embree benchmark programs for selected workloads
- correctness comparison against RTDL+Embree outputs
- performance comparison against RTDL+Embree timings
- iterative Codex review of Claude's code and reports
- final Claude consensus
- final Gemini report after Codex + Claude closure

Out of scope for the first step:
- NVIDIA / OptiX work
- new RTDL workload features
- pretending the current Goal 14 PIP profile is already solved

## Required workflow

1. Claude first reviews and writes a pre-action report plus plan.
2. Codex reviews Claude's plan.
3. Only after Codex + Claude consensus do we begin implementation.
4. Claude's code and results must then be reviewed iteratively.
5. Goal is closed only after Codex + Claude agree.
6. Then Gemini writes the final report for the goal.

## Initial comparison target

Start with Section 5.6 analogue workloads already present in RTDL:
- `lsi`
- `pip`

The likely comparison question is:
- how much of the current runtime cost comes from RTDL/Python-side orchestration versus direct C/C++ Embree execution?

## Acceptance criteria for the current pre-action step

- Claude produces a technically concrete review and plan
- the plan states what to implement first in pure C/C++ + Embree
- the plan states how correctness will be compared against RTDL+Embree
- the plan states how performance will be compared fairly
- Codex reviews the plan and either agrees or requests revision
