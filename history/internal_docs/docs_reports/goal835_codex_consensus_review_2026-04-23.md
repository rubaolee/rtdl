# Goal835 Codex Consensus Review

Date: 2026-04-23

Reviewer: Codex

## Scope

This review checks whether Goal835 generates a local baseline-collection
checklist from the Goal832/Goal834 manifest contracts without running cloud or
making performance claims.

## Findings

- The new Goal835 script derives its rows from the machine-readable RTX
  manifest, not from duplicated prose.
- The plan covers all `5` active entries and all `3` deferred entries.
- Each row preserves comparable metric scope, required baselines, required
  phases, claim limits, correctness parity, and phase-separation requirements.
- The generated markdown states that public RTX speedup claims require
  same-semantics baseline artifacts, correctness parity, and phase-separated
  timing.
- No cloud command is run, no benchmark is run, and deferred entries remain
  deferred.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal835_rtx_baseline_collection_plan_test
```

Result: `Ran 3 tests ... OK`.

```text
PYTHONPATH=src:. python3 scripts/goal835_rtx_baseline_collection_plan.py --output-json docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.json --output-md docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.generated.md
```

Result: `status: ok`, `active_count: 5`, `deferred_count: 3`, `invalid_count: 0`.

## Verdict

ACCEPT
