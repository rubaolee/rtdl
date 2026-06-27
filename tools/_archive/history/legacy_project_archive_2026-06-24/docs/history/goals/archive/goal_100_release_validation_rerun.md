# Goal 100: Release Validation Rerun

## Objective

Run the pre-release validation gate again after the Goal 98 OptiX repair and
Goal 99 OptiX prepared run-1 win.

This goal is the current release-quality health check for the v0.1 package.

## Why this goal exists

The earlier release-validation work predated the final OptiX repair/win package
now published at head `e15ee77`.

So the release gate must be rerun on the repaired head before v0.1 can be
considered ready for final audit and release.

## Required outputs

- one current release-validation report
- one artifact summary package
- explicit pass/fail status for:
  - local preflight
  - clean Linux full matrix
  - focused Linux milestone slice
  - Linux Vulkan slice
  - Goal 51 Vulkan parity ladder
  - backend artifact consistency checks

## Consensus requirement

This goal requires **3-AI review** of the final release-validation package:

- Codex
- Gemini
- Claude

## Acceptance

Goal 100 is done when:

- the rerun package clearly states what was actually revalidated
- the release head passes the chosen high-signal test gate
- the package is reviewed by Codex, Gemini, and Claude
- the final report is honest about what was rerun directly and what remains
  carried by same-head accepted artifacts
