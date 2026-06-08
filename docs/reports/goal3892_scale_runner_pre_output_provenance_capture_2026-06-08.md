# Goal3892 Scale Runner Pre-Output Provenance Capture

## Purpose

Goal3890 added `runtime_environment` metadata to the current benchmark
scale-profile runner. Its A5000 dry-run showed a useful edge case:
`working_tree_clean` became `false` because the runner created its own output
directory under `docs/reports` before collecting Git status.

Goal3892 fixes that ordering. The runner now captures runtime provenance before
creating output directories or output JSON files.

## What Changed

Updated `scripts/goal3828_current_benchmark_scale_profile_runner.py`:

- call `_runtime_environment_metadata()` immediately after row selection;
- create `output_dir` after provenance is captured;
- store the pre-output metadata in `result["runtime_environment"]`.

No row command, timeout, stdout/stderr file handling, JSON parsing,
prepared-session profile attachment, or claim scanner changed.

## Boundary

This is provenance ordering only. It does not authorize release action, public
speedup wording, broad RT-core wording, true-zero-copy wording, automatic
partner/backend selection, AMD performance wording, paper-reproduction wording,
or app-specific native-engine logic.

## Validation

Updated `tests/goal3890_scale_runner_runtime_provenance_test.py` with a
regression check that writes the runner output under a new in-repo artifact path
and verifies that the newly created output path does not appear in
`runtime_environment.git_status_short`.

## A5000 Clean-Tree Dry-Run Evidence

Ran from a fresh clone on the A5000 pod without pre-creating the in-repo output
directory:

Artifact:

`docs/reports/goal3892_pre_output_provenance_a5000_dry_run/summary.json`

Result:

- `exit_code`: `0`
- `dry_run`: `true`
- selected row count: `1`
- `runtime_environment.source_commit_short`: `682533e3`
- `runtime_environment.working_tree_clean`: `true`
- `runtime_environment.git_status_short`: `[]`
- `runtime_environment.nvidia_smi`: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`

This proves the runner now captures Git provenance before creating its own
output path. If a caller pre-creates or dirties the output path before invoking
the runner, that dirtiness will still be honestly recorded.
