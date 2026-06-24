# Codex + Claude Consensus: Phoenix V3 M22 Invalid Child Interpreter Stop And Restart

Date: 2026-06-23

Scope: Phoenix V3 M22 all-app same-RT-hardware V2.14 vs Phoenix V3 POD run.

## Verdict

Consensus verdict: `authorize_m22_restart_after_invalid_preflight_stop`

The stopped `phoenix_v3_m22_all_app_paired_20260623_044537` attempt is not valid performance evidence and does not consume the single authorized valid all-app run slot, because it was stopped fail-closed before the first required suite completed.

The restarted run remains:

```text
max_valid_completed_all_app_run_count: 1
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```

## External Review

Claude review:

```text
path: docs/reviews/claude_phoenix_v3_m22_invalid_child_interpreter_restart_review_2026-06-23.raw.md
verdict: authorize_m22_restart_after_invalid_preflight_stop
```

Claude's controlling findings:

- First attempt is not valid performance evidence.
- Child-interpreter repair is sufficient for one restart.
- No additional no-benchmark check is required before restart because the runner now performs exit-69 child-interpreter preflight before benchmarks.
- Release/public/broad V3-over-V2 wording remains unauthorized.
- The restarted run is the single authorized valid attempt; no further all-app run is authorized after it without renewed external review.

## Codex Acceptance

Codex accepts Claude's verdict.

The repair is narrow and evidence-scoped:

- `scripts/goal2626_benchmark_embree_optix_baseline.py`: `_py()` uses `PYTHON_BIN` or `sys.executable`.
- `scripts/phoenix_v3_serious_paired_v2x_runner.sh`: child-interpreter preflight probes both `current` and `v2_14`; mismatch exits 69 before benchmarks.
- `goal2636` inherits the `_py()` repair through its import.
- `goal3828` is checked through its existing `sys.executable` row-command substitution.

Verified before restart:

```text
local tests: 12 OK
protocol JSON parse: OK
runner bash -n: OK locally and remotely
v3_release_wording_gate.py --pretty: pass
remote child smoke current: child_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
remote child smoke v2_14: child_exe=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
remote residual benchmark processes from invalid attempt: none
```

## Restart Rule

Codex may start one new M22 all-app run with a new run id.

The restart command must still set:

```text
PHOENIX_V3_ALLOW_ALL_APP_RUN=1
PHOENIX_V3_RUNTIME_TRUNK_EXECUTED=1
BASE=/root/rtdl_v3_rebuild_20260620
PYTHON_BIN=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

If the restarted run fails any preflight or protocol gate, it must be recorded as failed/invalid; no further all-app restart is authorized without renewed external review.

## Goal-Level Decision Audit

1. Was I foolish?

Yes. The first M22 attempt missed an inner child-interpreter leak after checking only the suite driver interpreter.

2. If yes, what actions made the decision foolish?

The foolish action was treating suite-level `sys.executable` as sufficient proof that every benchmark subprocess used the same venv.

3. Was there another path?

Yes. A harmless child-process probe should have been part of the runner before the first all-app attempt.

4. Can I now try a different path?

Yes. The runner now has a fail-closed exit-69 child-interpreter probe, the repair is synced to both trees, and restart is backed by Claude + Codex consensus.
