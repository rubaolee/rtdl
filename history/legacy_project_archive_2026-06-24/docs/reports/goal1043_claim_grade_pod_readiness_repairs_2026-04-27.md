# Goal1043 Claim-Grade Pod Readiness Repairs

Date: 2026-04-27

## Scope

Goal1043 addresses the two concrete blockers identified by Goal1040/Goal1041 before another RTX pod run:

- Group summaries lacked source commit traceability when the pod was staged with `rsync` instead of a git checkout.
- Fixed-radius Group B cloud commands used `--skip-validation`, which blocked public-claim-grade correctness evidence.

## Changes

### Source Commit Injection

Updated `scripts/goal761_rtx_cloud_run_all.py`:

- `_source_commit()` now first checks `RTDL_SOURCE_COMMIT`.
- It still falls back to `git rev-parse HEAD`.
- It then falls back to `.rtdl_source_commit`.

Updated `docs/reports/goal1038_next_rtx_ready_app_rerun_packet_2026-04-26.md`:

- Exports `RTDL_SOURCE_COMMIT` from `.rtdl_source_commit` or git.
- Passes `RTDL_SOURCE_COMMIT` into the Group B and Group D commands.

### Validation-On Fixed-Radius Group B

Updated `scripts/goal759_rtx_cloud_benchmark_manifest.py`:

- Removed `--skip-validation` from `prepared_fixed_radius_density_summary`.
- Removed `--skip-validation` from `prepared_fixed_radius_core_flags`.

This makes the next Group B pod run collect in-band oracle counts rather than null oracle fields.

## Validation

Focused tests:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests/goal759_rtx_cloud_benchmark_manifest_test.py \
  tests/goal761_rtx_cloud_run_all_test.py
```

Result: `21 tests OK`.

Dry-run evidence:

```bash
PYTHONPATH=src:. RTDL_SOURCE_COMMIT=test-source-commit \
python3 scripts/goal761_rtx_cloud_run_all.py \
  --dry-run \
  --only prepared_fixed_radius_density_summary \
  --only prepared_fixed_radius_core_flags \
  --output-json /tmp/goal1043_group_b_dry_run.json
```

Observed:

- `source_commit: test-source-commit`
- fixed-radius command does not include `--skip-validation`
- `entry_count: 2`
- `unique_command_count: 1`
- `status: ok`

## Boundary

This is local claim-grade readiness plumbing only. It does not run cloud benchmarks, authorize public speedup claims, authorize release, or prove RTX correctness by itself.
