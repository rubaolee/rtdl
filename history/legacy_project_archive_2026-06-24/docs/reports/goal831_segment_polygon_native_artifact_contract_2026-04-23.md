# Goal831 Segment/Polygon Native Artifact Contract

Date: 2026-04-23

## Purpose

Goal831 prepares the deferred segment/polygon native OptiX gate for a future
single-session RTX cloud run. Before this goal, the Goal807 strict gate could
emit JSON, but the artifact did not carry the same machine-readable claim
contract used by the active RTX profilers, and the post-cloud artifact analyzer
did not understand the segment/polygon gate artifact.

## Changed Files

- `/Users/rl2025/rtdl_python_only/scripts/goal807_segment_polygon_optix_mode_gate.py`
- `/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py`
- `/Users/rl2025/rtdl_python_only/tests/goal807_segment_polygon_optix_mode_gate_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal831_segment_polygon_native_artifact_contract_test.py`

## Contract Added

Goal807 now emits:

- `schema_version: goal831_segment_polygon_native_gate_contract_v1`
- `cloud_claim_contract.claim_scope`
- `cloud_claim_contract.non_claim`
- `cloud_claim_contract.required_phase_groups`
- `cloud_claim_contract.required_record_labels`
- `cloud_claim_contract.cloud_policy`

The required record labels are:

- `cpu_python_reference`
- `optix_host_indexed`
- `optix_native`

PostGIS remains optional and is used when available.

## Artifact Analyzer Update

`scripts/goal762_rtx_cloud_artifact_report.py` now recognizes
`segment_polygon_hitcount` artifacts and extracts:

- strict pass/failure count;
- CPU reference timing;
- OptiX host-indexed timing;
- OptiX native timing/status/parity;
- optional PostGIS timing/parity;
- cloud contract status.

If the artifact lacks the required claim contract or required phase keys, the
Goal827 fail-closed behavior still returns `needs_attention`.

## Boundaries

This does not promote segment/polygon into the active RTX manifest. It remains a
deferred readiness gate. It is not a pair-row any-hit acceleration claim, not
default public app behavior, not a road-hazard whole-app speedup claim, and not
a public RTX speedup claim.

## Verification

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal831_segment_polygon_native_artifact_contract_test \
  tests.goal807_segment_polygon_optix_mode_gate_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result:

```text
Ran 20 tests
OK
```

Pre-cloud readiness gate:

```text
PYTHONPATH=src:. python3 scripts/goal824_pre_cloud_rtx_readiness_gate.py \
  --output-json docs/reports/goal824_pre_cloud_rtx_readiness_gate_2026-04-23.json
```

Result: `valid: true`.

## Consensus

Goal831 has 2-AI consensus:

- Codex: `ACCEPT`
- Gemini 2.5 Flash: `ACCEPT`

Claude was attempted, but the CLI reported:

```text
You've hit your limit · resets 3pm (America/New_York)
```

Consensus ledger:

- `/Users/rl2025/rtdl_python_only/docs/reports/goal831_two_ai_consensus_2026-04-23.md`

## Verdict

Goal831 is complete locally. No cloud pod was started.
