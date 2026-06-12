# Goal4332 RayJoin Public-CDB Fixture Runner Option

Date: 2026-06-11

## Purpose

Goal4329 proved the current pod stack can run the full 10-row scale packet, but
the first full run failed `9/10` because a fresh pod did not yet contain the
RayJoin public-CDB fixture.

The fix is not to hide a download behind normal execution. The fix is an
explicit runner option.

## Change

`scripts/goal3828_current_benchmark_scale_profile_runner.py` now accepts:

- `--materialize-rayjoin-public-cdb`
- `--rayjoin-public-cdb-dir PATH`

When the selected rows include
`spatial_rayjoin_public_cdb_representative_mixed_route_scale_default`, the
runner records a `rayjoin_public_cdb_fixture` block in its output. With
`--materialize-rayjoin-public-cdb`, it uses the existing Goal2159 public-CDB
downloader/materializer to prepare:

- `br_county_start256_count512.cdb`
- `br_soil_start256_count512.cdb`

Without the explicit materialize flag, the runner only records whether the
fixture is already provided. If the fixture is missing and the user does not opt
into materialization, the RayJoin row can still fail with a clear missing-data
error. This keeps network/data movement visible.

## App-Agnostic Boundary

This is benchmark-runner orchestration only. It does not add RayJoin logic to
the RTDL engine, native backends, primitive catalog, or partner protocol.

## Verification

Added `tests/goal4332_rayjoin_fixture_materialization_option_test.py` covering:

- dry-run materialization planning without network download;
- provided-fixture detection using temporary fake CDB files;
- not-needed status when no RayJoin row is selected;
- report boundary wording;
- pod-validation bundle pass-through for the explicit fixture flag.

Focused validation:

```text
PYTHONPATH=src:. python -m unittest \
  tests.goal4332_rayjoin_fixture_materialization_option_test \
  tests.goal4329_current_pod_validation_test \
  tests.goal4311_current_scale_timing_floor_guard_test
```

RTX pod validation:

- Artifact:
  `docs/reports/goal4329_current_pod_validation/goal4332_runner_option/rayjoin_materialized_summary.json`
- Result: `all_pass: true`, `json_pass_count: 1`
- Fixture status: `materialized`

Follow-up wiring:

- `docs/learn/benchmark_evidence_index.md` now shows the current scale-profile
  command with `--materialize-rayjoin-public-cdb`.
- `docs/audit/runbooks/v2_10_pod_validation_bundle.md` and
  `docs/audit/runbooks/rtx_cloud_single_session_runbook.md` now show the same
  explicit flag for current hardware packet runs.
- `scripts/rtdl_v2_10_pod_validation_bundle.py` accepts and passes through
  `--materialize-rayjoin-public-cdb` and `--rayjoin-public-cdb-dir`; the bundle
  records that the download is not hidden by the bundle.
- `scripts/rtdl_remote_pod_validation_driver.py` and its runbook expose the
  same explicit materialization flag for one-command SSH pod sessions.
- The pod-validation bundle now parses the child command's declared JSON
  artifact when stdout contains progress lines, so claim-flag checks are applied
  to `scale_profile_summary.json` rather than skipped because stdout is not pure
  JSON.
- Fixed bundle pass-through artifact:
  `docs/reports/goal4329_current_pod_validation/goal4332_bundle_pass_through_validation_fixed/bundle_summary.json`
  reports `status: pass`, hardware scale-profile step `json_source: artifact`,
  and the underlying scale-profile summary `all_pass: true`.

## Boundary

Goal4332 does not authorize release action, public speedup wording, broad
RT-core wording, paper-reproduction wording, true-zero-copy wording, automatic
partner selection, or app-specific native-engine logic.
