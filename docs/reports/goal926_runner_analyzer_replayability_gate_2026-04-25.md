# Goal 926: Runner/Analyzer Replayability Gate

Date: 2026-04-25

## Scope

Lock the current pre-cloud runner and post-cloud analyzer contract for the
post-Goal923 app board.

This goal prevents a future paid pod session from producing artifacts that the
local analyzer cannot replay. It does not run cloud, does not benchmark, and
does not authorize RTX speedup claims.

## Changes

- Added a Goal762 regression test that generates a full `--include-deferred`
  Goal761 dry-run summary and verifies Goal762 can analyze all rows.
- Updated the Goal761 selective deferred test to use `graph_analytics`, which
  is still deferred after Goal923.
- Added a Goal761 regression test proving `service_coverage_gaps` is now an
  active entry even when `--include-deferred` is enabled.

## Local Evidence

Generated dry-run analyzer probe:

```bash
PYTHONPATH=src:. python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --include-deferred \
  --output-json build/goal926_full_include_deferred_dry_run.json

PYTHONPATH=src:. python3 scripts/goal762_rtx_cloud_artifact_report.py \
  --summary-json build/goal926_full_include_deferred_dry_run.json \
  --output-json build/goal926_full_include_deferred_artifact_probe.json \
  --output-md build/goal926_full_include_deferred_artifact_probe.md
```

Result:

- runner status: `ok`
- analyzer status: `ok`
- entry count: `17`
- failure count: `0`
- unique app count: `16`
- all rows have `baseline_review_contract_status: ok`

## Verification

Focused verification:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal762_rtx_cloud_artifact_report_test \
  tests.goal761_rtx_cloud_run_all_test \
  tests.goal759_rtx_cloud_benchmark_manifest_test \
  tests.goal901_pre_cloud_app_closure_gate_test \
  tests.goal824_pre_cloud_rtx_readiness_gate_test
```

Result: 38 tests OK.

Additional checks:

- `py_compile` for Goal759/761/762 scripts: OK.
- `git diff --check` for edited tests: OK.

## Boundary

The analyzer result is from a dry run, so artifact statuses are
`dry_run_not_expected`. Real RTX evidence still requires a cloud run, copied
artifacts, non-dry-run Goal762 analysis, baseline review, and independent
claim review.
