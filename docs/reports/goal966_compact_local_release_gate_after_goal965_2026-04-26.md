# Goal966 Compact Local Release Gate After Goal965

Date: 2026-04-26

## Scope

Run a compact local release-facing gate after Goal964 and Goal965, before any
next paid RTX cloud run.

This gate focuses on public docs, example smoke checks, command truth, generated
RTX/cloud manifests, spatial readiness packets, native-continuation schema, and
the accepted Goal962 cloud packet. It is not a full unittest-discovery rerun;
Goal963 already records the latest full-suite pass.

## Initial Invocation Error

The first command used an incorrect test module name:

```text
tests.goal593_public_example_smoke_test
```

That module does not exist. The actual public smoke modules are:

```text
tests.goal512_public_doc_smoke_audit_test
tests.goal513_public_example_smoke_test
```

This was a command-selection error, not a code failure.

## Corrected Gate

Command:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal513_public_example_smoke_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal646_public_front_page_doc_consistency_test \
  tests.goal700_fixed_radius_summary_public_doc_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test \
  tests.goal829_rtx_cloud_single_session_runbook_test \
  tests.goal847_active_rtx_claim_review_package_test \
  tests.goal849_spatial_promotion_packet_test \
  tests.goal860_spatial_partial_ready_gate_test \
  tests.goal862_spatial_rtx_collection_packet_test \
  tests.goal939_current_rtx_claim_review_package_test \
  tests.goal947_v1_rtx_app_status_page_test \
  tests.goal958_public_app_native_continuation_schema_test \
  tests.goal962_next_rtx_pod_execution_packet_test
```

Result:

```text
Ran 76 tests in 10.783s

OK
```

## Additional Checks

Commands:

```bash
git diff --check -- \
  docs/reports/goal964_generated_spatial_gate_resync_2026-04-26.md \
  docs/reports/goal965_goal962_packet_hardening_2026-04-26.md \
  docs/reports/goal962_next_rtx_pod_execution_packet_2026-04-25.md \
  tests/goal962_next_rtx_pod_execution_packet_test.py \
  scripts/goal836_rtx_baseline_readiness_gate.py \
  scripts/goal860_spatial_partial_ready_gate.py \
  tests/goal860_spatial_partial_ready_gate_test.py \
  tests/goal862_spatial_rtx_collection_packet_test.py
```

```bash
PYTHONPATH=src:. python3 -m py_compile \
  scripts/goal836_rtx_baseline_readiness_gate.py \
  scripts/goal860_spatial_partial_ready_gate.py \
  tests/goal860_spatial_partial_ready_gate_test.py \
  tests/goal862_spatial_rtx_collection_packet_test.py \
  tests/goal962_next_rtx_pod_execution_packet_test.py
```

Results:

- `git diff --check`: pass.
- targeted `py_compile`: pass.

## Claim Boundary

Allowed statement:

- The compact local release-facing gate after Goal964/965 is clean.
- The accepted Goal962 packet remains ready for a future intentional RTX pod
  run.

Disallowed statement:

- Do not claim this goal ran cloud tests.
- Do not claim release authorization.
- Do not claim public RTX speedups.

## Verdict

Local compact gate verdict: PASS, pending peer review.
