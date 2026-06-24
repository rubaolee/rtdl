I have read all required evidence. Rendering verdict.

---

## M22 Final Restart Review — PYTHONPATH Preflight Guard Fix

**Verdict: `authorize_m22_final_restart_after_preflight_guard_fix`**

---

### Required Statements

**1. Is `restart_20260623_055701` valid performance evidence?**

No. The attempt exited 69 before any benchmark started. The log confirms `benchmark_started: false` and `valid_performance_evidence: false`. The exit was produced by the new exit-69 child-interpreter probe failing when `import goal3828_current_benchmark_scale_profile_runner` triggered `ModuleNotFoundError: No module named 'rtdsl'` — a defect in the probe's own environment, not a suite or measurement outcome. Zero rows were scored. This attempt is not valid evidence and does not consume the one authorized valid-evidence slot.

**2. Is the `PYTHONPATH=src:.` repair sufficient and appropriately narrow?**

Yes, on both counts.

Root cause is precise: the exit-69 probe subshell at line 114–161 imported `goal3828_...` which imports `rtdsl`, but `PYTHONPATH` was not yet set when the subshell ran.

Fix is narrow: a single `export PYTHONPATH="src:."` line added at line 42, after the venv existence check (exit 65) and before all preflight stages (exits 66–69). This is the identical `PYTHONPATH` already exported by `run_cmd` at line 201. No runner logic, preflight order, benchmark commands, or gate conditions were changed.

Remote smoke verified: both trees produce the correct interpreter for `goal2626_cmd0`, `goal2626_child`, `goal3828_cmd0`, and `goal3828_child` after the fix. The probe that previously triggered `ModuleNotFoundError` now passes.

**3. Is any additional no-benchmark check required before restart?**

No. The remote smoke is already complete and passed. The exit-69 guard executes inline at run time before any benchmark reaches the dispatch loop — it cannot be skipped on the pod. No additional pre-run check is needed.

**4. Does max valid completed all-app run count remain 1?**

Yes. Two failed preflights have occurred: `_044537` (prior child-interpreter check missing at code level) and `_055701` (PYTHONPATH missing in the new probe). Neither reached benchmarks. Neither is valid evidence. Neither consumes the authorized slot. The count remains: 0 valid completed runs, 1 authorized. After this final restart completes — valid or failed — no further all-app run is authorized without renewed external review.

**5. Do release, public speedup, and broad V3-over-V2 wording remain unauthorized?**

Yes, unconditionally. These fields are not contingent on run outcomes and are not changed by a restart authorization.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```

---

### Basis

The prior consensus rule ("if the restarted run fails any preflight or protocol gate, no further restart is authorized without renewed external review") correctly required this review. That rule was written to guard against contaminated measurements or suite failures. The `_055701` failure is a defect in the new gate mechanism itself — the exit-69 probe could not import `rtdsl` because the runner had not yet exported `PYTHONPATH` at that point. The fix closes that gap with one environment export, verified on remote, with no other runner changes. The situation is structurally identical to the original restart authorization: a fail-closed gate stopped the run before any evidence was generated; the gate's own infrastructure gap is now closed; restart is safe.
