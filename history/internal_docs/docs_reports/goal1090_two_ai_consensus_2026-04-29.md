# Goal1090 Two-AI Consensus

Date: 2026-04-29

## Verdict

ACCEPT.

## Consensus

Codex implemented and tested the robot Embree local baseline runbook. Claude
independently reviewed Goal1090 and accepted it in
`docs/reports/goal1090_claude_review_2026-04-29.md`.

Both reviews agree:

- The runbook is non-cloud/local work for Linux or Windows.
- The step order is smoke, one real chunk, intake, full resumable run, final intake.
- The pose-id offset formula and `RTDL_GOAL1085_*` resume controls are preserved.
- Generating the runbook does not run the heavy baseline.
- Goal1090 does not authorize release, public wording, or any public RTX speedup claim.

Claude noted a tautological validity check. Codex tightened the validity check
before closure by binding the pose-id formula once and requiring skip-existing
controls in the generated commands.

## Verification

Ran:

```bash
PYTHONPATH=src:. python3 scripts/goal1090_robot_embree_local_runbook.py
PYTHONPATH=src:. python3 -m unittest tests.goal1090_robot_embree_local_runbook_test
```

Result: runbook valid; 10 focused tests OK.
