# Goal827 Cloud Artifact Contract Audit

Date: 2026-04-23

## Purpose

Goal827 tightens the post-cloud evidence path. The existing artifact report
summarized timings, but it did not require the new `cloud_claim_contract`
metadata added in Goals825 and 826. That was unsafe because a cloud run could
finish successfully while producing artifacts that were not claim-reviewable.

## Changed File

- `/Users/rl2025/rtdl_python_only/scripts/goal762_rtx_cloud_artifact_report.py`
- `/Users/rl2025/rtdl_python_only/tests/goal762_rtx_cloud_artifact_report_test.py`

## Behavior Added

For non-dry-run cloud artifacts, the report now checks:

- `cloud_claim_contract` exists.
- `cloud_claim_contract.required_phase_groups` exists.
- Every required phase key is present in the relevant artifact phase source.
- Tier-2 service/hotspot artifacts from Goal811 are recognized and summarized.

If the contract is missing, malformed, or missing required phases, the artifact
report returns `needs_attention`.

## App Coverage

The contract check now covers:

- `database_analytics`
- `outlier_detection`
- `dbscan_clustering`
- `robot_collision_screening`
- `service_coverage_gaps`
- `event_hotspot_screening`

The Tier-2 apps remain deferred; this change only makes their future evidence
auditable if they are included in one consolidated cloud batch.

## Cloud Cost Policy

No cloud pod was started. This goal improves the local verifier so the next pod
session can be one batched run with deterministic artifact acceptance checks.

## Verification

Focused tests:

```text
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal827_cloud_artifact_contract_audit_test \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal769_rtx_pod_one_shot_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal826_tier2_phase_profiler_contract_test \
  tests.goal825_tier1_profiler_contract_test
```

Result:

```text
Ran 22 tests in 2.167s
OK
```

Compile check:

```text
python3 -m py_compile \
  scripts/goal762_rtx_cloud_artifact_report.py \
  tests/goal762_rtx_cloud_artifact_report_test.py
```

Result: passed.

## Verdict

Goal827 is complete locally. Post-cloud artifacts now have a stronger contract
audit before any NVIDIA RT-core performance claim can be reviewed.
