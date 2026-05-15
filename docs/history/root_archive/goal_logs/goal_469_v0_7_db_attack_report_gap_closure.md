# Goal 469: v0.7 DB Attack-Report Intake And Local Gap Closure

Date opened: 2026-04-16

## Purpose

Respond to the external v0.7 DB attack report at:

- `/Users/rl2025/claude-work/rtdl-2026-04-16b/docs/reports/test_v07_db_attack_report_2026-04-16.md`

The goal is to preserve the report, preserve its test artifact, close the
actionable local gaps, and classify the Linux-only gaps against already
recorded Linux validation gates.

## Scope

In scope:

- preserve the external report under `docs/reports/`
- preserve the external 105-test attack suite under `tests/`
- add local regression coverage for:
  - empty denormalized DB inputs
  - float-bound `between`
  - alternate integer `grouped_sum` value fields
  - large boundary row counts
  - repeated kernel compilation cleanup after success and failure
- update the external tester intake ledger
- obtain 2-AI consensus before calling the goal closed

Out of scope:

- retesting Linux PostgreSQL in this local goal
- retesting Embree/OptiX/Vulkan on macOS
- widening `v0.7` beyond the bounded Goal 416 DB workload contract
- staging, committing, tagging, merging, or releasing

## Acceptance Bar

- `tests.test_v07_db_attack` passes locally.
- `tests.goal469_v0_7_db_attack_gap_closure_test` passes locally.
- Prior Linux-only gaps are explicitly mapped to existing Linux evidence rather
  than silently ignored.
- The report and test artifact are preserved in the repo worktree.
- At least one external-style AI review accepts the closure.
