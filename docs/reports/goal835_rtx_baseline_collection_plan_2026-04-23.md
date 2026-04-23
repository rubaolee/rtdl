# Goal835 RTX Baseline Collection Plan

Date: 2026-04-23

## Purpose

Goal835 adds a local generator for the RTX baseline-collection checklist. It
turns the Goal832/Goal834 `baseline_review_contract` fields into a reviewer-
and-runner-facing plan before any future cloud session.

## Files Added

- `/Users/rl2025/rtdl_python_only/scripts/goal835_rtx_baseline_collection_plan.py`
- `/Users/rl2025/rtdl_python_only/tests/goal835_rtx_baseline_collection_plan_test.py`

## Generated Outputs

The script can write JSON and markdown:

```text
PYTHONPATH=src:. python3 scripts/goal835_rtx_baseline_collection_plan.py \
  --output-json docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.json \
  --output-md docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.generated.md
```

The plan covers:

- `5` active RTX manifest entries;
- `3` deferred entries;
- `0` invalid baseline-plan rows;
- required same-semantics baseline families;
- required timing phases;
- claim limits;
- placeholder artifact names for later baseline evidence.

## Boundaries

Goal835 does not start cloud, run benchmarks, promote deferred apps, or
authorize public RTX speedup claims. It is a local checklist and audit aid.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal835_rtx_baseline_collection_plan_test
```

Expected: all tests pass.

Actual result:

```text
Ran 4 tests
OK
```

## Consensus

Goal835 has 2-AI consensus:

- Codex: `ACCEPT`
- Gemini 2.5 Flash: `ACCEPT`

Claude was attempted, but the CLI reported:

```text
You've hit your limit · resets 3pm (America/New_York)
```

Consensus ledger:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_two_ai_consensus_2026-04-23.md`

## Verdict

Goal835 is locally implemented and accepted by 2-AI consensus.
