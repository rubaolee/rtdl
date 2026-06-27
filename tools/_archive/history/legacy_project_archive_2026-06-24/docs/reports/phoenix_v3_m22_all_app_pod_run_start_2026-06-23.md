# Phoenix V3 M22 All-App POD Run Start

Status: `m22_first_attempt_invalid_stopped_child_interpreter_repaired_pending_2ai_consensus`

This was the first attempt at the single all-app POD run authorized by M21 Claude review and Codex+Claude consensus. It is not a release run, and it is not valid M21/M22 evidence because a child interpreter leak was detected before the first suite completed.

```text
run_id: phoenix_v3_m22_all_app_paired_20260623_044537
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_20260623_044537
remote_pid: 904033
launcher_log: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_20260623_044537/launcher.log
main_log: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_20260623_044537/main.log
status_tsv: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_20260623_044537/status.tsv
```

## Authorization Boundary

```text
one_all_app_pod_run_authorized: true
max_run_count: 1
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```

## Preflight Result

The patched runner passed startup gates before entering benchmark suites:

```text
python_preflight_expected=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
python_preflight_actual=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
gpu_preflight_name=NVIDIA RTX 4000 Ada Generation
gpu_preflight_driver=550.127.05
gpu_preflight_compute_capability=8.9
required_import_preflight_cupy=14.1.1
required_import_preflight_numba=0.65.1
```

First suite entered:

```text
v2_14:goal2626_large
```

## Invalid Stop

During monitoring, the suite driver was confirmed to run under the project venv, but benchmark app children launched by `goal2626_benchmark_embree_optix_baseline.py` resolved `python3` to `/usr/bin/python3.12` instead of `/root/rtdl_v3_rebuild_20260620/.venv/bin/python`.

The system interpreter had different NumPy and lacked CuPy/Numba:

```text
venv_exe: /root/rtdl_v3_rebuild_20260620/.venv/bin/python
venv_numpy: 2.4.6
python3_exe: /usr/bin/python3
python3_numpy: 2.1.2
python3_cupy: ModuleNotFoundError
python3_numba: ModuleNotFoundError
```

Fail-closed action:

```text
remote_exit_code_marker: invalid_interpreter_child_process
stopped_before_first_suite_completed: true
valid_performance_evidence: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

Repair applied:

```text
scripts/goal2626_benchmark_embree_optix_baseline.py: _py() now uses PYTHON_BIN or sys.executable
scripts/phoenix_v3_serious_paired_v2x_runner.sh: adds child interpreter preflight, exit 69 on mismatch
remote current and v2_14 trees: goal2626 harness synced
remote no-benchmark smoke: current and v2_14 child_exe both resolve to /root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

2-AI restart consensus:

```text
call_for_review: docs/reviews/call_for_review_phoenix_v3_m22_invalid_child_interpreter_restart_2026-06-23.md
claude_review: docs/reviews/claude_phoenix_v3_m22_invalid_child_interpreter_restart_review_2026-06-23.raw.md
consensus: docs/reviews/codex_claude_phoenix_v3_m22_invalid_child_interpreter_restart_2ai_consensus_2026-06-23.md
verdict: authorize_m22_restart_after_invalid_preflight_stop
max_valid_completed_all_app_run_count_after_restart: 1
```

## Restart Attempt Blocked By New Preflight

Restart attempt:

```text
run_id: phoenix_v3_m22_all_app_paired_restart_20260623_055701
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_restart_20260623_055701
exit_code: 69
valid_performance_evidence: false
benchmark_started: false
```

The new child-interpreter guard correctly blocked before any benchmark, but the first version of the guard missed the runner's normal `PYTHONPATH=src:.` setup. The `goal3828` child probe failed to import `rtdsl`.

Repair applied after this preflight block:

```text
scripts/phoenix_v3_serious_paired_v2x_runner.sh: export PYTHONPATH=src:. before interpreter/import/child preflight
local runner bash -n: OK
local M21 protocol tests: OK
remote runner bash -n: OK
remote no-benchmark child smoke current/v2_14: goal2626 and goal3828 child_exe both resolve to project venv
```

No further all-app restart is authorized until renewed external review, per the previous Codex+Claude consensus.

Renewed external review:

```text
call_for_review: docs/reviews/call_for_review_phoenix_v3_m22_restart_after_exit69_pythonpath_fix_2026-06-23.md
claude_review: docs/reviews/claude_phoenix_v3_m22_restart_after_exit69_pythonpath_fix_review_2026-06-23.raw.md
consensus: docs/reviews/codex_claude_phoenix_v3_m22_final_restart_after_exit69_pythonpath_fix_2ai_consensus_2026-06-23.md
verdict: authorize_m22_final_restart_after_preflight_guard_fix
valid_completed_all_app_runs_before_final_restart: 0
authorized_valid_all_app_runs_remaining: 1
```

Final restarted run:

```text
run_id: phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315
remote_pid: 907917
launcher_log: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/launcher.log
main_log: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/main.log
status_tsv: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_finalrestart_20260623_060315/status.tsv
```

## Goal-Level Decision Audit

1. Was I foolish?

Yes, the first attempt still missed an inner child-process interpreter leak.

2. If yes, what actions made the decision foolish?

I verified the suite driver interpreter but did not initially prove that benchmark app children inherited the same interpreter.

3. Was there another path?

Yes: add a harmless child-interpreter probe to the runner before allowing any benchmark suite to start.

4. Can I now try a different path?

Yes. The harness now has both code-level repair and runner-level exit-69 preflight, and the next restart requires 2-AI consensus because the first attempt was invalidated.
