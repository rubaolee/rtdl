# Goal835 External Consensus Review Request

Date: 2026-04-23

Please independently review Goal835 in:

`/Users/rl2025/rtdl_python_only`

## Required Verdict

Write one of:

- `ACCEPT`
- `BLOCK`

If `BLOCK`, list exact blocking files and fixes.

## Review Question

Does Goal835 correctly generate a local RTX baseline-collection checklist from
the Goal832/Goal834 manifest contracts without running benchmarks, starting
cloud, promoting deferred apps, or authorizing public RTX speedup claims?

## Files To Read

Report:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.md`

Code:

- `/Users/rl2025/rtdl_python_only/scripts/goal835_rtx_baseline_collection_plan.py`

Tests:

- `/Users/rl2025/rtdl_python_only/tests/goal835_rtx_baseline_collection_plan_test.py`

Generated artifacts:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.json`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.generated.md`

Context:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal832_rtx_baseline_review_contract_2026-04-23.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal834_baseline_contract_gate_enforcement_2026-04-23.md`

## Evidence Commands Already Run

```text
PYTHONPATH=src:. python3 -m unittest -v tests.goal835_rtx_baseline_collection_plan_test
```

Result: `3 tests OK`.

```text
PYTHONPATH=src:. python3 scripts/goal835_rtx_baseline_collection_plan.py --output-json docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.json --output-md docs/reports/goal835_rtx_baseline_collection_plan_2026-04-23.generated.md
```

Result: `status: ok`, `active_count: 5`, `deferred_count: 3`, `invalid_count: 0`.

## Boundaries To Check

- No cloud pod should be started.
- No performance benchmarks should be run.
- Deferred entries must remain deferred.
- The generated plan must be a checklist only, not a speedup claim.
- The plan must preserve required baselines, required phases, and claim limits.
