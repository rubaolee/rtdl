# Goal1081 Two-AI Consensus

Date: 2026-04-29

## Verdict

ACCEPT.

## Consensus

Codex implemented and tested the Goal1081 same-scale baseline execution packet.
Claude independently reviewed the bounded goal and accepted it in
`docs/reports/goal1081_claude_review_2026-04-29.md`.

Both reviews agree:

- Facility now has an explicit same-scale baseline command for the 2,500,000-copy RTX timing row.
- Robot now has an explicit same-scale Embree baseline command for the 36,000,000-pose / 4,096-obstacle RTX timing row.
- Barnes-Hut remains blocked from baseline execution and public wording until the 20M validation/intake contract is superseded and reviewed.
- Goal1081 does not run the heavy baselines, does not change public wording, does not authorize release, and does not authorize public RTX speedup claims.

## Verification

Ran:

```bash
PYTHONPATH=src:. python3 scripts/goal1081_same_scale_baseline_execution_packet.py
PYTHONPATH=src:. python3 -m unittest tests.goal1081_same_scale_baseline_execution_packet_test
```

Result: packet valid; 4 tests OK.
