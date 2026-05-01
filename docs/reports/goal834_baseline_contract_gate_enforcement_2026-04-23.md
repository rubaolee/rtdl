# Goal834 Baseline Contract Gate Enforcement

Date: 2026-04-23

## Purpose

Goal832 added `baseline_review_contract` to the RTX benchmark manifest. Goal834
enforces that contract in the local pre-cloud gate, carries it through cloud
runner summaries, and makes the post-cloud artifact report fail closed when a
non-dry-run artifact row lacks a valid baseline-review contract.

This prevents a future cloud run from producing timing artifacts that look
claim-reviewable while lacking comparable baseline requirements.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal824_pre_cloud_rtx_readiness_gate.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal761_rtx_cloud_run_all.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py`
- `/Users/rl2025/rtdl_python_only/tests/goal824_pre_cloud_rtx_readiness_gate_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal761_rtx_cloud_run_all_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal762_rtx_cloud_artifact_report_test.py`

## Enforcement Added

### Goal824 Pre-Cloud Gate

The manifest check now validates every active and deferred manifest entry has a
baseline-review contract with:

- `status`
- `minimum_repeated_runs`
- `requires_correctness_parity`
- `requires_phase_separation`
- `forbidden_comparison`
- `comparable_metric_scope`
- `required_baselines`
- `required_phases`
- `claim_limit`

The gate returns invalid if the contract is missing, malformed, lacks required
baselines/phases, or does not require correctness parity and phase separation.

### Goal761 Cloud Runner

Each runner result row now preserves the manifest entry's
`baseline_review_contract`, so the post-cloud analyzer has the same comparison
contract that existed at manifest time.

### Goal762 Artifact Report

The artifact analyzer now:

- checks `baseline_review_contract`;
- records `baseline_review_contract_status`;
- exposes comparable metric scope and claim limit in markdown;
- returns `needs_attention` for non-dry-run rows missing a valid baseline
  contract.

Dry-run rows remain valid without artifacts because no benchmark claim evidence
is expected from dry-runs.

## Boundaries

Goal834 does not start cloud, run performance benchmarks, authorize public RTX
speedup claims, or promote deferred apps. It only makes the local and
post-cloud review pipeline stricter.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal762_rtx_cloud_artifact_report_test
```

Result:

```text
Ran 14 tests
OK
```

```text
python3 -m py_compile \
  scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  scripts/goal761_rtx_cloud_run_all.py \
  scripts/goal762_rtx_cloud_artifact_report.py \
  tests/goal824_pre_cloud_rtx_readiness_gate_test.py \
  tests/goal761_rtx_cloud_run_all_test.py \
  tests/goal762_rtx_cloud_artifact_report_test.py
```

Result: OK.

## Consensus

Goal834 has 2-AI consensus:

- Codex: `ACCEPT`
- Gemini 2.5 Flash: `ACCEPT`

Claude was attempted, but the CLI reported:

```text
You've hit your limit · resets 3pm (America/New_York)
```

Consensus ledger:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal834_two_ai_consensus_2026-04-23.md`

## Verdict

Goal834 is locally implemented and accepted by 2-AI consensus.
