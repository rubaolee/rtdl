# Call For Review: Phoenix V3 M22 Restart After Exit-69 PYTHONPATH Fix

Date: 2026-06-23

Scope: Phoenix V3 only. No V4. No release authorization.

## Background

Claude previously returned:

```text
docs/reviews/claude_phoenix_v3_m22_invalid_child_interpreter_restart_review_2026-06-23.raw.md
verdict: authorize_m22_restart_after_invalid_preflight_stop
```

Codex+Claude consensus then allowed one restart, but explicitly said no further all-app restart is authorized if the restarted run fails a preflight or protocol gate without renewed external review:

```text
docs/reviews/codex_claude_phoenix_v3_m22_invalid_child_interpreter_restart_2ai_consensus_2026-06-23.md
```

## What Happened

The authorized restart attempted:

```text
run_id: phoenix_v3_m22_all_app_paired_restart_20260623_055701
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_restart_20260623_055701
exit_code: 69
valid_performance_evidence: false
benchmark_started: false
```

The new exit-69 child-interpreter guard blocked before any benchmark. The guard itself lacked the runner's normal `PYTHONPATH=src:.`, so its `goal3828` probe could not import `rtdsl`.

Relevant log:

```text
python_preflight_expected=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
python_preflight_actual=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
gpu_preflight_name=NVIDIA RTX 4000 Ada Generation
gpu_preflight_driver=550.127.05
gpu_preflight_compute_capability=8.9
required_import_preflight_cupy=14.1.1
required_import_preflight_numba=0.65.1
ModuleNotFoundError: No module named 'rtdsl'
reason=Benchmark child interpreter preflight failed.
tree=current
required_child_interpreter=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
rc=1
```

## Repair

Changed:

```text
scripts/phoenix_v3_serious_paired_v2x_runner.sh
```

Patch:

```text
export PYTHONPATH=src:.
```

This is placed before interpreter/import/child preflight, matching the actual suite environment already used by `run_cmd`.

## Verification

Local:

```text
runner bash -n: OK
py -3 -m unittest tests.v3_phoenix_m21_all_app_pod_protocol_test: 8 tests OK
git diff --check scoped: OK
```

Remote:

```text
remote runner bash -n: OK

tree=current
driver_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal2626_cmd0=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal2626_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal3828_cmd0=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal3828_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python

tree=v2_14
driver_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal2626_cmd0=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal2626_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal3828_cmd0=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
goal3828_child=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

## Question

May Codex start one final M22 all-app run after this preflight-only exit-69 guard repair?

Please return exactly one verdict:

- `authorize_m22_final_restart_after_preflight_guard_fix`
- `block_restart_p0`
- `block_restart_p1`

Required statements:

- Whether the `restart_20260623_055701` attempt is valid performance evidence.
- Whether the `PYTHONPATH=src:.` repair is sufficient and appropriately narrow.
- Whether any additional no-benchmark check is required before restart.
- Whether max valid completed all-app run count remains 1.
- Whether release/public/broad V3-over-V2 speedup wording remains unauthorized.

Non-authorization must remain:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```
