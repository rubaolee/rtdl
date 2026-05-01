# Goal858 Codex Review

Verdict: ACCEPT

Reasoning:

- The docs now match the actual app surface instead of implying a simpler
  OptiX story than the code supports.
- The update is honest about the two most important current boundaries:
  - `--require-rt-core` still rejects this family today
  - pair-row native OptiX output still does not exist
- The new test is narrow and useful. It checks exact public phrases for the
  OptiX mode boundary without weakening existing doc-truth tests.

Boundary:

- This is a docs sync goal, not an RT-core promotion goal.
