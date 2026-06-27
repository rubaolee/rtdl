# V4 Goal4750 Unified RT-Core Runner Dry Run

Status: `goal4750_unified_runner_dry_run_rows_emitted_command_binding_in_progress`

This is the command-binding dry run for the final V2.14/V3.0.2/V4.0 POD matrix.
It does not execute timing and does not authorize release claims.

## Counts

- rows: `30`
- ready_for_command_binding: `30`
- blocked_until_repair: `0`

## POD

- host: `194.68.245.170`
- port: `22089`
- key: `~/.ssh/id_ed25519_rtdl_codex_current_pod`
- gpu: `NVIDIA RTX A5000`

## Blocked Rows

- None.

## Validation

- status: `passed`
- error_count: `0`

## Next

Generate required fixtures, smoke the bound commands, then run Goal4753 on the RTX POD.
