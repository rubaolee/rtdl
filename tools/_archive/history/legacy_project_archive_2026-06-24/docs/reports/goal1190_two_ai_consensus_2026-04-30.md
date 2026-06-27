# Goal1190 Two-AI Consensus

Date: 2026-04-30

## Scope

Goal1190 supersedes the Goal1189 blocked baseline classification for graph and
polygon rows by using public-app Embree summary outputs as same-contract
baseline command shapes.

## Inputs

- Goal1190 supersession manifest:
  `docs/reports/goal1190_next_rtx_pod_contract_manifest_supersession_2026-04-30.md`
- Goal1190 Claude review:
  `docs/reports/goal1190_claude_next_rtx_pod_contract_supersession_review_2026-04-30.md`
- Goal1189 consensus:
  `docs/reports/goal1189_two_ai_consensus_2026-04-30.md`

## Consensus Verdict

`ACCEPT`

Codex and Claude agree that all six remaining public-wording-evidence rows are
now command-complete at the planning level, but every row remains
`local_dry_run_required`. `pod_ready_now` remains `False`.

## Watch Item

The newly unblocked graph and polygon baseline commands redirect public-app
stdout to JSON files. Local dry-run/schema validation must confirm that stdout
is parseable JSON and contains the required comparable phase fields before any
pod executor is built.

## Verification

```bash
PYTHONPATH=src:. python3 scripts/goal1190_next_rtx_pod_contract_manifest_supersession.py
PYTHONPATH=src:. python3 -m unittest \
  tests/goal1190_next_rtx_pod_contract_manifest_supersession_test.py \
  tests/goal1189_next_rtx_pod_contract_manifest_test.py
```

Result: Goal1190 manifest returned `valid: true`; 8 focused tests passed.

## Boundary

This consensus does not authorize release, tagging, public RTX speedup wording,
or a pod run. Next work is local dry-run/schema validation for the six command
pairs.
