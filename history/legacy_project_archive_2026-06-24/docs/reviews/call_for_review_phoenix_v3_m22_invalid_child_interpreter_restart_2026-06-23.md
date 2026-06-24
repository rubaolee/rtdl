# Call For Review: Phoenix V3 M22 Invalid Child Interpreter Stop And Restart Decision

Date: 2026-06-23

Scope: Phoenix V3 only. No V4. No release authorization.

## Situation

M21 Claude review authorized exactly one all-app same-RT-hardware POD run under the M21 protocol, with release/public/broad-speedup authorization all false.

M22 started:

```text
run_id: phoenix_v3_m22_all_app_paired_20260623_044537
remote_run_dir: /root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m22_all_app_paired_20260623_044537
```

During monitoring, before the first required suite completed, Codex detected that the suite driver was using the project venv Python, but `goal2626_benchmark_embree_optix_baseline.py` launched benchmark app children via a hardcoded `python3`. On the POD this resolved to `/usr/bin/python3.12`, not `/root/rtdl_v3_rebuild_20260620/.venv/bin/python`.

That system Python had different NumPy and lacked CuPy/Numba:

```text
venv_exe: /root/rtdl_v3_rebuild_20260620/.venv/bin/python
venv_numpy: 2.4.6
python3_exe: /usr/bin/python3
python3_numpy: 2.1.2
python3_cupy: ModuleNotFoundError
python3_numba: ModuleNotFoundError
```

Codex stopped the run fail-closed and wrote:

```text
remote_exit_code_marker: invalid_interpreter_child_process
valid_performance_evidence: false
```

## Repair

Changed:

```text
scripts/goal2626_benchmark_embree_optix_baseline.py
scripts/phoenix_v3_serious_paired_v2x_runner.sh
tests/v3_phoenix_m21_all_app_pod_protocol_test.py
docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json
docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
docs/reports/phoenix_v3_m22_all_app_pod_run_start_2026-06-23.md
```

Patch summary:

- `goal2626._py()` now uses `PYTHON_BIN` or `sys.executable`, not hardcoded `python3`.
- `goal2636` inherits the same fix because it imports `_py` from `goal2626`.
- M22 runner now adds a child-interpreter preflight for both `current` and `v2_14`, probing `goal2626/goal2636` and `goal3828`; mismatch exits 69 before benchmarks.
- Protocol JSON/MD now records exit 69.

## Verification

Local:

```text
py -3 -m unittest tests.v3_phoenix_m21_all_app_pod_protocol_test tests.v3_phoenix_set_ab_scorecard_gate_test tests.v3_phoenix_serious_v2x_paired_analysis_test
result: 12 tests OK

protocol JSON parse: OK
runner bash -n: OK
v3_release_wording_gate.py --pretty: pass
git diff --check scoped: only Windows line-ending warning for goal2626 script
```

Remote no-benchmark smoke after syncing `goal2626` to both trees:

```text
tree=current
driver_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
cmd0=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
child_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python

tree=v2_14
driver_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
cmd0=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
child_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

Remote runner/protocol sync:

```text
remote_runner_protocol_synced_bash_n_ok
```

## Question For External Review

Does the invalid stopped attempt consume the single M21 all-app run authorization, or may Codex restart one valid all-app POD run after this fail-closed repair?

Please return exactly one verdict:

- `authorize_m22_restart_after_invalid_preflight_stop`
- `block_restart_p0`
- `block_restart_p1`

Required statements:

- Whether the first attempt is valid performance evidence.
- Whether the child-interpreter repair is sufficient for one restart.
- Whether any additional no-benchmark check is required before restart.
- Whether release/public/broad V3-over-V2 speedup wording remains unauthorized.
- Whether the restarted run, if authorized, still has max valid completed all-app run count = 1.

Non-authorization requested:

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```
