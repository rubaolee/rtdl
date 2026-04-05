# Meitner Review: Goal 108 v0.2 Workload Scope Charter

Date: 2026-04-05
Reviewer: Meitner
Status: complete

## Verdict

The charter is an improvement over the loose Goal 107 roadmap, but the first
draft still had a serious loophole at its center. It reduced chaos without yet
eliminating the main escape hatch.

## Criticisms

- The core classification rule was too abstract to enforce consistently.
- “Programmable counting/ranking kernels with geometric candidate structure”
  was still a disguised abstraction bucket for almost anything vaguely
  geometric and reducible.
- Generate-only mode should not sit in the same matrix as workload families.
- “Workload-first” still hedged too much when two in-scope families remained.
- The entry criteria were too easy to satisfy with paperwork.
- The critique document was too weak until it added stronger exclusion logic.

## Strongest Rebuttals

- The charter is materially better than the original roadmap because it
  separates `in_scope`, `experimental`, and `out_of_scope`.
- Declaring v0.2 “workload-first” is the right instinct.
- Keeping generate-only mode out of the in-scope set is the correct move.
- Explicit rejection of arbitrary AI-generated demo accumulation is one of the
  strongest lines in the package.

## Recommendation

Tighten the charter before using it as a real gate:

1. keep only one workload family in core scope
2. move counting/ranking kernels to experimental
3. remove generate-only mode from the workload-family charter
4. add hard gray-area exclusions and a comparative entry rule
